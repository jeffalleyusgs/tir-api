import requests
import datetime
import pysppin
import re

class Worms:
    worms = pysppin.worms.Worms()

    def __init__(self, operation_mode="local", cache_root=None, cache_manager=None):
        self.description = "Set of functions for assembling Worms data"
        self.date_format = "%m-%d-%Y"
        self.base_date = datetime.datetime.strptime("01-01-1900", self.date_format)

    def get_worms_data_from_scientific_name(self, scientific_name):
        worms_url = self.worms.get_worms_search_url("ExactName", scientific_name)
        worms_data = requests.get(worms_url)
        try:
            return worms_data.json()
        except ValueError:
            return None
