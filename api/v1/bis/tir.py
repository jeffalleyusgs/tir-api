
import json
import re
from api import api, URL_PREFIX
from flask_restx import Resource, fields
from api.common import get_elastic_result, get_species, get_natlist_year, get_natlist_allyears, get_multistate, handle_error, PUBLIC_S3_BUCKET,\
     get_primary_query_clause,get_intersection_of_species, get_sort_criteria
from flask import request
from api.v1.bis import NS, DESCRIPTION, ELASTIC_INDEX, DEFAULT_ERROR_MESSAGE, SINGLE_UNIT_MODEL
from . import sgcn as pysgcn
from . import ecos as pyecos
from . import itis as pyitis
from . import worms as pyworms
from . import sgcn as pysgcn

"""
This collection of API endpoints serves Taxonomic Information Registry (TIR)
records in the form of a paginated list or a single record lookup by identifier.
Additionally, it provides the ability to write custom queries following the Elasticsearch
query DSL specifications. (https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl.html)
"""

# return the possible routes and parameters starting with /tir
@NS.route('/')
class Tir(Resource):
    def get(self):
        """Returns general information about the TIR API"""
        try:
            return {
                'description': DESCRIPTION.replace("\n", " ").rstrip().lstrip(),
                'fulldataset': '{}/{}.json'.format(PUBLIC_S3_BUCKET,ELASTIC_INDEX)
            }
        except Exception as e:
            return handle_error(e, DEFAULT_ERROR_MESSAGE)


# Function to replace multiple occurrences
# of a character by a single character
def replace(string, char):
    pattern = char + '{2,}'
    string = re.sub(pattern, char, string)
    return string


@NS.route('/search')
class SearchTirRecords(Resource):

    parser = api.parser()
    parser.add_argument(
        'pagesize',
        type=int,
        help="The number of TIR records to return with this page of results. Maximum 5000",
        default=1000,
        location='query',
        required=False
        )

    parser.add_argument(
        'offset',
        type=int,
        help="The number of TIR records to skip when returning a page of results ",
        default=0,
        location='query',
        required=False
        )

    parser.add_argument(
        'criterion_type',
        choices = ('common_name', 'scientific_name'),
        type=str,
        help="Search by common name or scientific name.".format(URL_PREFIX or ""),
        default='scientific_name',
        location='query',
        required=True
        )

    parser.add_argument(
        'criteria',
        type=str,
        help="A string specifying the common or scientific name to search for. Case insensitive.\nExample: Megaptera novaeangliae or Canis lupus familiaris".format(URL_PREFIX or ""),
        default='',
        location='query',
        required=False
    )

    '''
    parser.add_argument(
        'data_type',
        choices = ('full_data', 'aggregation_only'),
        type=str,
        help="Type of data to return: full records or summary aggregation numbers.".format(URL_PREFIX or ""),
        default='full_data',
        location='query',
        required=True
    )
    '''


    list_records_response = NS.model('API Response: TIR records ', {
        'thispage': fields.String(description="A link to this page of results"),
        'nextpage': fields.String(description="A link to the next page of results."),
        'pagesize': fields.Integer(default=10, description="The pagesize(Number of results returned) value used for this request. Maximum  value 5000"),
        'offset': fields.Integer(default=0, description="The offset value used for this request"),
        'queryused': fields.String(description="The actual Elasticsearch query used for this request "),
        'total': fields.Integer(description="Total number of results matching this query"),
        'records': fields.List(fields.Nested(SINGLE_UNIT_MODEL), description="A List of TIR Records"),

    })

    @NS.expect(parser)
    @NS.doc(description="List TIR records.")
    @NS.response(200, "OK", list_records_response)
    def get(self):
        """List TIR records by search criteria"""

        try:
            #sgcn = pysgcn.Sgcn(operation_mode='pipeline', cache_manager=None)
            ecos = pyecos.Ecos(operation_mode='pipeline', cache_manager=None)
            itis = pyitis.Itis(operation_mode='pipeline', cache_manager=None)
            worms = pyworms.Worms(operation_mode='pipeline', cache_manager=None)
            sgcn = pysgcn.Sgcn(operation_mode='pipeline', cache_manager=None)

            # set defaults
            offset = 0
            pagesize = 1000

            if request.args.get('offset'):
                offset = int(request.args.get('offset'))
            if request.args.get('pagesize'):
                pagesize = int(request.args.get('pagesize'))
                if(pagesize > 5000):
                    return handle_error('Invalid Parameter', 'Invalid Pagesize: Maximum 5000')

            criteria = request.args.get('criteria')
            criterion_type = request.args.get('criterion_type')
            data_type = request.args.get('data_type')

            ecos_dict = ecos.get_entire_ecos_set()

            full_data = dict()

            if criteria in ecos_dict.keys():
                ecos_data = ecos_dict[criteria]
                full_data['commonname'] = ecos_data['commonname']
                full_data['status'] = ecos_data['status']
                full_data['status_date'] = ecos_data['date']
            else:
                full_data['commonname'] = 'TBD'
                ecos_data = {'data' : 'none found'}

            ecos_found = ecos.get_single_entry(criteria)

            if criterion_type == 'scientific_name':
                itis_tsn = itis.get_tsn_from_scientific_name(criteria)
                if itis_tsn == None:
                    return {'search by' : criterion_type, 'criteria' : criteria, 'full_data' : 'no data found'}
                itis_data = itis.get_full_itis_data_from_tsn(itis_tsn)
                if itis_data and full_data['commonname'] == 'TBD':
                    full_data['commonname'] = itis_data['commonNameList']['commonNames'][0]['commonName']

            worms_data = worms.get_worms_data_from_scientific_name(criteria)
            sgcn_data = sgcn.get_sgcn_aggregate_data(criteria)

            full_data['ecos'] = ecos_found
            full_data['worms'] = worms_data if worms_data else 'no worms entry'
            full_data['sgcn'] = sgcn_data if sgcn_data['total'] != 0 else 'no sgcn entry'
            full_data['itis'] = itis_data

            total_records_returned = 1
            criteria_param = "" if criteria == None else "&criteria=" + criteria
            params = "{}?criterion_type={}&criteria={}&data_type={}&offset={}&pagesize={}"
            this_page = params.format(request.base_url, criterion_type, criteria, data_type, offset, pagesize)
            next_page = "N/A" if total_records_returned <= int(pagesize) else params.format(request.base_url, data_type, criteria_param, offset + pagesize, pagesize)
            result = {
                'thispage': this_page,
                'nextpage': next_page,
                'pagesize': pagesize,
                'offset': offset,
                'search_by' : criterion_type,
                'criteria' : criteria,
                'full_data': full_data,
            }

            return result

        except Exception as e:
            return handle_error(e, DEFAULT_ERROR_MESSAGE)

