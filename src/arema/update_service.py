"""Ontology update service logic."""
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
import requests

from tools.python.converter import csv2ont
from tools.python.checks import shacl

logger = logging.getLogger("OntologyUpdateService")

# Paths
ROOT_DIR = Path(__file__).parent.parent.parent
SHAPES_FILE = ROOT_DIR / "src" / "quality-checks" / "skohub.shacl.ttl"


def create_github_release():
    """
    Create a GitHub release with the ontology file as an asset.
    
    If a release already exists for today, it will be deleted and recreated.
    
    Returns:
        bool: True if release was created successfully
    """
    github_token = os.getenv("GITHUB_TOKEN")
    github_repo = os.getenv("GITHUB_REPOSITORY", "sdsc-ordes/arema-ontology")
    
    if not github_token:
        logger.warning("GITHUB_TOKEN not set - skipping release creation")
        return False
    
    # Create release tag based on date only (overwrites releases on same day)
    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    tag_name = f"ontology-v{date_str}"
    
    # Create release
    release_url = f"https://api.github.com/repos/{github_repo}/releases"
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    release_data = {
        "tag_name": tag_name,
        "name": f"Ontology Update {date_str}",
        "body": f"Automated ontology update from Google Sheets\n\nGenerated: {datetime.now(timezone.utc).isoformat()}",
        "draft": False,
        "prerelease": False
    }
    
    try:
        # Check if release already exists and delete it
        existing_release_url = f"https://api.github.com/repos/{github_repo}/releases/tags/{tag_name}"
        existing_response = requests.get(existing_release_url, headers=headers)
        
        if existing_response.status_code == 200:
            logger.info(f"Found existing release for {tag_name}, deleting...")
            existing_release = existing_response.json()
            delete_url = f"https://api.github.com/repos/{github_repo}/releases/{existing_release['id']}"
            requests.delete(delete_url, headers=headers)
            
            # Also delete the tag
            tag_delete_url = f"https://api.github.com/repos/{github_repo}/git/refs/tags/{tag_name}"
            requests.delete(tag_delete_url, headers=headers)
            logger.info("Previous release and tag deleted")
        
        logger.info(f"Creating GitHub release {tag_name}...")
        response = requests.post(release_url, json=release_data, headers=headers)
        response.raise_for_status()
        release = response.json()
        
        # Upload ontology file as release asset
        upload_url = release["upload_url"].replace("{?name,label}", "")
        with open(csv2ont.TTL_PATH, "rb") as f:
            asset_response = requests.post(
                f"{upload_url}?name=AREMA-ontology.ttl",
                data=f,
                headers={
                    **headers,
                    "Content-Type": "text/turtle"
                }
            )
            asset_response.raise_for_status()
        
        logger.info(f"✅ Release created: {release['html_url']}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create GitHub release: {e}")
        return False


def run_conversion():
    """
    Execute the ontology conversion from Google Sheets.
    
    This function:
    1. Converts Google Sheets data to RDF/TTL format
    2. Validates the resulting graph using SHACL
    3. Uploads to local Fuseki instance
    4. Creates a GitHub Release (triggers docs generation)
    
    Raises:
        Exception: If conversion or validation fails
    """
    logger.info("Starting ontology conversion from Google Sheets")
    
    # Step 1: Convert Google Sheets to RDF/TTL
    csv2ont.convert_sheets_to_ontology()
    logger.info(f"✅ Ontology converted and saved to {csv2ont.TTL_PATH}")
    
    # Step 2: Validate the resulting graph using SHACL
    logger.info("Validating ontology with SHACL shapes...")
    is_valid = shacl.run_shacl_validation(
        str(csv2ont.TTL_PATH), 
        str(SHAPES_FILE)
    )
    
    if not is_valid:
        logger.error("Ontology validation failed: graph does not conform to SHACL shapes")
        raise Exception("Ontology validation failed: resulting graph is not valid")
    
    logger.info("✅ Ontology validation passed")
    
    # Step 3: Upload to local Fuseki instance
    logger.info("Uploading validated ontology to local Fuseki...")
    upload_success = csv2ont.upload_to_fuseki(
        str(csv2ont.TTL_PATH),
        os.getenv("FUSEKI_URL"),
        os.getenv("FUSEKI_USERNAME"),
        os.getenv("FUSEKI_PASSWORD"),
        os.getenv("GRAPH_URI", "https://ontology.atlas-regenmat.ch/")
    )
    
    if not upload_success:
        logger.warning("Upload to Fuseki was skipped or failed")
    else:
        logger.info("✅ Successfully uploaded to local Fuseki")
    
    # Step 4: Create GitHub release (triggers docs generation workflow)
    if create_github_release():
        logger.info("✅ GitHub release created - this will trigger documentation generation")
    else:
        logger.warning("Release creation skipped - ontology updated locally only")
