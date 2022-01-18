#!/usr/bin/env python
# coding: utf-8

# # Create Node and Relationship files from a BioPortal Ontology
# This notebook converts ontology files from [BioPortal](https://bioportal.bioontology.org/) to Node and Relationship files that represent the ontology trees. 
# 
# The Node and Relationship files can be uploaded into a Neo4j Graph Database using the [kg-import](https://github.com/sbl-sdsc/kg-import).

import argparse

def example_score(row):
    characters = 0
    score = 0
    
    for item in row:
        item = str(item)
        characters += len(item)
        # rows with the most complete data score higher
        if item != '':
            score += 1

    # rows with multiple synomyms score highter
    if '|' in row[2]:
        score += 0.5
         
    # shorter rows score higher
    score += len(row)/characters
    return score

def convert_ontology(mapping_filename):
    import os
    import glob
    from pathlib import Path
    import pandas as pd
    from utils import parse_bioportal_csv

    NODE_METADATA = os.getenv('NODE_METADATA', default='../metadata/nodes/')
    RELATIONSHIP_METADATA = os.getenv('RELATIONSHIP_METADATA', default='../metadata/relationships/')                  

    if NODE_METADATA == '../metadata/nodes/':
        os.makedirs(os.path.join(NODE_METADATA), exist_ok=True)

    if RELATIONSHIP_METADATA == '../metadata/relationships/':
        os.makedirs(os.path.join(RELATIONSHIP_METADATA), exist_ok=True)

    NODE_DATA = os.getenv('NODE_DATA', default='../data/nodes/')
    RELATIONSHIP_DATA = os.getenv('RELATIONSHIP_DATA', default='../data/relationships/') 

    if NODE_DATA == '../data/nodes/':
        os.makedirs(os.path.join(NODE_DATA), exist_ok=True)

    if RELATIONSHIP_DATA == '../data/relationships/':
        os.makedirs(os.path.join(RELATIONSHIP_DATA), exist_ok=True)


    config = pd.read_csv(mapping_filename)

    node_filename = config.query('key == "nodeFilename"').values[0][1]
    relationship_filename = config.query('key == "relationshipFilename"').values[0][1]

    #
    # Parse ontology file and create node and relationship dataframes
    #
    nodes, relationships = parse_bioportal_csv(config)
    print('Number of nodes:', nodes.shape[0])
    nodes.head()

    print('Number of relationships:', relationships.shape[0])
    relationships.head()

    # Save data files

    nodes.to_csv(os.path.join(NODE_DATA, node_filename), index=False)
    relationships.to_csv(os.path.join(RELATIONSHIP_DATA, relationship_filename), index=False)


    # Create Metadata files
    #    Pick a consise and representative example for the metadata file
    nodes['score'] = nodes.apply(example_score, axis=1)
    nodes = nodes.sort_values(by='score', ascending=False)
    # pick example from place 50. The top scoring example is often atypical.
    pick = min(50, nodes.shape[0])
    example_row = nodes[50:]
    examples = list(example_row.values[0])


    #    Infer data types
    nodes = nodes.convert_dtypes()

    # Create metadata
    metadata = []
    for node, dtype, exmpl in zip(nodes.columns, nodes.dtypes, examples):
        metadata.append({'property': node, 'type': dtype, 'description': node, 'example': exmpl})
    
    node_metadata = pd.DataFrame(metadata)
    # remove last row ('score')
    node_metadata = node_metadata[:-1]

    metadata = [{'property': 'from', 'type': 'string', 'description': 'Id of source node', 'example': relationships['from'][0]},
            {'property': 'to', 'type': 'string', 'description': 'Id of target node', 'example': relationships['to'][0]}]
    
    relationship_metadata = pd.DataFrame(metadata)

    # Save metadata files
    node_metadata.to_csv(os.path.join(NODE_METADATA, node_filename), index=False)
    relationship_metadata.to_csv(os.path.join(RELATIONSHIP_METADATA, relationship_filename), index=False)
    
    
parser = argparse.ArgumentParser(description='Ontology to CSV')
parser.add_argument('-m', '--mapping', help='ontology mapping file')

args = parser.parse_args()
print('Processing mapping file:', args.mapping)
convert_ontology(args.mapping)
    


