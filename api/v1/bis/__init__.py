import json
from api import api

# define constaints

DESCRIPTION = """
This collection of API endpoints serves Taxomomic Information Registry (TIR)
record documents in the form of a paginated list or a single record lookup by identifier.
Additionally, it provides the ability to write custom queries following the Elasticsearch
query DSL specifications. (https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl.html)
"""

ELASTIC_INDEX = 'bis_pipeline__pipeline_result__sgcn'
DEFAULT_ERROR_MESSAGE = 'Error! Something went wrong while processing this TIR request.'

NS = api.namespace('TIR', description='Taxonomic Information Registry', path="/api/v1")

UNIT_SCHEMA = {
  "$schema": "http://json-schema.org/draft-04/schema#",
    "taxonomic_category": {"type": "string"},
    "state": {"type": "string"},
    "record_processed": {"type": "string"},
    "source_file_date": {"type": "string"},
    "source_file_url": {"type": "string"},
    "year": {"type": "string"},
    "historic_list": {"type": "boolean"},
    "itis_override_id": {"type": ["string"]},
    "scientificname": {"type": "string"},
    "submitted_scientificname": {"type": "string"},
    "taxonomicrank": {"type": "string"},
    "taxonomic_authority_url": {"type": "string"},
    "match_method": {"type": "string"},
    "commonname": {"type": "string"},
    "class_name": {"type": "string"},
    "nationallist": {"type": "boolean"},

    "metadata" : { "type": "object",
        "properties": {
           "uri " : {"type": "string"},
           "run_id" : {"type": "string"},
           "record_id" : {"type": "string"}
        }
    },

  "additionalProperties": False
}

#UNIT_META_SCHEMA = {"$schema": "http://json-schema.org/draft-07/schema#","type": "object","required": ["metadata"],"properties": {"metadata": METADATA_SCHEMA}}
UNIT_META_SCHEMA = {"properties" : UNIT_SCHEMA}

SINGLE_UNIT_MODEL = NS.schema_model('TIR Record' , UNIT_META_SCHEMA)

# UNIT_META_SCHEMA = {"$schema": "http://json-schema.org/draft-07/schema#", "type": "object", "required": ["id", "data", "run_id", "created_date", "row_id"], "properties": {"id": {"$id": "#/properties/id", "type": "string", "title": "The Id Schema", "default": "", "examples": ["116849"], "pattern": "^(.*)$"}, "data": {"$id": "#/properties/data", "type": "object", "title": "The Source_data Schema"}, "run_id": {"$id": "#/properties/run_id", "type": "string", "title": "The Run_id Schema", "default": "", "examples": [
#     "aad3651e-f4e6-11e9-94aa-023f40fa784e"], "pattern": "^(.*)$"}, "created_date": {"$id": "#/properties/created_date", "type": "string", "title": "The Created_date Schema", "default": "", "examples": ["2019-10-22 16:12:11.236185"], "pattern": "^(.*)$"}, "row_id": {"$id": "#/properties/row_id", "type": "string", "title": "The Row_id Schema", "default": "", "examples": ["683065"], "pattern": "^(.*)$"}}}

#SINGLE_UNIT_MODEL = NS.schema_model('USNVC Unit' , UNIT_META_SCHEMA)
