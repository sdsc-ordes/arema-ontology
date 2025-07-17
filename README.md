# AREMA Ontology
The AREMA Ontology is first and foremost the controlled vocabulary for the Atlas of Regenerative Materials (AREMA). This repository contains the ontology files, validation scripts, and tools required to maintain, check, and publish the ontology.

The ontology is designed to provide a shared conceptual framework and common vocabulary for describing regenerative materials, buildings, professionals, and related concepts within the AREMA platform. It enables both humans and machines to interpret and exchange information consistently.

## 📚 Purpose of the Ontology
An ontology defines terms, relationships, and structures to describe a particular domain — in this case, regenerative materials. For AREMA, this ontology serves multiple purposes:

### Controlled Vocabulary for the Website
It powers the AREMA front-end by providing a standardized vocabulary for objects and properties that AREMA uses. This ensures that users interact with consistent terms throughout the platform, and allows us to link terms used on the front-end to definitions and relations in the ontology.

### Interoperability and Data Quality
By formalizing the domain knowledge as RDF and SHACL, the ontology supports structured data exchange and integration with external systems, while enabling automated quality checks and re-using existing metadata standards.

## 📂 Repository Structure
```plaintext
AREMA Ontology Repository
├── docs/                # Documentation outputs (placeholder)
├── external/            # External resources (placeholder)
├── LICENSE              # Licensing information
├── README.md            # This file
├── src/
│   ├── ontology/        # The ontology files
│   │   ├── arema-ontology.ttl
│   │   └── README.md    # Additional documentation for the ontology itself
│   └── quality-checks/  # SHACL shapes for validating the ontology
│       ├── shacl-shacl.ttl
│       └── skohub.shacl.ttl
└── tools/
    └── python/          # Python tooling for validation and documentation
        ├── checks/
        │   └── shacl.py
        ├── docs/
        │   └── sparql.py
        └── requirements.txt
```

### Key Components
**src/ontology/**:  
The core ontology in Turtle (.ttl) format.

**src/quality-checks/**:  
SHACL shapes for validating ontology consistency and compatibility with tools like SKOHUB.

**tools/python/**:  
Python scripts for running SHACL checks.

## 🔍 Quality Assurance
We employ SHACL shapes to validate the ontology structure and ensure ongoing data integrity. Scripts in `tools/python/` assist with:

- Running SHACL validation against the ontology.
- Generating documentation from SPARQL queries.

## 🚀 Usage (For Developers / Maintainers)

### Requirements
```bash
pip install -r tools/python/requirements.txt
```

### Run SHACL Checks
```bash
python tools/python/checks/shacl.py
```

## Contact
The Atlas of Regenerative Materials originates as a project from the Chair of Sustainable Construction at ETH Zurich, led by Professor Guillaume Habert.

The project was made possible thanks to the initial support of the Ricola Foundation, and the ETH Domain Open Research Data Program .

For comments, ideas or remarks, please contact shhuber@ethz.ch
