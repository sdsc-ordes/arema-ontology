import pandas as pd
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import SKOS, RDF

# === CONFIG ===
BASE_URI = "http://example.org/taxonomy/"
ME = Namespace(BASE_URI)

sheet_id = "1RL6Y120_H9-yD8x52eZO44S2iLQpLoZHitcExHsPfPs"
objects_gid = "1120751986"     # your objects sheet gid
properties_gid = "373147482"   # replace with your properties sheet gid

# === HELPERS ===
def to_camel_case(s: str) -> str:
    """Turn a label into CamelCase suitable for an IRI fragment."""
    if pd.isna(s):
        return None
    parts = ''.join(c if c.isalnum() or c.isspace() else ' ' for c in str(s)).split()
    return ''.join(p.capitalize() for p in parts)

def add_concept_from_row(g, row, is_property=False):
    """Add SKOS Concept triples from a sheet row."""
    camel_name = to_camel_case(row['s'])
    if not camel_name:
        return
    concept_uri = URIRef(BASE_URI + camel_name)

    g.add((concept_uri, RDF.type, SKOS.Concept))
    g.add((concept_uri, SKOS.inScheme, ME.MyThesaurus))

    # Labels
    if pd.notna(row.get('enLabel')):
        g.add((concept_uri, SKOS.prefLabel, Literal(row['enLabel'], lang='en')))
    if pd.notna(row.get('deLabel')):
        g.add((concept_uri, SKOS.prefLabel, Literal(row['deLabel'], lang='de')))
    if pd.notna(row.get('frLabel')):
        g.add((concept_uri, SKOS.prefLabel, Literal(row['frLabel'], lang='fr')))
    if pd.notna(row.get('itLabel')):
        g.add((concept_uri, SKOS.prefLabel, Literal(row['itLabel'], lang='it')))

    # Definitions
    if pd.notna(row.get('enDefinition')):
        g.add((concept_uri, SKOS.definition, Literal(row['enDefinition'], lang='en')))
    if pd.notna(row.get('deDefinition')):
        g.add((concept_uri, SKOS.definition, Literal(row['deDefinition'], lang='de')))
    if pd.notna(row.get('frDefinition')):
        g.add((concept_uri, SKOS.definition, Literal(row['frDefinition'], lang='fr')))
    if pd.notna(row.get('itDefinition')):
        g.add((concept_uri, SKOS.definition, Literal(row['itDefinition'], lang='it')))

    # Broader relationships
    if pd.notna(row.get('sub-entity level')):
        parent_camel = to_camel_case(row['sub-entity level'])
        if parent_camel:
            g.add((concept_uri, SKOS.broader, URIRef(BASE_URI + parent_camel)))
    if pd.notna(row.get('entity')):
        parent_camel = to_camel_case(row['entity'])
        if parent_camel:
            g.add((concept_uri, SKOS.broader, URIRef(BASE_URI + parent_camel)))

    # Extra fields for properties
    if is_property:
        if pd.notna(row.get('symbol')):
            g.add((concept_uri, ME.symbol, Literal(row['symbol'])))
        if pd.notna(row.get('unit')):
            g.add((concept_uri, ME.unit, Literal(row['unit'])))

# === MAIN ===
# Init graph
g = Graph()
g.bind("rdfs", "http://www.w3.org/2000/01/rdf-schema#")
g.bind("me", BASE_URI)
g.bind("brick", "https://w3id.org/brick#")
g.bind("ifc", "https://standards.buildingsmart.org/IFC/DEV/IFC4/ADD2_TC1/OWL#")
g.bind("owl", "http://www.w3.org/2002/07/owl#")
g.bind("skos", "http://www.w3.org/2004/02/skos/core#")
g.bind("xsd", "http://www.w3.org/2001/XMLSchema#")
g.bind("dct", "http://purl.org/dc/terms/")
g.bind("vann", "http://purl.org/vocab/vann/")
g.bind("qudt", "http://qudt.org/schema/qudt/")

# Static ontology metadata
ontology_metadata = """
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix me: <http://example.org/taxonomy/> .
@prefix brick: <https://w3id.org/brick#> .
@prefix ifc: <https://standards.buildingsmart.org/IFC/DEV/IFC4/ADD2_TC1/OWL#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix dct: <http://purl.org/dc/terms/> .
@prefix vann: <http://purl.org/vocab/vann/> .

@base <https://w3id.org/arema/ontology/> .

me:MyThesaurus a skos:ConceptScheme ;
    skos:prefLabel "AREMA Ontology"@en ;
    dct:description "AREMA Ontology for building materials, buildings, natural resources, professionals, and technical constructions."@en ;
    vann:preferredNamespaceUri "https://w3id.org/arema/ontology/" ;
    vann:preferredNamespacePrefix "me" ;
    skos:hasTopConcept me:Object, me:Property ;
    skos:prefLabel "AREMA Ontology"@en ,
                   "AREMA Ontologie"@de ,
                   "Ontologie AREMA"@fr ,
                   "Ontologia AREMA"@it ;
    dct:license <https://creativecommons.org/licenses/by/4.0/> .
"""

# Inject into the graph
g.parse(data=ontology_metadata, format="turtle")

# Load objects sheet
objects_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={objects_gid}"
df_objects = pd.read_csv(objects_url)

for _, row in df_objects.iterrows():
    add_concept_from_row(g, row, is_property=False)

# Load properties sheet
properties_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={properties_gid}"
df_properties = pd.read_csv(properties_url)

for _, row in df_properties.iterrows():
    add_concept_from_row(g, row, is_property=True)

# Serialize all concepts to one TTL
g.serialize("./src/ontology/arema-ontology.ttl", format="turtle")
