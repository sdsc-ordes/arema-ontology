"""Ontology update service logic."""
import os
import logging
from datetime import datetime, timezone

from tools.python.converter import csv2ont

logger = logging.getLogger("OntologyUpdateService")


def run_conversion():
    """
    Execute the ontology conversion from Google Sheets.
    
    Raises:
        Exception: If conversion fails
    """
    logger.info("Starting ontology conversion")
    
    # Set environment variable for the script
    os.environ["INPUT_SOURCE"] = "google_sheets"
    
    # Run conversion
    csv2ont.convert_sheets_to_ontology()
    
    logger.info("Ontology conversion completed successfully")
