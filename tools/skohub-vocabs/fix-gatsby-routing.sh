#!/bin/bash
# Fix Gatsby routing bug when custom_domain is set in SKOHub
# When custom_domain is configured, Gatsby creates duplicate page-data routes:
# - /page-data/index/ (broken - empty pageContext)
# - /page-data/index.html/ (working - full data)
# This script copies the working data to fix the homepage

set -e

DOCS_DIR="./docs"

echo "Checking for Gatsby routing bug..."

if [ -f "$DOCS_DIR/page-data/index.html/page-data.json" ]; then
    if [ -f "$DOCS_DIR/page-data/index/page-data.json" ]; then
        echo "✓ Fixing Gatsby routing: copying working page-data to index route"
        cp "$DOCS_DIR/page-data/index.html/page-data.json" "$DOCS_DIR/page-data/index/page-data.json"
        echo "✓ Homepage routing fixed"
    else
        echo "⚠ Warning: /page-data/index/ not found, skipping fix"
    fi
else
    echo "⚠ Warning: /page-data/index.html/ not found, skipping fix"
fi
