
class Tess:
    def __init__(self):
        self.description = 'Set of functions for working with the USFWS Threatened and Endangered Species System'


    def get_tess_search_url(self,queryType,criteria):

        if queryType != "TSN":
            criteria = '"'+bis.string_cleaning(criteria)+'"'

        return "https://ecos.fws.gov/ecp0/TessQuery?request=query&xquery=/SPECIES_DETAIL["+queryType+"="+criteria+"]"


    def tess_query(self,queryurl):
        import requests
        import xmltodict
        from datetime import datetime

        # These properties in TESS data often contain single quotes or other characters that need to be escaped in order for the resulting data to be inserted into databases like PostgreSQL
        keysToClean = ["COMNAME","INVNAME"]

        listingStatusKeys = ["STATUS_TEXT","LISTING_DATE","POP_ABBREV","POP_DESC"]

        tessData = {}
        tessData["cacheDate"] = datetime.utcnow().isoformat()
        tessData["result"] = False

        # Query the TESS XQuery service
        tessXML = requests.get(queryurl).text

        # Build an unordered dict from the TESS XML response (we don't care about ordering for our purposes here)
        tessDict = xmltodict.parse(tessXML, dict_constructor=dict)

        if "results" not in list(tessDict.keys()):
            return tessData

        # Handle cases where there is more than one listing designation for a species
        if tessDict["results"] is not None and type(tessDict["results"]["SPECIES_DETAIL"]) is list:
            tessData["result"] = True
            tessData["ENTITY_ID"] = tessDict["results"]["SPECIES_DETAIL"][0]["ENTITY_ID"]
            tessData["SPCODE"] = tessDict["results"]["SPECIES_DETAIL"][0]["SPCODE"]
            tessData["VIPCODE"] = tessDict["results"]["SPECIES_DETAIL"][0]["VIPCODE"]
            tessData["DPS"] = tessDict["results"]["SPECIES_DETAIL"][0]["DPS"]
            tessData["COUNTRY"] = tessDict["results"]["SPECIES_DETAIL"][0]["COUNTRY"]
            tessData["INVNAME"] = tessDict["results"]["SPECIES_DETAIL"][0]["INVNAME"]
            tessData["SCINAME"] = tessDict["results"]["SPECIES_DETAIL"][0]["SCINAME"]
            tessData["COMNAME"] = tessDict["results"]["SPECIES_DETAIL"][0]["COMNAME"]
            try:
                tessData["REFUGE_OCCURRENCE"] = tessDict["results"]["SPECIES_DETAIL"][0]["REFUGE_OCCURRENCE"]
            except:
                pass
            tessData["FAMILY"] = tessDict["results"]["SPECIES_DETAIL"][0]["FAMILY"]
            tessData["TSN"] = tessDict["results"]["SPECIES_DETAIL"][0]["TSN"]

            tessData["listingStatus"] = []

            for speciesDetail in tessDict["results"]["SPECIES_DETAIL"]:
                thisStatus = {}
                thisStatus["STATUS"] = speciesDetail["STATUS_TEXT"]
                # If a species is not actually listed, there will not be a listing date
                if "LISTING_DATE" in speciesDetail:
                    thisStatus["LISTING_DATE"] = speciesDetail["LISTING_DATE"]
                # There are cases where population description information is missing from TESS records
                if "POP_DESC" in speciesDetail:
                    thisStatus["POP_DESC"] = speciesDetail["POP_DESC"]
                if "POP_ABBREV" in speciesDetail:
                    thisStatus["POP_ABBREV"] = speciesDetail["POP_ABBREV"]
                tessData["listingStatus"].append(thisStatus)

        # Handle cases where there is only a single listing status for a species by cleaning/popping a few keys and appending the rest of the result dict
        elif tessDict["results"] is not None and type(tessDict["results"]["SPECIES_DETAIL"]) is dict:
            tessData["result"] = True

            # Clean up the problematic string properties
            for key in keysToClean:
                tessData[key] = tessDict["results"]["SPECIES_DETAIL"][key]
                tessDict["results"]["SPECIES_DETAIL"].pop(key,None)

            # Build the single listing status record for this species
            tessData["listingStatus"] = []
            thisStatus = {}
            thisStatus["STATUS"] = tessDict["results"]["SPECIES_DETAIL"]["STATUS_TEXT"]
            # If a species is not actually listed, there will not be a listing date
            if "LISTING_DATE" in tessDict["results"]["SPECIES_DETAIL"]:
                thisStatus["LISTING_DATE"] = tessDict["results"]["SPECIES_DETAIL"]["LISTING_DATE"]
            # There are cases where population description information is missing from TESS records
            if "POP_DESC" in tessDict["results"]["SPECIES_DETAIL"]:
                thisStatus["POP_DESC"] = tessDict["results"]["SPECIES_DETAIL"]["POP_DESC"]
            if "POP_ABBREV" in tessDict["results"]["SPECIES_DETAIL"]:
                thisStatus["POP_ABBREV"] = tessDict["results"]["SPECIES_DETAIL"]["POP_ABBREV"]
            tessData["listingStatus"].append(thisStatus)

            # Get rid of listing status information from the original dict
            for key in listingStatusKeys:
                tessDict["results"]["SPECIES_DETAIL"].pop(key,None)

            # Put the remaining properties into the record for this species
            tessData.update(tessDict["results"]["SPECIES_DETAIL"])

        return tessData