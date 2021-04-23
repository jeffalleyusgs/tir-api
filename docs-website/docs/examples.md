---
id: examples
title: SGCN Examples
sidebar_label: All Examples
---

This document shows some basic query examples for using the SGCN API

:::note Exact match for strings

__What to do__  
For exact match searches on `string` fields use a [Match Phrase](https://www.elastic.co/guide/en/elasticsearch/reference/6.8/query-dsl-match-query-phrase.html) query (example in [single field searches](#single-field-searches)).

__Why__  
We use the [standard analyzer](https://www.elastic.co/guide/en/elasticsearch/reference/6.8/analysis-standard-analyzer.html) for indexing data in Elasticsearch. The standard analyzer indexes `string` properties as [`text` fields](https://www.elastic.co/guide/en/elasticsearch/reference/6.8/text.html). `text` fields break up a string and index each word, they are designed for full-text searches. This can result in unexpected behavior and/or additional results when a user might expect results exactly matching the provided `string`. Use `match_phrase` to get results that match the `string` exactly.

Try these two searches to see the difference:  
```
{"match_phrase" : {"data.match_method" : "Fuzzy Match"}}
```  
```
{"match" : {"data.match_method" : "Fuzzy Match"}}
```

The second query returns 65379 more results because most record's `match_method` contain the word "Match".  
:::

## Sample queries
### Search for records by species common or scientific name
#### Single field searches
Searching for records by common name (returns results for "Peregrine" and "Falcon")
```
{
    "match": {
        "data.common name": "Peregrine Falcon"
    }
}
```
Searching for records with an exact match on "Peregrine falcon"
```
{
    "match_phrase": {
        "data.common name": "Peregrine Falcon"
    }
}
```
For partial word searches use `match_phrase_prefix`, this will search for records with scientific names that contain words starting with "pere"
```
{
    "match_phrase_prefix": {
        "data.scientific name": "pere"
    }
}
```

:::note Unique value searches
To get unique values for a particular record property use the `aggregations` endpoint. 
The endpoint takes a DSL query to filter results just like the `records` endpoint.  
An example use case could be searching for unique `scientific name` values containing "pere". Using the above query returns:
```
{
    "q": "{'match_phrase_prefix': {'data.scientific name': 'pere'}}",
    "buckets": [
        {
            "key": "Falco peregrinus",
            "doc_count": 111
        },
        {
            "key": "Falco peregrinus anatum",
            "doc_count": 18
        },
        {
            "key": "Oenothera perennis",
            "doc_count": 9
        },
        {
            "key": "Lupinus perennis",
            "doc_count": 6
        },
        [...]
    ]
}
```
These might be used for further querying like finding records for matching `Falco peregrinus anatum`.
:::

Match query documentation: https://www.elastic.co/guide/en/elasticsearch/reference/6.8/query-dsl-match-query.html  
Match phrase query documentation: https://www.elastic.co/guide/en/elasticsearch/reference/6.8/query-dsl-match-query-phrase.html  
Match phrase query documentation: https://www.elastic.co/guide/en/elasticsearch/reference/6.8/query-dsl-match-query-phrase-prefix.html

#### Multi field searches
Searching for records with scientific and common names containing "falcon"
```
{
    "multi_match": {
        "query": "falcon",
        "fields": [
            "data.scientific name",
            "data.common name"
        ],
        "operator": "Or"
    }
}
```
A partial match on multiple fields with `match_phrase_prefix` might look like this
```
{
    "multi_match": {
        "query": "falco",
        "type": "phrase_prefix",
        "fields": [
            "data.scientific name",
            "data.common name"
        ],
        "operator": "Or"
    }
}
```
Multi match query documentation: https://www.elastic.co/guide/en/elasticsearch/reference/6.8/query-dsl-multi-match-query.html  
Using Match Phrase in `multi_match` queries: https://www.elastic.co/guide/en/elasticsearch/reference/6.8/query-dsl-multi-match-query.html#type-phrase

### National List records
National List records contain the `taxonomic_authority_url` property. 
```
{
    "exists": {
        "field": "data.taxonomic_authority_url"
    }
}
```
Non-National List records don't have the `taxonomic_authority_url` property.
```
{
    "bool": {
        "must_not": {
            "exists": {
                "field": "data.taxonomic_authority_url"
            }
        }
    }
}
```
Exists query documentation: https://www.elastic.co/guide/en/elasticsearch/reference/6.8/query-dsl-exists-query.html

### Search by state
Searching for records submitted by New Jersey
```
{
    "match_phrase": {
        "data.state": "New Jersey"
    }
}
```
Matching multiple fields, like state and year
```
{
    "bool": {
      "should": [
        { "match": {"data.state": "Florida"}},
        { "match": {"data.year": "2015"}}
      ],
      "minimum_should_match": 2
    }
}
```
Bool query documentation: https://www.elastic.co/guide/en/elasticsearch/reference/6.8/query-dsl-bool-query.html