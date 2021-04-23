import os
import json
import requests
import time
import datetime
from api import app
from flask import jsonify
import collections

ELASTIC_BASE_URL = os.environ.get("ELASTIC_BASE_URL")
PUBLIC_S3_BUCKET = os.environ.get("PUBLIC_S3_BUCKET")


def get_elastic_result(index_suffix, es_query):
    """
    Hits the elastic search index and returns the result.
    https://www.elastic.co/guide/en/elasticsearch/reference/7.0/query-dsl.html

    :param index_suffix: Name of the elastic search index to query
    :param es_query: A python object representation of a elastic search query (dsl)
    :return: json response from the elastic searvice
    """

    es_url = "%s/%s/_search" % (ELASTIC_BASE_URL, index_suffix)
    response = None
    if es_query is not None:
        response = requests.get(
            headers={"content-type": "application/json"},
            url=es_url,
            data=json.dumps(es_query),
        ).json()
    else:
        response = requests.get(url=es_url).json()
    if "error" in response:
        raise Exception(response)
    return response

def get_species(offset,pagesize, species, years):

    # Need to replace single apostrophes with double apostrophes because that is how
    # the common name is stored in the DB
    species = species.replace("'", "''")

    years_filter = get_years_filter(years, None)
    q = {
        'from':offset,'size':pagesize,
        'query': {
            'bool': {
                'should': [
                    {
                        'match_phrase': { 'data.scientific name': species}
                    },
                    {
                        'match_phrase': { 'data.scientificname': species}
                    },
                    {
                        'match_phrase': { 'data.clean_scientific_name': species}
                    },
                    {
                        'match_phrase': { 'data.common name': species }
                    },
                    {
                        'match_phrase': { 'data.commonname': species }
                    }
                ],
                'minimum_should_match' : 1,
                'must':years_filter
            }
        }
    }
    return q

def get_primary_query_clause(search_fields, states, years, nationallist, primary_search_field):
    nationallist_filter = get_national_list_filter(nationallist)
    years_filter = get_years_filter(years, nationallist_filter)
    states_filter = get_compound_filter(states, "data.state")

    if search_fields:
        primary_fields = search_fields.split(",")
        clause = []
        for primary_field in primary_fields:
            primary_field = primary_field.capitalize()
            clause.append({ primary_search_field : primary_field })
        phrases = json.dumps([dict(match_phrase = ph) for ph in clause])
        jsonphrases = json.loads(phrases)

        q = {
            'bool': {
                'should': jsonphrases,
                'minimum_should_match' : 1,
                'must' : years_filter,
                'filter' : states_filter,
            }
         }
        return q

    if states_filter:
        q = { 'bool': {
            'must' : years_filter,
            'filter' : states_filter,
            }
         }
        return q

    if years_filter:
        q = {'bool' : { 'must' : years_filter}}
        return q

    if nationallist_filter:
        return nationallist_filter

def get_years_filter(years_fields, nationallist_filter):

    if not years_fields:
        return nationallist_filter

    years = years_fields.split(",")
    if len(years) > 1:
        return nationallist_filter

    if not nationallist_filter:
        return {'match':{'data.year':years[0]}}
    else:
        return [{'match':{'data.year':years[0]}},nationallist_filter]

def get_national_list_filter(nationallist):
    if not nationallist:
        return None
    value = False
    if nationallist.lower() == "true": value = True
    return {'match':{'data.nationallist':value}}

def get_compound_filter(filter_fields, filter_field_name):
    if not filter_fields:
        return None

    fields = filter_fields.split(",")
    clause = []
    for field in fields:
        field = field.capitalize()
        clause.append({ filter_field_name : field })
    phrases = json.dumps([dict(match_phrase = ph) for ph in clause])
    jsonphrases = json.loads(phrases)
    compound_filter = {
            'bool' : {
            'should' : jsonphrases, 'minimum_should_match' : 1
            }
    }
    return compound_filter

def get_state(offset,pagesize, state,taxa):
    q = {}
    if (taxa is None ):
        q = {
            'from':offset,'size':pagesize,
            'query': {'match_phrase' : {'data.state' : state}}
        }
    else:
        q = {'from':offset,'size':pagesize,
            'query': {
                'bool': {
                    'must':{'match':{'data.taxonomic category':taxa}},
                    'filter':{'match_phrase':{'data.state':state}}
                }
            }
        }
    return q

def get_state_year(offset,pagesize,state,year,taxa):
    q ={}
    if(taxa is None):
        q = {
            'from':offset,'size':pagesize,
            'query': {
                'bool': {
                    'must':{'match':{'data.year':year}},
                    'filter':{'match_phrase':{'data.state':state}}
                }
            }
        }
    else:
        q = {
            'from':offset,'size':pagesize,
            'query': {
                'bool': {
                    'must':[{'term':{'data.year':year}}, {'match':{'data.taxonomic category':taxa}}],
                    'filter':{'match_phrase':{'data.state':state}}
                },
            }
        }
    return q

