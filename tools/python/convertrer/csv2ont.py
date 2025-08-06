import pandas as pd
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import SKOS, RDF

sheet_id = "1RL6Y120_H9-yD8x52eZO44S2iLQpLoZHitcExHsPfPs"
gid = "740321531"

export_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

df = pd.read_csv(export_url)
print(df.head()) 

# Create RDF graph
g = Graph()
EX = Namespace("http://example.org/")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
ME = Namespace("http://example.org/taxonomy/")
g.bind("rdfs", "http://www.w3.org/2000/01/rdf-schema#")
g.bind("me", "http://example.org/taxonomy/")
g.bind("brick", "https://w3id.org/brick#")
g.bind("ifc", "https://standards.buildingsmart.org/IFC/DEV/IFC4/ADD2_TC1/OWL#")
g.bind("owl", "http://www.w3.org/2002/07/owl#")
g.bind("skos", "http://www.w3.org/2004/02/skos/core#")
g.bind("xsd", "http://www.w3.org/2001/XMLSchema#")
g.bind("dct", "http://purl.org/dc/terms/")
g.bind("vann", "http://purl.org/vocab/vann/")

# Add concepts to the graph
for _, row in df.iterrows():
    concept = URIRef(row['s'])
    g.add((concept, RDF.type, SKOS.Concept))
    g.add((concept, SKOS.inScheme, ME.MyThesaurus))

    # Labels
    if pd.notna(row['enLabel']):
        g.add((concept, SKOS.prefLabel, Literal(row['enLabel'], lang='en')))
    if pd.notna(row['deLabel']):
        g.add((concept, SKOS.prefLabel, Literal(row['deLabel'], lang='de')))
    if pd.notna(row['frLabel']):
        g.add((concept, SKOS.prefLabel, Literal(row['frLabel'], lang='fr')))
    if pd.notna(row['itLabel']):
        g.add((concept, SKOS.prefLabel, Literal(row['itLabel'], lang='it')))

    # Definitions
    if pd.notna(row['enDefinition']):
        g.add((concept, SKOS.definition, Literal(row['enDefinition'], lang='en')))
    if pd.notna(row['deDefinition']):
        g.add((concept, SKOS.definition, Literal(row['deDefinition'], lang='de')))
    if pd.notna(row['frDefinition']):
        g.add((concept, SKOS.definition, Literal(row['frDefinition'], lang='fr')))
    if pd.notna(row['itDefinition']):
        g.add((concept, SKOS.definition, Literal(row['itDefinition'], lang='it')))

    # Broader relationships
    if pd.notna(row['sub-entity level']):
        g.add((concept, SKOS.broader, URIRef(row['sub-entity level'])))
    if pd.notna(row['entity']):
        g.add((concept, SKOS.broader, URIRef(row['entity'])))


static_turtle = """
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
    skos:hasTopConcept me:BuildingMaterial, me:Building, me:NaturalResource, me:Professional, me:TechnicalConstruction ;
    skos:prefLabel "AREMA Ontology"@en , "AREMA Ontologie"@de , "Ontologie AREMA"@fr , "Ontologia AREMA"@it ;
    dct:license <https://creativecommons.org/licenses/by/4.0/> .

me:BuildingMaterial a skos:Concept ;
    skos:inScheme me:MyThesaurus ;
    skos:prefLabel "Building Materials"@en , "Baustoffe"@de , "Matériaux de construction"@fr , "Materiali da costruzione"@it .

me:Building a skos:Concept ;
    skos:inScheme me:MyThesaurus ;
    skos:prefLabel "Buildings"@en , "Gebäude"@de , "Bâtiments"@fr , "Edifici"@it .

me:NaturalResource a skos:Concept ;
    skos:inScheme me:MyThesaurus ;
    skos:prefLabel "Natural Resources"@en , "Natürliche Ressourcen"@de , "Ressources naturelles"@fr , "Risorse naturali"@it .

me:Professional a skos:Concept ;
    skos:inScheme me:MyThesaurus ;
    skos:prefLabel "Professionals"@en , "Fachleute"@de , "Professionnels"@fr , "Professionisti"@it .

me:TechnicalConstruction a skos:Concept ;
    skos:inScheme me:MyThesaurus ;
    skos:prefLabel "Technical Constructions"@en , "Technische Konstruktionen"@de , "Constructions techniques"@fr , "Costruzioni tecniche"@it ;
    skos:definition "Aspects of construction related to the physical realization of buildings, encompassing structural, thermal, acoustic, and service-related elements."@en .
"""

# Parse the static Turtle into your existing graph
g.parse(data=static_turtle, format="turtle")

# Save to Turtle
g.serialize("./src/ontology/sheet-ontology.ttl", format="turtle")
