import qiime2
import tempfile
import xarray as xr
import pandas as pd
import numpy as np
import subprocess
import os
import re


def _alr2clr(x):
    y = np.vstack((np.ones(x.shape[1]), x))
    return y - y.mean(axis=0)


def run_commands(cmds, verbose=True):
    if verbose:
        print("Running external command line application(s). This may print "
              "messages to stdout and/or stderr.")
        print("The command(s) being run are below. These commands cannot "
              "be manually re-run as they will depend on temporary files that "
              "no longer exist.")
    for cmd in cmds:
        if verbose:
            print("\nCommand:", end=' ')
            print(" ".join(cmd), end='\n\n')
        proc = subprocess.run(cmd, check=True)


def basset(table : pd.DataFrame,
           time : qiime2.NumericMetadataColumn,
           subjects : qiime2.CategoricalMetadataColumn,
           host : str,
           monte_carlo_samples: int=1000) -> xr.DataArray:

    time = time.to_series()
    subjects = subjects.to_series()
    metadata = pd.DataFrame({'time': time, 'subject': subjects})
    metadata = metadata.loc[metadata.subject == host]
    ids = list(set(table.index) & set(metadata.index))
    table = table.loc[ids]
    metadata = metadata.loc[ids]
    metadata = metadata['time']
    table = table.loc[:, ((table>0).sum(axis=0) > 0)]  # filter out taxa
    print(table.shape, metadata.shape)
    with tempfile.TemporaryDirectory() as temp_dir_name:
        biom_fp = os.path.join(temp_dir_name, 'input.tsv.biom')
        map_fp = os.path.join(temp_dir_name, 'input.map.txt')
        summary_fp = os.path.join(temp_dir_name, 'output.summary.txt')

        # Need to manually specify header=True for Series (i.e. "meta"). It's
        # already the default for DataFrames (i.e. "table"), but we manually
        # specify it here anyway to alleviate any potential confusion.
        table.to_csv(biom_fp, sep='\t', header=True)
        metadata.to_csv(map_fp, sep='\t', header=True)

        cmd = ['fido-timeseries.R', biom_fp, map_fp, 'time',
               monte_carlo_samples, summary_fp]
        cmd = list(map(str, cmd))

        try:
            run_commands([cmd])
        except subprocess.CalledProcessError as e:
            raise Exception("An error was encountered while running fido"
                            " in R (return code %d), please inspect stdout"
                            " and stderr to learn more." % e.returncode)

        lam = pd.read_feather(summary_fp)
        # convert to clr coordinates for the sake of sanity
        pattern = re.compile(r'X(\d+).(\d+)')
        cols = list(map(lambda x: pattern.findall(x)[0], lam.columns[1:]))
        lookup = pd.DataFrame(np.array(cols), index=lam.columns[1:],
                              columns=['sample_num', 'mc_sample'])
        lam = lam.set_index('Unnamed: 0').T
        lam = pd.merge(lam, lookup, left_index=True, right_index=True)
        lam['sample_num'] = lam['sample_num'].astype(np.int64)
        lam['mc_sample'] = lam['mc_sample'].astype(np.int64)
        lam_tensor = pd.melt(lam, id_vars=['sample_num', 'mc_sample'],
                             var_name='featureid')
        lam_tensor = lam_tensor.set_index(['sample_num', 'mc_sample', 'featureid'])
        xdata = lam_tensor.to_xarray()

        # rename taxa grrr
        pattern = re.compile(r'log\((\S+)/(\S+)\)')
        f = lambda x: pattern.findall(x)[0]
        ftaxa = list(map(f, list(np.array(xdata.coords['featureid']))))
        t, r = zip(*ftaxa)
        xdata['coords']['featureid'] = np.array(list(t))
        # Convert alr coordinates to clr coordinates across entire tensor
        zdata = xr.DataArray(
            np.zeros((1, 2000, 43)),
            dims=['featureid', 'mc_sample', 'sample_num'],
            coords=dict(
                featureid=np.array(r[0]),
                mc_sample=np.array(xdata.coords['mc_sample']),
                sample_num=np.array(xdata.coords['sample_num'])
            )
        )
        zdata = zdata.to_dataset(name='value')
        zdata['name'] = 'data'
        xdata['name'] = 'data'
        posterior = xr.concat((zdata, xdata), dim='featureid')
        return posterior