def clean_record(record):
    cleanRecord = record['data']
    cleanRecord['submitted_scientificname'] = ""
    cleanRecord['taxonomic_category'] = record['data']['taxonomic category']
    cleanRecord['metadata'] = dict()
    cleanRecord['metadata']['uri'] = record['uri']
    cleanRecord['metadata']['run_id'] = record['run_id']
    cleanRecord['metadata']['record_id'] = record['row_id']
    keys = record['data'].keys()
    if 'commonname' in keys and record['data']['commonname']:
        commonname = record['data']['commonname']
    elif 'common name' in keys:
        commonname = record['data']['common name']
    else:
        commonname = "no common name"
    cleanRecord['commonname'] = replace(commonname, "'")

    keys = cleanRecord.keys()
    submitted_scientific_name = "unknown"
    if 'scientificname' not in keys:
        cleanRecord['scientificname'] = cleanRecord['clean_scientific_name']
    if 'scientific name' in keys:
        submitted_scientific_name = cleanRecord['scientific name']
        del cleanRecord['scientific name']
    if 'clean_scientific_name' in keys:
        submitted_scientific_name = cleanRecord['clean_scientific_name']
        del cleanRecord['clean_scientific_name']
    cleanRecord['submitted_scientificname'] = submitted_scientific_name
    if 'taxonomic category' in keys: del cleanRecord['taxonomic category']
    if 'common name' in keys: del cleanRecord['common name']
    if 'sppin_key' in keys: del cleanRecord['sppin_key']
    if 'taxogroupings' in keys: del cleanRecord['taxogroupings']
    if 'sciencebase_item_id' in keys: del cleanRecord['sciencebase_item_id']
    if 'id' in keys: del cleanRecord['id']

    return cleanRecord;

