# AREMA Ontology
The AREMA Ontology is first and foremost the controlled vocabulary for the Atlas of Regenerative Materials (AREMA). This repository contains the ontology files, validation scripts, and tools required to maintain, check, and publish the ontology.

The ontology is designed to provide a shared conceptual framework and common vocabulary for describing regenerative materials, buildings, professionals, and related concepts within the AREMA platform. It enables both humans and machines to interpret and exchange information consistently.

## 📚 Purpose of the Ontology
An ontology defines terms, relationships, and structures to describe a particular domain — in this case, regenerative materials. For AREMA, this ontology serves multiple purposes:

### Controlled Vocabulary for the Website
It powers the AREMA front-end by providing a standardized vocabulary for objects and properties that AREMA uses. This ensures that users interact with consistent terms throughout the platform, and allows us to link terms used on the front-end to definitions and relations in the ontology.

### Interoperability and Data Quality
By formalizing the domain knowledge as RDF and SHACL, the ontology supports structured data exchange and integration with external systems, while enabling automated quality checks and re-using existing metadata standards.

## 🏗️ Architecture

The AREMA ontology system consists of three main components:

1. **Ontology Manager API** (FastAPI) - Converts Google Sheets to RDF and manages updates
2. **Apache Fuseki** - SPARQL endpoint and triplestore
3. **SKOHub Vocabs** - Static site generator for human-readable vocabulary browser

### Workflow
```
Google Sheets → Ontology Manager → Fuseki (SPARQL) → GitHub → SKOHub → Static Site
```

The ontology manager fetches data from Google Sheets, converts it to SKOS/RDF format, uploads to Fuseki, and the changes are published via SKOHub to https://ontology.atlas-regenmat.ch/

## 📂 Repository Structure
```plaintext
arema-ontology/
├── docs/                        # SKOHub-generated static site
├── src/
│   ├── arema/                   # Core utility modules
│   │   └── sheets_utils.py      # Google Sheets API utilities
│   ├── server/                  # FastAPI service
│   │   └── main.py              # API endpoints and scheduler
│   ├── ontology/                # Generated ontology files
│   │   └── AREMA-ontology.ttl   # Main ontology (auto-generated)
│   └── quality-checks/          # SHACL validation shapes
│       ├── shacl-shacl.ttl
│       └── skohub.shacl.ttl
├── tools/
│   ├── fuseki/                  # Fuseki configuration
│   │   ├── config.ttl           # Fuseki assembler config
│   │   ├── data/                # TDB2 database storage
│   │   └── docker-compose.yml   # Standalone Fuseki setup
│   ├── python/
│   │   ├── converter/           # Google Sheets → RDF converter
│   │   │   └── csv2ont.py
│   │   └── checks/              # Validation scripts
│   │       └── shacl.py
│   └── skohub-vocabs/           # Custom SKOHub configuration
├── .github/
│   └── workflows/
│       └── docs.yaml            # CI/CD for SKOHub builds
├── Dockerfile                   # Container definition
├── docker-compose.yml           # Multi-service orchestration
├── pyproject.toml               # Python dependencies
└── uv.lock                      # Locked dependencies
```

### Key Components

**src/server/main.py**  
FastAPI service that manages ontology conversions and updates. Provides REST API endpoints for triggering updates and checking status.

