---
id: api_info
title: Understanding the API
sidebar_label: General API Info
---

## `/api/v1/records`
The api endpoint  **/api/v1/records**  allows for specific queries to be submitted.
### Parameters
#### `pagesize`  
Sets the maximum number of results returned by the query.  
#### `offset`  
Used to implement paging within the result set.  
#### `q`  
Specifies the query in ElasticSearch DSL format.  
If not provided defaults to `{"match_all": {}}`.  
More information about the query syntax can be found
at [Elastic Search Query Language Documentation](https://www.elastic.co/guide/en/elasticsearch/reference/6.8/query-dsl.html).  
*Use ES documentation for version `6.8`*

## `/api/v1/records/{identifier}`
The api endpoint **/api/v1/records/{identifier}** retrieves an individual record.  
### Parameters
#### `identifier` *required*
The identifier is used to retrieve a specific record. Generally this would be a record retrieved as part of more general query. 

## `/api/v1/aggregations/{field}`
The api endpoint **/api/v1/aggregations/{field}** retrieves unique values of a given SGCN record field.
### Parameters
#### `field` *required*
The field has to be a property of the record model.  
#### `q`  
Specifies the query in ElasticSearch DSL format.  
If not provided defaults to `{"match_all": {}}`.  
More information about the query syntax can be found
at [Elastic Search Query Language Documentation](https://www.elastic.co/guide/en/elasticsearch/reference/6.8/query-dsl.html).  
*Use ES documentation for version `6.8`*


:::note Programming against the API
When processing an existing result set via a program or script running against the API keep in mind near the bottom of each record returned is a uri field that can be used to access the individual record.
:::