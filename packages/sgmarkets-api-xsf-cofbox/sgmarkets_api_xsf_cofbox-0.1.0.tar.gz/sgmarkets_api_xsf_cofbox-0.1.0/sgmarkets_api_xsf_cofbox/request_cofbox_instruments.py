
from timeit import default_timer as timer
from IPython.display import Markdown

from ._util import Util
from .response_cofbox_instruments import ResponseCofboxInstruments


class RequestCofboxInstruments:
    """
    """

    def __init__(self,
                 instrumentCodes=None):
        """
        """
        dic_url = {'base_url': 'https://analytics-api.sgmarkets.com',
                   'service': '/cofbox',
                   'endpoint': '/v1/instruments'}
        self.url = Util.build_url(dic_url)
        self.instrumentCodes = [] if instrumentCodes is None else instrumentCodes
        self.dic_input = {'instruments': self.instrumentCodes}

    def info(self):
        """
        """
        md = """
A RequestCofboxInstruments object has the properties:
+ `url`: {}
+ `dic_input`: user input (dict)

and the methods:
+ `call_api()` to make the request to the url
        """.format(self.url)
        return Markdown(md)

    def call_api(self,
                 api,
                 debug=False):
        """
        See https://analytics-api.sgmarkets.com/cofbox/swagger/ui/index#!/Explore/Explore_01
        """
        t0 = timer()
        print('calling API...')
        self.dic_api = self.dic_input
        raw_response = api.get(self.url, payload=self.dic_api)
        t1 = timer()
        print('done in {:.2f} s'.format(t1 - t0))
        if debug:
            print('*** START DEBUG ***\n{}\n*** END DEBUG ***'.format(raw_response))
        response = ResponseCofboxInstruments(raw_response, self.dic_api)
        return response
