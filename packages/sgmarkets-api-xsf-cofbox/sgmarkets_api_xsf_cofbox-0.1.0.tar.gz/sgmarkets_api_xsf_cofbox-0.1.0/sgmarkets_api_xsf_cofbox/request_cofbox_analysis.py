

from timeit import default_timer as timer
from IPython.display import display, Markdown

from ._util import Util
from .response_cofbox_analysis import ResponseCofboxAnalysis


class RequestCofboxAnalysis:
    """
    """

    def __init__(self,
                 analysisTypes=None,
                 instruments=None,
                 startDate=None,
                 endDate=None,
                 colTypes=None,
                 data=None,
                 path_data=None):
        """
        """
        if (data is not None) or (path_data is not None):
            self.data = data
            self.path_data = path_data
            return

        dic_url = {'base_url': 'https://analytics-api.sgmarkets.com',
                   'service': '/cofbox',
                   'endpoint': '/v1/analysis'}
        self.url = Util.build_url(dic_url)

        # analysisTypes
        if analysisTypes is None:
            analysisTypes = ['Cof', 'FwdCof', 'RollDownCof']

        valid_colTypes = ['CofDiv100pct', 'CofDivMarket']
        if colTypes is None:
            colTypes = valid_colTypes

        # instruments
        msg = 'instruments must be a list of dict'
        assert isinstance(instruments, list), msg
        for e in instruments:
            assert isinstance(e, dict), msg

            msg = 'Each instrument is a dict with keys "instrumentCode" and "maturitiesCodes"'
            assert 'instrumentCode' in e.keys()
            assert 'maturitiesCodes' in e.keys()
            li_mat_codes = e['maturitiesCodes']

            msg = 'maturitiesCodes must be a list of str like 1Y, 3M, etc'
            isinstance(li_mat_codes, list), msg
            for e2 in li_mat_codes:
                assert len(e2) == 2, msg
                assert e2[0].isdigit(), msg
                assert e2[1] in ['M', 'Y'], msg

        # colTypes
        msg = 'colTypes must be a list subset of {}'.format(valid_colTypes)
        assert isinstance(colTypes, list), msg
        for e in colTypes:
            assert e in valid_colTypes, msg

        self.dic_input = {
            'analysisTypes': analysisTypes,
            'instruments': instruments,
            'startDate': startDate,
            'endDate': endDate,
            'colTypes': colTypes,
        }
        self.dic_api = self.dic_input

    def info(self):
        """
        """
        md = """
A RequestCofboxRelativeRoll object has the properties:
+ `url`: {}
+ `dic_input`: user input (dictionary)

and the methods:
+ `call_api()` to make the request to the url
""".format(self.url)
        return Markdown(md)

    def call_api(self,
                 api,
                 debug=False):
        """
        See https://analytics-api.sgmarkets.com/cofbox/swagger/ui/index#!/Analyse/Analyse_02
        """
        t0 = timer()
        print('calling API...')
        raw_response = api.post(self.url, payload=self.dic_api)
        t1 = timer()
        print('done in {:.2f} s'.format(t1 - t0))
        if debug:
            print('*** START DEBUG ***\n{}\n*** END DEBUG ***'.format(raw_response))
        response = ResponseCofboxAnalysis()
        response.load_raw_data(raw_response, self.dic_api)
        return response

    def load_data(self):
        """
        """
        response = ResponseCofboxAnalysis()
        response.load_stored_data(path=self.path_data, data=self.data)
        return response
