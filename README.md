# kg-onto

kg-onto converts Ontologies into Node, Relationship, and Metadata files for import into Property Graph database systems.

The current version converts biomedical ontologies from [BioPortal](https://bioportal.bioontology.org/).

BioPortal hosts more than 900 ontologies from the biomedical domain. Note, while the majority of ontologies in BioPortal are freely available, some ontologies have access restrictions or data use agreements and are not directly available from BioPortal, e.g., SNOWMED CT.

## Features
* Automated conversion process - no programming required
* A mapping file is used to specify the ontology and properties to be exported
* Both ontology classes and their properties are exported into data files
* Data types of properties are inferred
* The data files are property graph database system agnostic

## Overview
The conversion of an ontology requires the following steps:
1. Identify an ontology of interest from BioPortal
2. Create a mapping file for the ontology
3. Run kg-onto to convert the ontology into data and metadata files
4. Run [kg-import](https://github.com/sbl-sdsc/kg-import) to import the ontologies into a Property Graph Database

## Mapping file
A mapping file includes the name of the ontology, the BioPortal download link, and an optional selection of properties to be included in the output file. The mapping file is a csv file with the following key-value pairs:


```
key,value
name,<name of ontology>
downloadUrl,<download link from BioPortal in csv format>
curie,<compact URI for ontology from Identifiers.org>
nodeFilename,<name of the node property file>
relationshipFilename,<name of the relationship property file>
originalPropertyName-1,<new name for property>
...
originalPropertyName-n,<new name for property>
```

Below is an example of a mapping file for the Chemical Entities of Biological Interest (ChEBI) Ontology:
```
key,value
name,Chemical Entities of Biological Interest Ontology
downloadUrl,https://data.bioontology.org/ontologies/CHEBI/download?apikey=8b5b7825-538d-40e0-9e9e-5ab9274a9aeb&download_format=csv
curie,chebi
nodeFilename,Compound_chebi-v207.csv
relationshipFilename,Compound-IS_A-Compound_chebi-v207.csv
http://purl.obolibrary.org/obo/chebi/formula,formula
http://purl.obolibrary.org/obo/chebi/inchikey,inchiKey
http://purl.obolibrary.org/obo/chebi/inchi,inchi
http://purl.obolibrary.org/obo/chebi/mass,mass
```

The node filename specifies the Node label, e.g., `Compound`, and the relationship filename specifies the Relationship type, e.g. `Compound-IS_A-Compound`. A postfix, e.g., `chebi-v207`, can be added to distinguish different sources, versions, or download dates. The kg-import project describes the [file naming conventions](https://github.com/sbl-sdsc/kg-import#naming-conventions) used for Node Labels, Relationship Types, and Properties. By following these conventions, the data files can be directly imported into Property Graphs with the [kg-import tool](https://github.com/sbl-sdsc/kg-import).

By default, kg-onto includes the node properties: id, name, synonymes, definition, and url for each class in the ontology. Additional properties can be added by specifying additional key-value pairs of `originalPropertyName,newPropertyName`. For the ChEBI ontology, four properties (formula, inchiKey, inchi, and mass) have been added.

More examples of mapping files are available in the `mappings` directory.


