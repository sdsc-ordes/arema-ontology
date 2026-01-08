"""Ontology update service logic."""
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
import requests

from tools.python.converter import csv2ont

logger = logging.getLogger("OntologyUpdateService")


def create_github_release():
    """
    Create a GitHub release with the ontology file as an asset.
    
    Returns:
        bool: True if release was created successfully
    """
    github_token = os.getenv("GITHUB_TOKEN")
    github_repo = os.getenv("GITHUB_REPOSITORY", "sdsc-ordes/arema-ontology")
    
    if not github_token:
        logger.warning("GITHUB_TOKEN not set - skipping release creation")
        return False
    
    # Create release tag based on timestamp
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    tag_name = f"ontology-v{timestamp}"
    
    # Create release
    release_url = f"https://api.github.com/repos/{github_repo}/releases"
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    release_data = {
        "tag_name": tag_name,
        "name": f"Ontology Update {timestamp}",
        "body": f"Automated ontology update from Google Sheets\n\nGenerated: {datetime.now(timezone.utc).isoformat()}",
        "draft": False,
        "prerelease": False
    }
    
    try:
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
    
    Converts Google Sheets data to RDF/TTL format and creates a GitHub Release.
    The release triggers GitHub Actions which:
    - Downloads the ontology from the release asset
    - Validates using SHACL
    - Generates documentation
    - Deploys to production Fuseki endpoint
    
    Raises:
        Exception: If conversion fails
    """
    logger.info("Starting ontology conversion from Google Sheets")
    
    # Convert Google Sheets to RDF/TTL
    csv2ont.convert_sheets_to_ontology()
    logger.info(f"✅ Ontology converted and saved to {csv2ont.TTL_PATH}")
    
    # Create GitHub release with the ontology file
    if create_github_release():
        logger.info("✅ GitHub release created - this will trigger validation and deployment")
    else:
        logger.warning("Release creation skipped - ontology saved locally only")
