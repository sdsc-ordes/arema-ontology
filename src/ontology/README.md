# AREMA Ontology

This directory contains generated ontology files that are **not committed to git**. The ontology is only stored as GitHub Release assets.

## 📥 Where to Find the Ontology

The latest version of the AREMA ontology can be downloaded from:
- **GitHub Releases**: [https://github.com/sdsc-ordes/arema-ontology/releases](https://github.com/sdsc-ordes/arema-ontology/releases)
- Each release contains `AREMA-ontology.ttl` as an asset
- Releases are tagged with date: `ontology-vYYYYMMDD`

## 🔍 How to Query the Ontology

The ontology is loaded into a local Apache Jena Fuseki SPARQL endpoint:

- **SPARQL Query Endpoint**: `http://localhost:3030/arema/query`
- **SPARQL Update Endpoint**: `http://localhost:3030/arema/update`
- **Graph URI**: `https://ontology.atlas-regenmat.ch/`

Example SPARQL query:
```sparql
SELECT ?concept ?label
WHERE {
  GRAPH <https://ontology.atlas-regenmat.ch/> {
    ?concept a skos:Concept ;
             skos:prefLabel ?label .
  }
}
LIMIT 10
```

## ✏️ How to Edit the Ontology

The ontology is generated from Google Sheets:

- **Google Sheets**: [AREMA Ontology Data](https://docs.google.com/spreadsheets/d/1RL6Y120_H9-yD8x52eZO44S2iLQpLoZHitcExHsPfPs/edit)
- Edit the sheets to add/modify concepts, labels, and definitions
- Trigger an update via: `curl -X PUT http://localhost:8000/update` (Or wait 5 minutes for the auto-update script to kick in)
- The system will automatically validate, upload to Fuseki, and create a new release

## 📚 Documentation

Human-readable documentation is generated from the ontology and published at:

- **Documentation Website**: [https://sdsc-ordes.github.io/arema-ontology/](https://sdsc-ordes.github.io/arema-ontology/)
- Documentation is automatically updated when a new release is created

## 🔄 Update Process

1. Edit data in Google Sheets
2. POST to `/update` endpoint
3. System converts sheets → validates SHACL → uploads to Fuseki → creates GitHub Release
4. GitHub Actions generates documentation from release
5. Documentation is published to GitHub Pages