**src/arema/**  
Core utility modules for git operations and file management.

**tools/python/converter/csv2ont.py**  
Converts Google Sheets data to SKOS/RDF format with support for:
- Multilingual labels (en/de/fr/it)
- QUDT units and symbols
- Hierarchical concept schemes
- Automatic upload to Fuseki

**docker-compose.yml**  
Orchestrates the ontology manager and Fuseki services with proper networking and volume management.

**tools/fuseki/**  
Apache Fuseki SPARQL endpoint configuration with TDB2 storage and union default graph support.

**src/quality-checks/**  
SHACL shapes for validating ontology consistency and SKOHub compatibility.

## 🔍 Quality Assurance

The ontology undergoes multiple validation checks:

- **SHACL Validation**: Ensures structural consistency and conformance to SKOS/QUDT patterns
- **SKOHub Compatibility**: Validates compatibility with the static site generator
- **Automated Testing**: `test.sh` script validates the full workflow

Run validation:
```bash
python tools/python/checks/shacl.py
```

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+ (for local development)
- uv package manager (recommended)
- Google Service Account JSON key file (see below)

### Google Sheets Authentication Setup

The service uses Google Drive API to efficiently check for Sheet modifications:

1. Create a Google Cloud Project and enable the Drive API
2. Create a Service Account and download the JSON key file
3. Place the JSON key as `service_account.json` in the repository root
4. Share your Google Sheet with the service account email (found in the JSON file under `client_email`)
5. Grant the service account "Viewer" permission

### Running the Services

The repository includes a FastAPI service that automatically checks for Google Sheet updates every 5 minutes using the Drive API (no downloads unless the sheet was modified).

```bash
# 1. Copy and configure environment variables
cp .env.dist .env
# Edit .env and set FUSEKI_USERNAME and FUSEKI_PASSWORD

# 2. Place your service_account.json in the repository root

# 3. Start services (Fuseki + Ontology Manager)
docker compose up -d

# 4. Check service health
curl http://localhost:8000/
curl http://localhost:3030/$/ping
```

The ontology manager API runs on `http://localhost:8000` and Fuseki on `http://localhost:3030`.

**Automatic Updates:** The service checks for Google Sheet modifications every 5 minutes using the Drive API. If changes are detected, it automatically converts the data and uploads to Fuseki triplestore.

### API Endpoints

- `GET /` - Service status, health check, and scheduler information (includes last check time and last update time)
- `PUT /update` - Trigger immediate ontology update from Google Sheets
  ```bash
  curl -X PUT http://localhost:8000/update
  ```

### Local Development

```bash
# Install dependencies
uv sync

# Run conversion script directly
uv run tools/python/converter/csv2ont.py

# Run SHACL validation
python tools/python/checks/shacl.py
```

### Testing

```bash
curl http://localhost:8000/
curl http://localhost:3030/$/ping
```

## 📖 Documentation

- **[API_README.md](API_README.md)** - Detailed API documentation and usage examples
- **[AUTOMATION.md](AUTOMATION.md)** - Automation features (see feature branch)
- **Online Vocabulary**: https://ontology.atlas-regenmat.ch/
- **SPARQL Endpoint**: http://localhost:3030/arema/sparql (when running locally)

## 🐳 Docker Configuration

### Environment Variables

Required in `.env`:
```bash
FUSEKI_URL=http://localhost:3030/arema/data
FUSEKI_USERNAME=admin
FUSEKI_PASSWORD=your_secure_password
```

### Ports
- `8000` - Ontology Manager API
- `3030` - Apache Fuseki SPARQL endpoint

### Volumes
- `./src` - Ontology output files
- `./tools/fuseki/data` - Fuseki database persistence
- `./tools/fuseki/config.ttl` - Fuseki configuration

## 🔄 Development Workflow

1. **Edit Google Sheet** - Domain experts update the taxonomy
2. **Trigger Update** - API endpoint or wait for scheduled update
3. **Conversion** - CSV → SKOS/RDF with QUDT units
4. **Upload** - Data uploaded to Fuseki triplestore
5. **Validation** - SHACL checks ensure quality
6. **Publication** - GitHub Actions builds SKOHub static site
7. **Deployment** - Published to https://ontology.atlas-regenmat.ch/

## Contact

The Atlas of Regenerative Materials originates as a project from the Chair of Sustainable Construction at ETH Zurich, led by Professor Guillaume Habert.

The project was made possible thanks to the initial support of the Ricola Foundation, and the ETH Domain Open Research Data Program.

For comments, ideas or remarks, please contact shhuber@ethz.ch
