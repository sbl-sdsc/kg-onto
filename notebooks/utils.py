#!/usr/bin/env python
# coding: utf-8

# # Convert BioPortal Ontology to node and relationship files

def parse_bioportal_csv(url, extra_properties, curie):
    import pandas as pd
    
    # core properties to be extracted from all ontology files
    properties = {'Preferred Label': 'name',  'Preferred Label': 'name', 'Synonyms': 'synonyms', 'Definitions': 'definition', 'Class ID': 'url','Parents': 'parents'}
    
    # append extra properties
    properties.update(extra_properties)
    col_names = list(properties.keys())
    node_properties = ['id'] + list(properties.values())
    node_properties.remove('parents')
    
    # read selected properties
    df = pd.read_csv(url, usecols=col_names, compression='gzip', low_memory=False)
    df.fillna('', inplace=True)
    df.rename(columns=properties, inplace=True)

    # Prepare nodes
    df['id'] = df['url'].str.rsplit(pat="/", n=1)
    df['id'] = curie + ':' + df['id'].str[1]

    nodes = df[node_properties]

    # relationships
    rels = df[['id', 'parents']].copy()

    # expand to-many relationship for parents
    rels.query('parents != ""', inplace=True)
    rels['parents'] = rels['parents'].str.split('|')
    rels = rels.explode('parents')

    rels.rename(columns={'id': 'from'}, inplace=True)
    rels['to'] = rels['parents'].str.rsplit(pat="/", n=1)
    rels['to'] = rels['to'].str[1]
    
    # replace http://www.w3.org/2002/07/owl#Thing parent with "root", the root of the ontology tree.
    rels['to'] = rels['to'].str.replace('owl#Thing', 'root')

    # add curie   
    rels['to'] = curie + ':' + rels['to']

    rels = rels[['from','to']]

    return nodes, rels