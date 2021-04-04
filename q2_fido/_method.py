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
           monte_carlo_samples: int=2000) -> xr.Dataset:

    time = time.to_series()
    subjects = subjects.to_series()
    metadata = pd.DataFrame({'time': time, 'subject': subjects})
    metadata = metadata.loc[metadata.subject == host]
    ids = list(set(table.index) & set(metadata.index))
    table = table.loc[ids]
    metadata = metadata.loc[ids]
    metadata = metadata['time'] - metadata['time'].min()
    table = table.loc[:, ((table>0).sum(axis=0) > 3)]  # filter out taxa in less than 3 samples
    with tempfile.TemporaryDirectory() as temp_dir_name:
        # temp_dir_name = '.'
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
        # convert to tensor for the sake of sanity
        lam = lam.set_index('featureid').T
        pattern = re.compile(r'(\d+).(\d+)')
        cols = list(map(lambda x: pattern.findall(x)[0], lam.index))
        lookup = pd.DataFrame(np.array(cols), index=lam.index,
                              columns=['sampleid', 'mc_sample'])
        lam = pd.merge(lam, lookup, left_index=True, right_index=True)
        lam['sampleid'] = lam['sampleid'].astype(np.int64)
        lam['mc_sample'] = lam['mc_sample'].astype(np.int64)
        lam_tensor = pd.melt(lam, id_vars=['sampleid', 'mc_sample'],
                             var_name='featureid')
        sampleids = lam_tensor['sampleid'].apply(
            lambda i: metadata.index[int(i) - 1])
        lam_tensor['sampleid'] = sampleids
        lam_tensor = lam_tensor.set_index(['sampleid', 'mc_sample', 'featureid'])
        xdata = lam_tensor.to_xarray()
        if len(xdata.coords['mc_sample']) != monte_carlo_samples:
            raise ValueError('Only MAP estimate is returned, '
                             'the Hessian likely failed.')

        # rename taxa grrr
        pattern = re.compile(r'log\((\S+)/(\S+)\)')
        f = lambda x: pattern.findall(x)[0]
        ftaxa = list(map(f, list(np.array(xdata.coords['featureid']))))
        t, r = zip(*ftaxa)
        xdata['featureid'] = np.array(list(t))
        # Convert alr coordinates to clr coordinates across entire tensor
        n_samples = len(metadata)
        zdata = xr.DataArray(
            np.zeros((1, monte_carlo_samples, n_samples)),
            dims=['featureid', 'mc_sample', 'sampleid'],
            coords=dict(
                featureid=np.array([r[0]]),
                mc_sample=np.array(xdata.coords['mc_sample']),
                sampleid=np.array(xdata.coords['sampleid'])
            )
        )
        zdata = zdata.to_dataset(name='value')
        zdata['name'] = 'data'
        xdata['name'] = 'data'
        posterior = xr.concat((zdata, xdata), dim='featureid')
        return posterior
