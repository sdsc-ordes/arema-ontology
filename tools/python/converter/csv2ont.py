import os
import pandas as pd
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import SKOS, RDF
from dotenv import load_dotenv
import requests
from inflection import camelize
from pathlib import Path

# === BASE DIRS ===
SCRIPT_DIR = Path(__file__).parent      # tools/python/converter
ROOT_DIR = SCRIPT_DIR.parent.parent.parent  # ../../.. from converter -> root of repo
ONTOLOGY_DIR = ROOT_DIR / "src" / "ontology"
ONTOLOGY_DIR.mkdir(parents=True, exist_ok=True)

TTL_PATH = ONTOLOGY_DIR / "AREMA-ontology.ttl"

# === CONFIG ===
BASE_URI = "https://ontology.atlas-regenmat.ch/"
ME = Namespace(BASE_URI)
QUDT = Namespace("http://qudt.org/schema/qudt/")

def add_concept_from_row(g, row, is_property=False):
    """Add SKOS Concept triples from a sheet row."""
    s_value = row['s']
    if pd.isna(s_value):
        return

    cleaned = ''.join(c if c.isalnum() or c.isspace() else ' ' for c in str(s_value))
    camel_name = camelize(cleaned.strip()).replace(' ', '')
    if not camel_name:
        return
    concept_uri = URIRef(BASE_URI + camel_name)

    g.add((concept_uri, RDF.type, SKOS.Concept))
    g.add((concept_uri, SKOS.inScheme, ME.AREMA))

    # Labels
    for lang in ['en', 'de', 'fr', 'it']:
        label_key = f"{lang}Label"
        if pd.notna(row.get(label_key)):
            g.add((concept_uri, SKOS.prefLabel, Literal(row[label_key], lang=lang)))

    # Definitions
    for lang in ['en', 'de', 'fr', 'it']:
        def_key = f"{lang}Definition"
        if pd.notna(row.get(def_key)):
            g.add((concept_uri, SKOS.definition, Literal(row[def_key], lang=lang)))

    # Broader relationships
    for parent_field in ['sub-entity level', 'entity']:
        if pd.notna(row.get(parent_field)):
            parent_value = row[parent_field]
            cleaned_parent = ''.join(c if c.isalnum() or c.isspace() else ' ' for c in str(parent_value))
            parent_camel = camelize(cleaned_parent.strip()).replace(' ', '')
            if parent_camel:
                g.add((concept_uri, SKOS.broader, URIRef(BASE_URI + parent_camel)))

    # Extra fields for properties
    if is_property:
        if pd.notna(row.get('symbol')):
            g.add((concept_uri, QUDT.symbol, Literal(row['symbol'])))
        if pd.notna(row.get('unit')):
            g.add((concept_uri, QUDT.unit, Literal(row['unit'])))

def upload_to_fuseki(file_path, fuseki_url=None, username=None, password=None, graph_uri=None):
    """Upload the generated TTL file to Fuseki database."""
    if not fuseki_url:
        fuseki_url = os.getenv("FUSEKI_UPDATE_URL") or os.getenv("FUSEKI_URL")
    
    if not fuseki_url:
        print("⚠️  Skipping upload: FUSEKI_UPDATE_URL not set.")
        return False
    
    username = username or os.getenv("FUSEKI_USERNAME", "admin")
    password = password or os.getenv("FUSEKI_PASSWORD")
    graph_uri = graph_uri or "https://ontology.atlas-regenmat.ch/"
    
    upload_url = f"{fuseki_url}?graph={graph_uri}"
    
    print(f"📤 Uploading {file_path} to {upload_url}...")
    try:
        with open(file_path, "rb") as f:
            ttl_data = f.read()
        
        response = requests.put(
            upload_url,
            data=ttl_data,
            headers={"Content-Type": "text/turtle"},
            auth=(username, password) if username and password else None
        )
        response.raise_for_status()
        print(f"✅ Upload successful! ({response.status_code})")
        return True
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return False


def convert_sheets_to_ontology():
    """Convert Google Sheets data to SKOS/RDF ontology and upload to Fuseki."""
    load_dotenv()
    FUSEKI_BASE = os.getenv("FUSEKI_URL")
    GRAPH_URI = "https://ontology.atlas-regenmat.ch/"
    USERNAME = os.getenv("FUSEKI_USERNAME")
    PASSWORD = os.getenv("FUSEKI_PASSWORD")

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

    ontology_metadata = """
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix me: <https://ontology.atlas-regenmat.ch/> .
@prefix brick: <https://w3id.org/brick#> .
@prefix ifc: <https://standards.buildingsmart.org/IFC/DEV/IFC4/ADD2_TC1/OWL#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix dct: <http://purl.org/dc/terms/> .
@prefix vann: <http://purl.org/vocab/vann/> .
@prefix qudt: <http://qudt.org/schema/qudt/> .

@base <https://ontology.atlas-regenmat.ch/> .

me:AREMA a skos:ConceptScheme ;
    skos:prefLabel "AREMA Ontology"@en ;
    dct:description "AREMA Ontology for building materials, buildings, natural resources, professionals, and technical constructions."@en ;
    vann:preferredNamespaceUri "https://ontology.atlas-regenmat.ch/" ;
    vann:preferredNamespacePrefix "me" ;
    skos:hasTopConcept me:Object, me:Property ;
    skos:prefLabel "AREMA Ontology"@en ,
                   "AREMA Ontologie"@de ,
                   "Ontologie AREMA"@fr ,
                   "Ontologia AREMA"@it ;
    dct:license <https://creativecommons.org/licenses/by/4.0/> .
"""
    g.parse(data=ontology_metadata, format="turtle")

    # Load Google Sheets
    sheet_id = os.getenv("GOOGLE_SHEET_ID", "1RL6Y120_H9-yD8x52eZO44S2iLQpLoZHitcExHsPfPs")
    objects_gid = os.getenv("GOOGLE_SHEET_OBJECTS_GID", "1120751986")
    properties_gid = os.getenv("GOOGLE_SHEET_PROPERTIES_GID", "373147482")
    objects_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={objects_gid}"
    df_objects = pd.read_csv(objects_url)
    for _, row in df_objects.iterrows():
        add_concept_from_row(g, row, is_property=False)

    properties_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={properties_gid}"
    df_properties = pd.read_csv(properties_url)
    for _, row in df_properties.iterrows():
        add_concept_from_row(g, row, is_property=True)

    # Serialize TTL to file
    TTL_PATH = ONTOLOGY_DIR / "AREMA-ontology.ttl"
    g.serialize(TTL_PATH, format="turtle")
    print(f"✅ Generated ontology file: {TTL_PATH}")

    # === UPLOAD TO FUSEKI ===
    upload_to_fuseki(TTL_PATH, FUSEKI_BASE, USERNAME, PASSWORD, GRAPH_URI)


if __name__ == "__main__":
    convert_sheets_to_ontology()
