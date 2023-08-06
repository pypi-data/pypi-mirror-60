
from ._obj_from_dict import ObjFromDict

from .request_cofbox_instruments import RequestCofboxInstruments
from .response_cofbox_instruments import ResponseCofboxInstruments

from .request_cofbox_instruments_details import RequestCofboxInstrumentsDetails
from .response_cofbox_instruments_details import ResponseCofboxInstrumentsDetails

from .request_cofbox_analysis_types import RequestCofboxAnalysisTypes
from .response_cofbox_analysis_types import ResponseCofboxAnalysisTypes

from .request_cofbox_analysis import RequestCofboxAnalysis
from .response_cofbox_analysis import ResponseCofboxAnalysis


dic_endpoint = {
    'v1_instruments': {
        'request': RequestCofboxInstruments,
        'response': ResponseCofboxInstruments,
    },
    'v1_instruments_details': {
        'request': RequestCofboxInstrumentsDetails,
        'response': ResponseCofboxInstrumentsDetails,
    },
    'v1_analysis_types': {
        'request': RequestCofboxAnalysisTypes,
        'response': ResponseCofboxAnalysisTypes,
    },
    'v1_analysis': {
        'request': RequestCofboxAnalysis,
        'response': ResponseCofboxAnalysis,
    },
    # to add new endpoint here after creating the corresponding
    # Request Response and optionally Slice objects
}

endpoint = ObjFromDict(dic_endpoint)
