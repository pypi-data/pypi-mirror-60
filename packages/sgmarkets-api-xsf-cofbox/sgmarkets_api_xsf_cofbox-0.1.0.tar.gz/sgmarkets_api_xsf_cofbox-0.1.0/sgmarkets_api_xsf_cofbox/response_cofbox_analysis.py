
import json
import pandas as pd

from IPython.display import display, HTML, Markdown
from copy import deepcopy as copy

from sgmarkets_api_auth.util import save_result

from ._plot import Plot
from ._util import Util
from ._dashboard import MyDashboard


pd.options.mode.chained_assignment = None


class ResponseCofboxAnalysis:
    """
    TBU
    """

    def __init__(self):
        """
        """
        pass

    def load_stored_data(self,
                         path=None,
                         data=None):
        """
        """
        msg = 'path or data are not None'
        assert (path is not None) or (data is not None), msg

        if path is not None:
            with open(path, 'r') as f:
                try:
                    self.raw_data = json.loads(f.read())
                    self.dic_res = self._build_dic_res()
                except:
                    print('invalid path')

    def load_raw_data(self,
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
        self.dic_res = self._build_dic_res()

    def _build_dic_res(self):
        """
        """
        data_api = self.raw_data
        dic = {}

        for data_ic in data_api:
            ic = data_ic['instrumentCode']
            dic[ic] = {}
            if 'cof' in data_ic:
                data = data_ic['cof']
                df = self._build_df_cof(data)
                dic[ic]['Cof'] = df
            if 'fwdCof' in data_ic:
                data = data_ic['fwdCof']
                df = self._build_df_fwdcof(data)
                dic[ic]['fwdCof'] = df
            if 'rollDownCof' in data_ic:
                data = data_ic['rollDownCof']
                df = self._build_df_rolldowncof(data)
                dic[ic]['rollDownCof'] = df

        return dic

    def _build_df_cof(self, data):
        """
        """
        li_d = []
        for e in data:
            date = e['date']
            series = e['series']
            for s in series:
                d = {}
                d['date'] = date
                for k in ['maturityCode', 'maturityDate', 'cofDiv100pct']:
                    d[k] = s[k]
                li_d.append(d)
        df = pd.DataFrame(li_d)
        df = df[['date', 'maturityCode', 'maturityDate', 'cofDiv100pct']]

        return df

    def _build_df_fwdcof(self, data):
        """
        """
        li_d = []
        for e in data:
            date = e['date']
            series = e['series']
            for s in series:
                d = {}
                d['date'] = date
                for k in ['maturityCode', 'maturityDate']:
                    d[k] = s[k]
                d2 = s['fwdCofs']
                if len(d2) > 0:
                    for e2 in d2:
                        for k in ['maturityCode', 'maturityDate', 'fwdCofDiv100pct']:
                            if k == 'fwdCofDiv100pct':
                                d[k] = e2[k]
                            else:
                                d['fwd '+k] = e2[k]
                            li_d.append(d)
        df = pd.DataFrame(li_d)
        df = df[['date', 'maturityCode', 'maturityDate',
                 'fwd maturityCode', 'fwd maturityDate',
                 'fwdCofDiv100pct']]
        return df

    def _build_df_rolldowncof(self, data):
        """
        """
        li_d = []
        for e in data:
            date = e['date']
            series = e['series']
            for s in series:
                d = {}
                d['date'] = date
                for k in ['maturityCode', 'maturityDate']:
                    d[k] = s[k]
                d2 = s['rollDownCofs']
                if len(d2) > 0:
                    for e2 in d2:
                        for k in ['maturityCode', 'maturityDate', 'rollDownCofDiv100pct']:
                            if k == 'rollDownCofDiv100pct':
                                d[k] = e2[k]
                            else:
                                d['fwd '+k] = e2[k]
                            li_d.append(d)
        df = pd.DataFrame(li_d)
        df = df[['date', 'maturityCode', 'maturityDate',
                 'fwd maturityCode', 'fwd maturityDate',
                 'rollDownCofDiv100pct']]
        return df

    def save(self,
             folder_save='dump',
             name=None,
             tagged=True):
        """
        """
        if name is None:
            name = 'SG_COFBOX_Analysis'

        path = Util.save_as_json(self.raw_data,
                                 folder_save,
                                 name=name,
                                 tagged=tagged)

        print('raw_data saved to {}'.format(path))

    def info(self):
        """
        """
        md = """
A ResponseCofboxRelativeRoll object has the properties:
+ `dic_req`: request data (dict)
+ `dic_res`: response data (dict of dataframes)

+ `raw_data`: raw data in response (dictionary)

and the methods:
+ `save()` to save the data as several `.csv` or `.xlsx` files
"""
        return Markdown(md)
