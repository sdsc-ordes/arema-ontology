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
g.bind("qudt", "http://qudt.org/schema/qudt/")

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
@prefix qudt: <http://qudt.org/schema/qudt/> .

@base <https://w3id.org/arema/ontology/> .

me:MyThesaurus a skos:ConceptScheme ;
    skos:prefLabel "AREMA Ontology"@en ;
    dct:description "AREMA Ontology for building materials, buildings, natural resources, professionals, and technical constructions."@en ;
    vann:preferredNamespaceUri "https://w3id.org/arema/ontology/" ;
    vann:preferredNamespacePrefix "me" ;
    skos:hasTopConcept me:Object, me:Property ;
    skos:prefLabel "AREMA Ontology"@en , "AREMA Ontologie"@de , "Ontologie AREMA"@fr , "Ontologia AREMA"@it ;
    dct:license <https://creativecommons.org/licenses/by/4.0/> .

me:Property a skos:Concept ;
    skos:definition "Properties of building materials."@en ;
    skos:inScheme me:MyThesaurus ;
    skos:prefLabel "Eigenschaft"@de,
        "Property"@en,
        "Propriété"@fr .

me:mechanical a skos:Concept ;
    skos:broader me:Property ;
    skos:definition "Properties of materials that are related to their mechanical behavior, such as strength, elasticity, and durability."@en ;
    skos:inScheme me:MyThesaurus ;
    skos:prefLabel "Mechanisch"@de,
        "Mechanical"@en,
        "Mécanique"@fr .

me:density a skos:Concept ;
    skos:broader me:mechanical ;
    skos:definition "Density of a material, defined as its mass per unit volume."@en ;
    skos:inScheme me:MyThesaurus ;
    qudt:unit qudt:KilogramPerCubicMeter ;
    skos:prefLabel "Dichte"@de,
        "Density"@en,
        "Densité"@fr .

me:compressiveStrength a skos:Concept ;
    skos:broader me:mechanical ;
    skos:definition "The ability of a material to withstand axial loads without failure."@en ;
    skos:inScheme me:MyThesaurus ;
    qudt:unit qudt:MegaPascal
    skos:prefLabel "Druckfestigkeit"@de,
        "Compressive Strength"@en,
        "Résistance à la Compression"@fr .



me:tensileStrength a skos:Concept ;
    skos:broader me:mechanical ;
    skos:definition "The ability of a material to withstand tensile (pulling) forces without failure."@en ;
    skos:inScheme me:MyThesaurus ;
    skos:prefLabel "Zugfestigkeit"@de,
        "Tensile Strength"@en,
        "Résistance à la Traction"@fr .
        
me:youngsModulus a skos:Concept ;
    skos:broader me:mechanical ;
    skos:definition "A measure of the stiffness of a material, defined as the ratio of stress to strain in the linear elastic region."@en ;
    skos:inScheme me:MyThesaurus ;
    skos:prefLabel "E-Modul"@de,
        "Young's Modulus"@en,
        "Module d'élasticité"@fr .

me:hygrothermal a skos:Concept ;
    skos:broader me:Property ;
    skos:definition "Properties of materials related to their moisture and thermal behavior, such as thermal conductivity and moisture permeability."@en ;
    skos:inScheme me:MyThesaurus ;
    skos:prefLabel "Hygrothermisch"@de,
        "Hygrothermal"@en,
        "Hygrothermique"@fr .

me:thermalConductivity a skos:Concept ;
    skos:broader me:hygrothermal ;
    skos:definition "The ability of a material to conduct heat, defined as the amount of heat that passes through a unit area of the material per unit time for a given temperature difference."@en ;
    skos:inScheme me:MyThesaurus ;
    skos:prefLabel "Wärmeleitfähigkeit"@de,
        "Thermal Conductivity"@en,
        "Conductivité Thermique"@fr .

me:thermalCapacity a skos:Concept ;
    skos:broader me:hygrothermal ;
    skos:definition "The ability of a material to store thermal energy, defined as the amount of heat required to change the temperature of a unit mass of the material by one degree Celsius."@en ;
    skos:inScheme me:MyThesaurus ;
    skos:prefLabel "Wärmekapazität"@de,
        "Thermal Capacity"@en,
        "Capacité Thermique"@fr .

me:watervaporDiffusionResistance a skos:Concept ;
    skos:broader me:hygrothermal ;
    skos:definition "The resistance of a material to the diffusion of water vapor, defined as the ratio of the water vapor pressure difference across the material to the water vapor flux through the material."@en ;
    skos:inScheme me:MyThesaurus ;
    skos:prefLabel "Wasserdampfdiffusionswiderstand"@de,
        "Water vapor Diffusion Resistance"@en,
        "Résistance à la Diffusion de la Vapeur d'Eau"@fr .

