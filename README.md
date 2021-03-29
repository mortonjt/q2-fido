# q2-fido
qiime2 plugin for Fido for high dimensional compositional time series analysis

# Installation
```
conda install fido r-dplyr r-tidybayes r-tidyr -c mortonjt -c r
conda install -c conda-forge --strict-channel-priority r-arrow feather-format
pip install git+git@github.com:mortonjt/q2-fido.git
```

# Getting started
See `qiime fido basset --help` for more information.

An example run may look as follows.  See the `examples/alm` for relevant files
```
qiime fido basset --i-table feature-table.qza --m-time-file fecal-metadata.txt --m-time-column collection_day --m-subjects-file fecal-metadata.txt --m-subjects-column host_subject_id --p-host DonorA --p-monte-carlo-samples 1000 --output-dir DonorA --verbose
```
