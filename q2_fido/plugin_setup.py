import importlib
import qiime2.plugin
import qiime2.sdk
from qiime2.plugin import (Str, Properties, Int, Float,  Metadata, Bool,
                           MetadataColumn, Categorical, Continuous)

from q2_fido import __version__
from q2_differential._type import FeatureTensor
from q2_differential._format import FeatureTensorNetCDFFormat, FeatureTensorNetCDFDirFmt
from q2_fido._method import basset


plugin = qiime2.plugin.Plugin(
    name='basset',
    version=__version__,
    website="https://github.com/mortonjt/q2-fido",
    citations=[],
    short_description=('Plugin for high-dimensional time series analysis '
                       'via count-based models.'),
    description=('This is a QIIME 2 plugin supporting time series models on '
                 'feature tables and metadata.'),
    package='q2-differential')

plugin.methods.register_function(
    function=dirichlet_multinomial,
    inputs={'table': FeatureTable[Frequency]},
    parameters={
        'subjects': MetadataColumn[Categorical],
        'host' : Str,
        'time': MetadataColumn[Continuous],
        'monte_carlo_samples': Int
    },
    outputs=[
        ('posterior', FeatureTensor)
    ],
    input_descriptions={
        "table": "Input table of counts.",
    },
    output_descriptions={
        'posterior': ('Output posterior time series learned from '
                      'Matrix t-distribution.'),
    },
    parameter_descriptions={
        'subjects': ('Specifies host subject ids.'),
        'host': ('Host subject id of interest'),
        'time': (
            'Specifies time data.'
        ),
        'monte_carlo_samples': (
            'Number of monte carlo samples to draw from '
            'posterior distribution.'
        ),

    },
    name='Basset',
    description=("Fits a Matrix t-distribution on a single trajectory."),
    citations=[]
)
