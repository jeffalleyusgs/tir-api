import requests
import json

class Sgcn:
    def __init__(self, operation_mode="local", cache_root=None, cache_manager=None):
        self.description = "Set of functions for returning SGCN data"

    def get_sgcn_aggregate_data(self, scientific_name):
        sgcn_url = 'https://data.usgs.gov/sgcn/api/v1/aggregation/state?data_type=aggregation_only&states=All&criterion_type=scientificname&criterion=' + scientific_name + '&years=All'
        sgcn_data = requests.get(sgcn_url)
        try:
            return sgcn_data.json()
        except ValueError:
            return None
