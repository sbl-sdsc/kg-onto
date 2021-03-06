#!/usr/bin/env python
# coding: utf-8

# # Convert BioPortal Ontology to node and relationship files

def parse_bioportal_csv(config):
    import pandas as pd
    import re
    
    # core properties to be extracted from all ontology files
    properties = {'Preferred Label': 'name',  'Preferred Label': 'name', 'Synonyms': 'synonyms', 
                  'Definitions': 'definition', 'Class ID': 'url','Parents': 'parents'}
    
    url = config.query('key == "downloadUrl"').values[0][1]
    curie = config.query('key == "curie"').values[0][1]
    
    # append extra properties  
    config = config[5:]
    for row in config.itertuples():
        properties[row[1]] = row[2]

    #properties.update(extra_properties)
    col_names = list(properties.keys())
    node_properties = ['id'] + list(properties.values())
    node_properties.remove('parents')
    
    # read selected properties
    df = pd.read_csv(url, usecols=col_names, compression='gzip', low_memory=False)
    df.fillna('', inplace=True)
    df.rename(columns=properties, inplace=True)

    # Prepare nodes
    #df['id'] = df['url'].str.rsplit(pat="/|#", n=1, expand=True)
    #df['id'] = curie + ':' + df['id'].str[1]
    df['id'] = df['url'].apply(lambda s: re.split('\W+', s)[-1])
    df['id'] = curie + ':' + df['id']

    nodes = df[node_properties]

    # relationships
    rels = df[['id', 'parents']].copy()

    # expand to-many relationship for parents
    rels.query('parents != ""', inplace=True)
    rels['parents'] = rels['parents'].str.split('|')
    rels = rels.explode('parents')

    rels.rename(columns={'id': 'from'}, inplace=True)
    # rels['to'] = rels['parents'].str.rsplit(pat="/", n=1)
    # rels['to'] = rels['to'].str[1]
    rels['to'] = rels['parents'].apply(lambda s: re.split('\W+', s)[-1])
    
    
    # add a root node, owl#Thing is the root node of ontologies (http://www.w3.org/2002/07/owl#Thing)
    roots = rels.query('to == "owl#Thing"')
    if roots.shape[0] > 0:
        root_df = pd.DataFrame([{'id': curie + ':root', 'name': 'root', 'synonyms': 'root|' + curie + ' root',
                                'definition': 'root node of ' + curie, 'url': ''}])
        nodes = pd.concat([nodes, root_df])
        # replace http://www.w3.org/2002/07/owl#Thing parent with "root", the root of the ontology tree.
        rels['to'] = rels['to'].str.replace('owl#Thing', 'root')
    

    # add curie   
    rels['to'] = curie + ':' + rels['to']

    rels = rels[['from','to']]
    rels = rels.reset_index(drop=True)

    return nodes, rels