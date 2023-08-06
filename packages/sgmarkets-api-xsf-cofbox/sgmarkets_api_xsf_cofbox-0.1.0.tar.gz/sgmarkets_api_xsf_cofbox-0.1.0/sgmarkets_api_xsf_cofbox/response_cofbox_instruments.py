
import pandas as pd

from IPython.display import Markdown
from copy import deepcopy as copy

from sgmarkets_api_auth.util import save_result


class ResponseCofboxInstruments:
    """
    TBU
    """

    def __init__(self,
                 raw_data=None,
                 dic_req=None):
        """
        """
        msg1 = 'Error: data returned by API must be a dict - Run call_api() again with debug=True'
        msg2 = 'Error: "instruments" must be a key of the dict - Run call_api() again with debug=True'
        msg3 = 'Error: data["instruments"] must be a list - Run call_api() again with debug=True'

        assert isinstance(raw_data, dict), msg1
        assert 'instruments' in raw_data, msg2
        assert isinstance(raw_data['instruments'], list), msg3

        self.dic_req = dic_req
        self.raw_data = raw_data['instruments']
        self.df_res = self._build_df_res()

    def _build_df_res(self):
        """
        """
        data = self.raw_data

        df = pd.DataFrame(data)
        df = df[['instrumentCode',
                 'instrumentLabel',
                 'currency',
                 'referenceRate',
                 'underlyingType',
                 'underlyingCode',
                 'underlyingLabel']]
        return df

    def save(self,
             folder_save='dump',
             name=None,
             tagged=True,
             excel=False):
        """ 
        """
        if name is None:
            name = 'SG_COFBOX_Instruments'

        save_result(self.df_res,
                    folder_save,
                    name=name,
                    tagged=tagged,
                    excel=excel)

    def _repr_html_(self):
        """
        """
        return self.df_res.to_html()

    def info(self):
        """
        """
        md = """
A ResponseCofboxInstruments object has the properties:
+ `dic_req`: request data (dict)
+ `df_res`: response data (dataframe)

+ `raw_data`: raw data in response under key 'instruments' (dictionary)

and the methods:
+ `save()` to save the data as `.csv` and `.xlsx` files
        """
        return Markdown(md)
