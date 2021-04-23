---
id: data_dictionary
title: Data Dictionary
sidebar_label: Data Dictionary
---
The documentation of the fields is as follows:

**** denotes a field that will be MISSING if NO taxonomic authority was found.

 1.   "id": example "1cff000fe5ebfbe2fb7dd7c453c0f193227ada03",  (Internal DB record identifier.  Should not be searchable)
 2.   "common name": The common name of the species as found in the state SWAP data file
 3.   "scientific name": The scientific name of the species as found in the state SWAP data file
 4.  "taxonomic category": Taxonomic category (optionally) provided in the state SWAP data file. This will be overridden by data matched in the sgcnTaxonomicGroupMappings.json file. If no match is found in the sgcnTaxonomicGroupMappings.json file, whatever data (if provided) in the original SWAP data will be used.
 5.  "state": State where species was recorded in SWAP data
 6.   "sciencebase_item_id": Sciencebase location for state SWAP data
 7.  "record_processed": Date the record was processed by the SGCN pipeline
 8.  "source_file_date": Date associated with the SWAP data file where the species was found
 9.  "source_file_url": Web location of SWAP data for a specific state
 10.   "year": Year that SWAP data was entered for the state (currently 2005 OR 2015)
 11.  "clean_scientific_name": Derived from "scientific name" after cleaning up unrecognizable characters and numbers and other extraneous, unprocessable characters.
 12.  "historic_list": true/false if species was found in the 2005SWAPSpeciesList.txt file
 13.   "itis_override_id": true/null if species was found in the SGCN ITIS Overrides.json file
 14.   "sppin_key": Internal search key.  Should NOT be searchable externally
 15.   "taxogroupings": Transient internal key that will always be null at this point
 16.   ** "scientificname": Populated with the corrected scientific name ONLY IF found in a taxonomic authority (ITIS/WoRMS)
 17.   ** "taxonomicrank": Populated with the corrected taxonomic rank ONLY IF found in a taxonomic authority (ITIS./WoRMS)
 18.   ** "taxonomic_authority_url": Populated with the url associated with the taxonomic authority ONLY IF found (ITIS/WoRMS)
 20.   ** "match_method": The method of scientific name that caused a match in the taxomic authority. Can be one of: "Exact Match", "Fuzzy Match", "Followed Accepted TSN", or "Found multiple matches"
 21.   ** "class_name": The class of the species as designated by the taxonomic authority
 22.   ** "commonname": The correct common name of the species as designated by the taxonomic authority
 23.   "nationallist" : true / false   Designates whether or not this species is on the National List.  If the species has a taxonomic_authority OR the value of "historic_list" is true, then nationallist will be true.
