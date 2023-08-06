
import pandas as pd

from IPython.display import Markdown
from copy import deepcopy as copy

from ._util import Util


class ResponseCofboxInstrumentsDetails:
    """
    """

    def __init__(self,
                 raw_data=None,
                 dic_req=None):
        """
        """
        msg1 = 'Error: raw_data returned by API must be a dict - Run call_api() again with debug=True'
        msg2 = 'Error: "instruments" must be a key of the dict - Run call_api() again with debug=True'
        msg3 = 'Error: raw_data["instruments"] must be a list - Run call_api() again with debug=True'

        assert isinstance(raw_data, dict), msg1
        assert 'instruments' in raw_data, msg2
        assert isinstance(raw_data['instruments'], list), msg3

        self.dic_req = dic_req
        self.raw_data = raw_data['instruments']
        self.li_res = self._build_li_res()

    def _build_li_res(self):
        """
        """
        dic = self.raw_data
        return dic

    def save(self,
             folder_save='dump',
             name=None,
             tagged=True):
        """
        """
        if name is None:
            name = 'SG_COFBOX_Instruments_Details'

        Util.save_as_json(self.li_res,
                          folder_save,
                          name=name,
                          tagged=tagged)

    def _repr_html_(self):
        """
        """
        return str(self.li_res)

    def info(self):
        """
        """
        md = """
A ResponseCofboxInstrumentsDetails object has the properties:
+ `dic_req`: request data (dict)
+ `li_res`: response data (list)

+ `raw_data`: raw data in response under key 'roll' (dictionary)

and the methods:
+ `save()` to save the data as `.json` files
        """
        return Markdown(md)
