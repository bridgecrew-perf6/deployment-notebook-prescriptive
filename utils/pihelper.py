import urllib3

from osisoft.pidevclub.piwebapi.pi_web_api_client import PIWebApiClient
from osisoft.pidevclub.piwebapi.models import PIAnalysis, PIItemsStreamValues, PIStreamValues, PITimedValue, PIRequest

class PIHelper(object):
    def __init__(self):
        self.webapi = 'https://pivision.indonesiapower.corp/piwebapi'
        #pernah gagal klo pake user domain indonesiapower\
        self.username = 'pisystem'
        self.password = 'Abcd1234!'

    def connect_client(self):
        client = PIWebApiClient(self.webapi, 
                                False, 
                                username=self.username, 
                                password=self.password,
                                verifySsl=False)
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        return client