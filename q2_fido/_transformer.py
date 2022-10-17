import biom
import skbio
import qiime2
import xarray as xr

from . import FeatureTensorNetCDFFormat


@plugin.register_transformer
def _225(ff: FeatureTensorNetCDFFormat) -> az.InferenceData:
    return xr.open_dataset(str(ff))


@plugin.register_transformer
def _226(obj: xr.Dataset) -> FeatureTensorNetCDFFormat:
    ff = FeatureTensorNetCDFFormat()
    obj.to_netcdf(str(ff))
    return ff
