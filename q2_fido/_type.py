
from qiime2.plugin import SemanticType
from ..plugin_setup import plugin
from . import FeatureTensorNetCDFDirFmt


FeatureTensor = SemanticType('FeatureTensor')


plugin.register_semantic_types(FeatureTensor)
plugin.register_semantic_type_to_format(
    FeatureTensor, FeatureTensorNetCDFDirFmt)
