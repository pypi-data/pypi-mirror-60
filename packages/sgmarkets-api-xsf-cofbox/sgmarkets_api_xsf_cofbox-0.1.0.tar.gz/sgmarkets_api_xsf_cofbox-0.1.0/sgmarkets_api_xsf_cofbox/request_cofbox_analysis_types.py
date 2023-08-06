
from timeit import default_timer as timer
from IPython.display import Markdown

from ._util import Util
from .response_cofbox_analysis_types import ResponseCofboxAnalysisTypes


class RequestCofboxAnalysisTypes:
    """
    """

    def __init__(self):
        """
        """
        dic_url = {'base_url': 'https://analytics-api.sgmarkets.com',
                   'service': '/cofbox',
                   'endpoint': '/v1/analysis-types'}
        self.url = Util.build_url(dic_url)


    def info(self):
        """
        """
        md = """
A RequestCofboxUnderlyings object has the properties:
+ `url`: {}

and the methods:
+ `call_api()` to make the request to the url
        """.format(self.url)
        return Markdown(md)

    def call_api(self,
                 api,
                 debug=False):
        """
        See https://analytics-api.sgmarkets.com/cofbox/swagger/ui/index#!/Analyse/Analyse_01
        """
        t0 = timer()
        print('calling API...')
        raw_response = api.get(self.url)
        t1 = timer()
        print('done in {:.2f} s'.format(t1 - t0))
        if debug:
            print('*** START DEBUG ***\n{}\n*** END DEBUG ***'.format(raw_response))
        response = ResponseCofboxAnalysisTypes(raw_response)
        return response