def get_natlist_year(offset,pagesize,year,order_by):
    q = {}
    if (order_by == 'species'):
        sort_order = "data.scientificname.keyword"
    else:
        sort_order = "data.state.keyword"

    q = {
        'from':offset,'size':pagesize,
        'query':{
            'bool': {
                'must':{'match':{'data.nationallist':'true'}},
                'filter':{'term':{'data.year':year}}
            },
        },
        "sort" : [{sort_order : {"order" : "asc"}}]
        }
    return q

def get_natlist_allyears(offset,pagesize,order_by):
    q = {}
    if (order_by == 'species'):
        sort_order = "data.scientificname.keyword"
    else:
        sort_order = "data.state.keyword"

    q = {
        'from':offset,'size':pagesize,
        'query': {"match":{"data.nationallist":"true"}},
        "sort" : [{sort_order : {"order" : "asc"}}]
    }

    return q

def get_sort_criteria(sort_value, sort_order, grouping):
    if sort_value: sort_value = sort_value.lower()
    if not sort_value or sort_value == "unsorted" and not sort_value.startswith("sci") and not sort_value.startswith("com"):
        return None, "", "", ""

    value = "data.scientificname.keyword" if sort_value.startswith("sci") else "data.commonname.keyword"
    order = "desc" if sort_order and sort_order.lower().startswith("desc") else "asc"
    groupby = "interstate" if grouping and grouping.lower().startswith("inter") else "intrastate"

    # NOTE: the sort order entered by the user ONLY applies to the scientific name/common name field.
    # The sort order for the states (whether primary or secondary), is ALWAYS 'asc'
    if groupby.startswith("inter"):
        primary_sort_key = value
        secondary_sort_key = "data.state.keyword"
        pri_order = order
        sec_order = "asc"
    else:
        primary_sort_key = "data.state.keyword"
        secondary_sort_key = value
        pri_order = "asc"
        sec_order = order

    sort_clause = [
            {primary_sort_key : {"order" : pri_order}},
            {secondary_sort_key : {"order" : sec_order}},
            {"data.year.keyword" : {"order" : "asc"}}
            ]
    sort_operator = "&sort={}".format(value.replace("data.", "").replace(".keyword", ""))
    order_operator = "&order={}".format(order)
    group_operator = "&group={}".format(groupby)
    return sort_clause, sort_operator, order_operator, group_operator

def get_multistate(offset,pagesize,state_list,criterion,criterion_type,reporting_year,state_operator,nationallist, aggregation):
    # on an intersection query, pagesize might not give all results
    if (state_operator.lower() == 'intersection' and len(state_list) > 1):
        q = {'size':1000}
    else:
        q = {'from':offset,'size':pagesize}

    state_match_phrase = get_state_match_clause(state_list)

    if (reporting_year.lower() != "all"):
        state_match_phrase["must"] = {"match_phrase":{'data.year':reporting_year}}

    if (criterion.lower() != "all"):
        if criterion.lower() == "null":
            state_match_phrase['must_not'] = [{'wildcard':{'data.{}'.format(criterion_type):"*"}}]
        else:
            state_match_phrase['filter'] = {'match_phrase':{'data.{}'.format(criterion_type):criterion}}

    add_nationallist_filter(state_match_phrase, nationallist)

    q["query"]={"bool":state_match_phrase}
    if aggregation: q["aggs"] = get_state_aggregation("state")

    return q

def get_state_match_clause(state_list):
    if state_list[0].lower() == "all": return {}

    states_filter = []
    for state in state_list:
        states_filter.append({"match_phrase":{"data.state":state}})

    state_match_clause = {'should':states_filter}
    state_match_clause["minimum_should_match"] = 1

    return state_match_clause

def add_nationallist_filter(state_match_phrase, nationallist):
    nationallist_filter = get_national_list_filter(nationallist)
    if nationallist_filter:
        if "must" in state_match_phrase.keys():
            phrase = state_match_phrase["must"],nationallist_filter
        else:
            phrase = nationallist_filter
        state_match_phrase["must"] = phrase

def get_state_aggregation(agg_field):
    return {"agg": { "terms": {
                    "field": "data.{}.keyword".format(agg_field),
                    "size": 100
                    }}}

def get_intersection_of_species(records, num_states):
    species_and_year = list()
    for record in records:
        record_id = record['year'] + "," + record['scientificname']
        species_and_year.append(record_id)

    occurrences = collections.Counter(species_and_year)
    intersecting_species = list()
    for occurrence in occurrences:
        if (occurrences[occurrence] == num_states):
            intersecting_species.append(occurrence)

    sorted_species = sorted(intersecting_species)
    species_dict = dict()
    for species in sorted_species:
        fields = species.split(",")
        year = fields[0]
        specie = fields[1]
        if year not in species_dict.keys():
            species_dict[year] = list()
        species_dict[year].append(specie)

    return species_dict

def handle_error(e, message, status_code=400):
    """
    Standardize the error response
    :param e: An error
    :param message: String; An endpoint specific message
    :param status_code: what status code to return. Default 400
    :return: a standardized error message with status code set
    """
    app.logger.info("Encountered an error: " + str(e))
    error = {
        "error": str(e),
        "time": datetime.datetime.fromtimestamp(time.time()),
        "message": message,
    }
    response = jsonify(error)
    response.status_code = status_code
    return response