def group_by(criteria, records, primary_search_field):
    if not criteria:
        return records

    if primary_search_field == "taxonomic_category":
        search_field = "taxonomic_category"
    elif primary_search_field == "class_name":
        search_field = "class_name"
    else:
        search_field = "scientificname"

    newRecords = []
    primary_fields = criteria.split(",")
    if len(primary_fields) < 2:
        return records

    for primary_field in primary_fields:
        primary_field = primary_field.capitalize()
        for record in records[:]:
            if record[search_field] == primary_field:
                newRecords.append(record)
                records.remove(record)

    return newRecords


'''
@NS.route('/aggregation/state')
class TirStateLookup(Resource):
    parser = api.parser()
    parser.add_argument(
        'pagesize', type=int, help="The number of TIR records to return with this page of results. Maximum value 5000", default=10, location='query', required=False)
    parser.add_argument(
        'offset', type=int, help="The number of TIR records to skip when returning a page of results", default=0, required=False)

    # Sort parameters (optional)
    parser.add_argument(
        'sort',
        choices = ('scientific name', 'common name'),
        type=str,
        help="Sort the results by scientific name or by common name.\nIf multiple results are returned for a species, they will be presented in order of 'year', oldest first.\nDefaults to 'unsorted' if not specified.",
        default="unsorted",
        required=False)

    parser.add_argument(
        'order',
        choices = ('asc', 'desc'),
        type=str,
        help="Direction of sort:\n  asc = ascending (a->z)\n  desc = descending (z->a)\nDefaults to 'asc' if not specified.",
        required=False)

    parser.add_argument(
        'group',
        choices = ('intra-state', 'inter-state'),
        type=str,
        help="Group the sort results\n  intra-state = sort the results within each state\n  inter-state = sort the results across ALL states\nDefaults to intra-state if not specified.\nState order will ALWAYS be A->Z",
        required=False)

    parser.add_argument(
    'data_type',
    choices = ('full_data', 'aggregation_only'),
    type=str,
    help="Type of data to return: full records or summary aggregation numbers.".format(URL_PREFIX or ""),
    default='full_data',
    location='query',
    required=True
    )
    parser.add_argument(
        'states',
        type=str,
        help="The State(s) to lookup. Can be 'all' or a commma-separated list of states",
        default="All",
        required=True
        )
    parser.add_argument(
        'state_operator',
        choices = ('union', 'intersection'),
        type=str,
        help="This field is only used if performing a multi-state search. Indicates if results are a Union(in ANY state) or an Intersection(in ALL states listed).".format(URL_PREFIX or ""),
        default='N/A',
        location='query',
        required=False
        )
    parser.add_argument(
        'criterion_type',
        choices = ('taxonomic category', 'scientificname', 'class_name'),
        type=str,
        help="Search by taxonomic category or scientific name or class name.".format(URL_PREFIX or ""),
        default='taxonomic category',
        location='query',
        required=True
        )
    parser.add_argument(
        'criterion',
        type=str,
        help="A string specifying the taxonomic category(birds,mammals,etc...) OR scientific name OR class name(Aves, Reptilia, etc...) to search for.  Case insensitive.\nLeave blank or specify 'all' to include all records.\nSpecify 'null' to look for records with missing data.\n'Null' for scientificname will find records for which no taxonomic authority exists(the place scientific name authoritatively comes from), thus the scientific name had to come from the SWAP record.\n\nOf note: searching for 'mammal' or 'bird' is handy for finding mis-classified records.".format(URL_PREFIX or ""),
        default="All",
        required=False
        )
    parser.add_argument(
        'years',
        type=str,
        help="Valid years are All, 2005 or 2015. If no year entered all years will be returned",
        default="All",
        required=False
        )
    parser.add_argument(
        'nationallist',
        type=bool,
        help="A boolean specifying the whether or not to include national list entries.  If not specified, nationallist will not be used as a filter.\nOf note: a species will NOT be included on the nationallist if no taxonomic authority is found nor was it on the historic list.".format(URL_PREFIX or ""),
        default='',
        location='query',
        required=False
    )

    list_records_response = NS.model('API Response: TIR records ', {
        'pagesize': fields.Integer(default=10, description="The pagesize value used for this request."),
        'offset': fields.Integer(default=0, description="The offset value used for this request"),
        'total': fields.Integer(description="Total number of results matching this query"),
        'queryused': fields.String(description="The actual Elasticsearch query used for this request "),
        'records': fields.List(fields.Nested(SINGLE_UNIT_MODEL), description="A List of TIR Records"),
        'nextpage': fields.String(description="A link to the next page of results."),
        'thispage': fields.String(description="A link to this page of results"),
    })
    @NS.expect(parser)
    @NS.doc(description="List TIR records data or the aggregation of the returned data from a state or states search. The search allows selection of a specific taxonomic category, class name, or scientific name for a specific year. Multiple states can be searched at the same time. ")
    @NS.response(200, "OK", list_records_response)
    def get(self):
        """List TIR records data or the aggregation of the returned data from a state or states search."""
        pagesize = 10
        offset = 0

        if request.args.get('offset'):
            offset = int(request.args.get('offset'))
        if request.args.get('pagesize'):
            pagesize = int(request.args.get('pagesize'))
            if(pagesize > 5000):
                return handle_error('Invalid Parameter', 'Invalid Pagesize: Maximum 5000')

        years = request.args.get('years')
        years = "all" if not years else years.lower()
        if(years != "2015" and years != "2005" and years != "all"):
            return handle_error('Invalid Parameter', 'Invalid Year Entered')

        criterion = request.args.get('criterion')
        criterion = "all" if not criterion or criterion == "" else criterion.lower()

        criterion_type = request.args.get('criterion_type')

        state_operator = request.args.get('state_operator')
        state_operator = "n/a" if not state_operator else state_operator.lower()

        states = request.args.get('states')
        states = "all" if states is None or states == "" else states.lower()
        state_list = str(states).split(',')
        num_states = len(state_list)

        aggregation = True if request.args.get('data_type') == "aggregation_only" else False
        nationallist = request.args.get('nationallist')

        if state_operator == "intersection" and aggregation:
            return handle_error('Invalid Parameter combination', 'Cannot do intersection on aggregation of data.')
        if (states == "all" or num_states < 2) and state_operator == "intersection":
            return handle_error('Invalid Parameter combination', 'Cannot do intersection on ALL states or an individual state.')

        es_query = get_multistate(offset,pagesize,state_list,criterion,criterion_type,years,state_operator,nationallist,aggregation)
        sort_clause, sort_operator, order_operator, group_operator = get_sort_criteria(request.args.get('sort'), request.args.get('order'), request.args.get('group'))

        if sort_clause and not aggregation:
            es_query["sort"] = sort_clause

        r = get_elastic_result(ELASTIC_INDEX, es_query)

        national = "ignored" if not nationallist else nationallist
        if "aggregations" in r.keys():
            aggregation = {}
            aggregation = r["aggregations"]["agg"]
            aggregation['states'] = aggregation.pop('buckets')
            for state in aggregation['states']:
                state['state'] = state.pop('key')
                state['count'] = state.pop('doc_count')
            del aggregation["doc_count_error_upper_bound"]
            del aggregation["sum_other_doc_count"]
            if years == "all": years = "2005,2015"
            return {
                criterion_type : criterion,
                'year' : years,
                'nationallist' : national,
                'total' : r['hits']['total'],
                **aggregation
            }

        records = []
        base_url = str(request.base_url)
        url_base = base_url.replace("state","records")
        for hit in r['hits']['hits']:
            record = hit['_source']
            record['uri'] = url_base + '/' + str(record['row_id'])
            record = clean_record(record)
            records.append(record)

        if(state_operator == 'intersection' and num_states > 1):
            results = get_intersection_of_species(records, num_states)
            result = {
                'states' : states,
                'criterion_type' : criterion_type,
                'criterion' : criterion,
                'nationallist' : national,
                'in_common' : results
                }
            return result

        nationallist_param = "" if not nationallist else "&nationallist=" + nationallist
        criterion_param = "" if not criterion else "&criterion=" + criterion
        data_type = request.args.get('data_type')
        state_operator_param = "" if not state_operator or state_operator.lower() == "n/a" else "&state_operator=" + state_operator
        params = "{}?offset={}&pagesize={}&data_type={}&states={}{}&criterion_type={}{}&year={}{}{}{}{}"
        result = {
            'thispage': params.format(request.base_url,offset, pagesize,data_type,states,state_operator_param,criterion_type,criterion_param,years,nationallist_param,sort_operator,order_operator,group_operator),
            'nextpage': params.format(request.base_url,offset+pagesize, pagesize,data_type,states,state_operator_param,criterion_type,criterion_param,years,nationallist_param,sort_operator,order_operator,group_operator),
            'pagesize': pagesize,
            'offset': offset,
            'queryused': json.dumps(es_query).replace('\"', "'"),
            'total': r['hits']['total'],
            'records': records,
        }

        return result
'''