

from timeit import default_timer as timer
from IPython.display import display, Markdown

from ._util import Util
from .response_cofbox_instruments_details import ResponseCofboxInstrumentsDetails


class RequestCofboxInstrumentsDetails:
    """
    """

    def __init__(self,
                 instrumentCodes=None,
                 asOfDate=None):
        """
        """
        dic_url = {'base_url': 'https://analytics-api.sgmarkets.com',
                   'service': '/cofbox',
                   'endpoint': '/v1/instruments-details'}
        self.url = Util.build_url(dic_url)

        self.dic_input = {
            'instrumentCodes': instrumentCodes,
            'asOfDate': asOfDate,
        }

    def info(self):
        """
        """
        md = """
A RequestCofboxInstrumentsDetails object has the properties:
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
        See https://analytics-api.sgmarkets.com/cofbox/swagger/ui/index#!/Explore/Explore_02
        """
        t0 = timer()
        print('calling API...')
        self.dic_api = self.dic_input
        raw_response = api.get(self.url, payload=self.dic_api)
        t1 = timer()
        print('done in {:.2f} s'.format(t1 - t0))
        if debug:
            print('*** START DEBUG ***\n{}\n*** END DEBUG ***'.format(raw_response))
        response = ResponseCofboxInstrumentsDetails(raw_response, self.dic_api)
        return response