me:moistureBufferingValue a skos:Concept ;
    skos:broader me:hygrothermal ;
    skos:definition "The ability of a material to buffer changes in moisture content, defined as the ratio of the change in moisture content to the change in relative humidity."@en ;
    skos:inScheme me:MyThesaurus ;
    skos:prefLabel "Feuchtepufferwert"@de,
        "Moisture Buffering Value"@en,
        "Valeur de Tampon d'Humidité"@fr .

me:porosity a skos:Concept ;
    skos:broader me:hygrothermal ;
    skos:definition "The ratio of the volume of voids in a material to the total volume of the material, expressed as a percentage."@en ;
    skos:inScheme me:MyThesaurus ;
    skos:prefLabel "Porosität"@de,
        "Porosity"@en,
        "Porosité"@fr .

me:effusivity a skos:Concept ;
    skos:broader me:hygrothermal ;
    skos:definition "A measure of a material's ability to exchange heat with its environment, defined as the square root of the product of thermal conductivity and volumetric heat capacity."@en ;
    skos:inScheme me:MyThesaurus ;
    skos:prefLabel "Effusivität"@de,
        "Effusivity"@en,
        "Effusivité"@fr .

me:waterContentAt80Percent a skos:Concept ;
    skos:broader me:hygrothermal ;
    skos:definition "The water content of a material at 80% relative humidity, expressed as a percentage of the dry mass of the material."@en ;
    skos:inScheme me:MyThesaurus ;
    skos:prefLabel "Wassergehalt bei 80% relativer Luftfeuchte"@de,
        "Water Content at 80% Relative Humidity"@en,
        "Teneur en Eau à 80% d'Humidité Relative"@fr .

me:freeSaturation a skos:Concept ;
    skos:broader me:hygrothermal ;
    skos:definition "The maximum amount of water that a material can absorb without any free water present, expressed as a percentage of the dry mass of the material."@en ;
    skos:inScheme me:MyThesaurus ;
    skos:prefLabel "Freie Sättigung"@de,
        "Free Saturation"@en,
        "Saturation Libre"@fr .

me:acoustic a skos:Concept ;
    skos:broader me:Property ;
    skos:definition "Properties of materials related to their acoustic behavior, such as sound absorption and sound insulation."@en ;
    skos:inScheme me:MyThesaurus ;
    skos:prefLabel "Akustisch"@de,
        "Acoustic"@en,
        "Acoustique"@fr .

me:absorptionCoefficientAt500Hz a skos:Concept ;
    skos:broader me:acoustic ;
    skos:definition "The sound absorption coefficient of a material at 500 Hz, defined as the ratio of the sound energy absorbed by the material to the total sound energy incident on the material."@en ;
    skos:inScheme me:MyThesaurus ;
    skos:prefLabel "Absorptionskoeffizient bei 500 Hz"@de,
        "Absorption Coefficient at 500 Hz"@en,
        "Coefficient d'Absorption à 500 Hz"@fr .
    
me:fireResistance a skos:Concept ;
    skos:broader me:Property ;
    skos:definition "The ability of a material to withstand fire or heat without significant degradation or failure."@en ;
    skos:inScheme me:MyThesaurus ;
    skos:prefLabel "Brandwiderstand"@de,
        "Fire Resistance"@en,
        "Résistance au Feu"@fr .

me:reactionToFireClassDINEN135011 a skos:Concept ;
    skos:broader me:fireResistance ;
    skos:definition "The classification of a material's reaction to fire according to the DIN EN 13501-1 standard, which assesses the fire performance of construction products."@en ;
    skos:inScheme me:MyThesaurus ;
    skos:prefLabel "Reaktion auf Feuer Klasse DIN EN 13501-1"@de,
        "Reaction to Fire Class DIN EN 13501-1"@en,
        "Classe de Réaction au Feu DIN EN 13501-1"@fr .

me:interventionType a skos:Concept ;
    skos:broader me:Property ;
    skos:definition "The status of a building or construction, indicating whether it is new, existing, or under renovation."@en ;
    skos:example "New, Renovation"@en , "Neu, Umbau"@de, "Neuf, Rénovation"@fr ;
    skos:inScheme me:MyThesaurus ;
    skos:prefLabel "Art der Massnahme"@de,
        "Intervention Type"@en,
        "Type d'Intervention"@fr .

"""

# Parse the static Turtle into your existing graph
g.parse(data=static_turtle, format="turtle")

# Save to Turtle
g.serialize("./src/ontology/sheet-ontology.ttl", format="turtle")
