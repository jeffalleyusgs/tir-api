import requests
import datetime
import pysppin
from . import tess as pytess
import re

class Itis:
    itis_api = pysppin.itis.ItisApi()
    worms = pysppin.worms.Worms()

    def __init__(self, operation_mode="local", cache_root=None, cache_manager=None):
        self.description = "Set of functions for assembling the ITIS data"
        self.date_format = "%m-%d-%Y"
        self.base_date = datetime.datetime.strptime("01-01-1900", self.date_format)

    def get_tsn_from_scientific_name(self, scientific_name):
        search_name = '\%20'.join(re.split(' ', scientific_name))
        sci_name_url = "https://services.itis.gov/?wt=json&rows=10&q=nameWOInd:" + search_name + "\%20AND\%20(usage:accepted%20OR%20usage:valid)"
        search_url_from_itis = self.itis_api.get_itis_search_url(scientific_name)
        # search_url_from_itis works  if you add a \ before the %20 ON
        worms_url = self.worms.get_worms_search_url("ExactName", scientific_name)
        # worms url works
        tess = pytess.Tess()
        tess_url = tess.get_tess_search_url("TSN", "180530")
        # tess_url no longer found
        print("hand-crafted itis url:  {}".format(sci_name_url))
        print("url from itis library:  {}".format(search_url_from_itis))
        print("url from worms library: {}".format(worms_url))
        print("url from tess library:  {}".format(tess_url))

        # TRY TO ACCESS SGCN's public production url from here

        result = pysppin.itis.ItisApi().search("Scientific Name:" + scientific_name, name_source=None, source_date=None)
        tsn = result['data'][0]['tsn'] if 'data' in result.keys() else None
        return tsn

    # NOTE: There is a set of tools already written to process itis as a full DB download
    # if we need them.
    def get_full_itis_data_from_tsn(self, tsn):
        url = "https://www.itis.gov/ITISWebService/jsonservice/getFullRecordFromTSN?tsn=" + tsn
        result = requests.get(url)
        return result.json()