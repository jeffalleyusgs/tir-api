import requests
import datetime

class Ecos:
    def __init__(self, operation_mode="local", cache_root=None, cache_manager=None):
        self.description = "Set of functions for assembling the ECOS data"
        self.date_format = "%m-%d-%Y"
        self.base_date = datetime.datetime.strptime("01-01-1900", self.date_format)

    def get_entire_ecos_set(self):
        # This is every column that can be pulled from ECOS
        ecos_all_columns = "https://ecos.fws.gov/ecp/pullreports/catalog/species/report/species/export?columns=/species@cn,sn,status,desc,listing_date,cn,dps,id,sid,abbrev,desc,listing_date,status,country,in,is_bcc,is_foreign,agency,more_info_url,alt_status,range_envelope,range_shapefile,sn,gn,status_category,vipcode&format=json&limit=50000&sort=/species@cn+asc;/species@sn+asc"
        ecos_important_columns = "https://ecos.fws.gov/ecp/pullreports/catalog/species/report/species/export?columns=/species@cn,sn,status,desc,listing_date&format=json&limit=50000&sort=/species@cn+asc;/species@sn+asc"

        ecos_response = requests.get(ecos_all_columns)
        ecos_list = ecos_response.json()
        ecos_dict = dict()
        for entry in ecos_list['data']:
            common_name = entry[0]
            key = entry[1]['value']
            status = entry[2]
            new_date_field = entry[4]
            #if key == "Megaptera novaeangliae": print("{} {} {}".format(key, status, new_date_field))
            newdate = datetime.datetime.strptime(new_date_field, self.date_format) if new_date_field != None else self.base_date
            if key in ecos_dict:
                old_date_field = ecos_dict[key]['date']
                olddate = datetime.datetime.strptime(old_date_field, self.date_format) if old_date_field != None else self.base_date
            else: olddate = self.base_date

            # More data can be added to this record from the original ecos record if needed
            if (newdate >= olddate): ecos_dict[key] = {'commonname': common_name, 'status': status, 'date' : new_date_field}

        return ecos_dict

    def get_single_entry(self, entry):
        # Search for a single entry by scientific name in ecos
        response = requests.get("https://ecos.fws.gov/ecp/pullreports/catalog/species/report/species/export?columns=/species@cn,sn,status,desc,listing_date&filter=/species@sn+=+%27" + entry + "%27&format=json&limit=100&sort=/species@cn+asc;/species@sn+asc")
        single_response = response.json()
        data = single_response['data']
        if len(data) == 0: return "no ecos entry"
        cleaned_response = dict()
        cleaned_response['commonname'] = data[0][0]
        cleaned_response['scientificname'] = data[0][1]['value']
        cleaned_response['url'] = data[0][1]['url']
        cleaned_response['ESA_listings'] = list()
        for entry in data:
            record = {'status' : entry[2], 'location' : entry[3], 'date' : entry[4]}
            cleaned_response['ESA_listings'].append(record)
            pass
        return cleaned_response
