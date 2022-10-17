import importlib
import qiime2.plugin
import qiime2.sdk
from qiime2.plugin import (Str, Properties, Int, Float,  Metadata, Bool,
                           MetadataColumn, Categorical, Numeric)
from q2_types.feature_table import FeatureTable, Frequency
from q2_types.distance_matrix import DistanceMatrix

from q2_fido import __version__
from q2_fido._type import FeatureTensor
from q2_fido._format import FeatureTensorNetCDFFormat, FeatureTensorNetCDFDirFmt
from q2_fido._method import basset, dtw


plugin = qiime2.plugin.Plugin(
    name='fido',
    version=__version__,
    website="https://github.com/mortonjt/q2-fido",
    citations=[],
    short_description=('Plugin for high-dimensional time series analysis '
                       'via count-based models.'),
    description=('This is a QIIME 2 plugin supporting time series models on '
                 'feature tables and metadata.'),
    package='q2-fido')

plugin.methods.register_function(
    function=basset,
    inputs={'table': FeatureTable[Frequency]},
    parameters={
        'subjects': MetadataColumn[Categorical],
        'host' : Str,
        'time': MetadataColumn[Numeric],
        'min_samples': Int,
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
        'min_samples' : (
            'Minimum number of samples a microbe '
            'has to be present in.'),
        'monte_carlo_samples': (
            'Number of monte carlo samples to draw from '
            'posterior distribution.'
        ),

    },
    name='Basset',
    description=("Fits a Matrix t-distribution on a single trajectory."),
    citations=[]
)

plugin.methods.register_function(
    function=dtw,
    inputs={'table': FeatureTable[Frequency]},
    parameters={
        'filepaths': MetadataColumn[Categorical],
        'subjects': MetadataColumn[Categorical],
        'time': MetadataColumn[Numeric],
    },
    outputs=[
        ('distance_matrix', DistanceMatrix)
    ],
    input_descriptions={
        "table": "Input table of counts.",
    },
    output_descriptions={
        'distance_matrix': ('Pairwise distances between subjects.'),
    },
    parameter_descriptions={
        'filepaths': ('Specifies location of posterior estimates.'),
        'subjects': ('Specifies host subject ids.'),
        'time': ('Specifies time data.'),
    },
    name='Dynamic Time Warping',
    description=("Fits a Matrix t-distribution on a single trajectory."),
    citations=[]
)

plugin.register_semantic_type_to_format(
    FeatureTensor, FeatureTensorNetCDFDirFmt)
