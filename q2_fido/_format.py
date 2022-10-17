import qiime2.plugin.model as model
from qiime2.plugin import ValidationError
import qiime2
import xarray as xr


class FeatureTensorNetCDFFormat(model.BinaryFileFormat):

    def sniff(self):
        try:
            xr.open_dataset(str(self))
            return True
        except Exception:
            return False


FeatureTensorDirectoryFormat = model.SingleFileDirectoryFormat(
    'FeatureTensorDirectoryFormat', 'monte-carlo-samples.nc',
    FeatureTensorNetCDFFormat)
