import os
import sys
import logging
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI, BackgroundTasks, HTTPException
from apscheduler.schedulers.background import BackgroundScheduler

from arema.update_service import run_conversion
from arema.scheduler import check_and_update

logger = logging.getLogger("OntologyManager")
logging.basicConfig(level=logging.INFO)


class OntologyManagerState:
    """Simple state container for the ontology manager."""
    
    def __init__(self):
        self.is_updating: bool = False
        self.last_sheet_check_time: datetime = datetime.now(timezone.utc)
        self.last_update_time: Optional[datetime] = None
        self.scheduler: BackgroundScheduler = BackgroundScheduler()


# Application state
state = OntologyManagerState()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan - startup and shutdown."""
    # Startup
    state.last_sheet_check_time = datetime.now(timezone.utc)
    logger.info(f"Starting scheduler - will check for Sheet updates every 5 minutes")
    
    state.scheduler.add_job(lambda: check_and_update(state), 'interval', minutes=5, id='check_updates')
    state.scheduler.start()
    logger.info("Scheduler started")
    
    yield  # Application runs here
    
    # Shutdown
    state.scheduler.shutdown()
    logger.info("Scheduler shutdown")


app = FastAPI(
    title="AREMA Ontology Manager",
    description="API service for managing AREMA ontology conversions with automatic polling",
    version="2.0.0",
    lifespan=lifespan
)


def run_update_task():
    """Background task wrapper for manual update trigger."""
    try:
        run_conversion()
        state.last_update_time = datetime.now(timezone.utc)
    except Exception as e:
        logger.error(f"Update Failed: {str(e)}", exc_info=True)
    finally:
        state.is_updating = False


@app.get("/")
async def root():
    """Service status and scheduler info."""
    return {
        "service": "AREMA Ontology Manager",
        "version": "2.0.0",
        "status": "healthy",
        "updating": state.is_updating,
        "scheduler": {
            "active": state.scheduler.running if hasattr(state.scheduler, 'running') else True,
            "check_interval": "5 minutes",
            "last_sheet_check": state.last_sheet_check_time.isoformat() if state.last_sheet_check_time else None,
            "last_update": state.last_update_time.isoformat() if state.last_update_time else None
        }
    }


@app.put("/update")
async def trigger_update(background_tasks: BackgroundTasks):
    """
    Trigger an ontology update from Google Sheets.
    
    Converts Google Sheets to RDF and uploads to Fuseki triplestore.
    """
    if state.is_updating:
        raise HTTPException(
            status_code=409,
            detail="Update already in progress"
        )

    state.is_updating = True
    background_tasks.add_task(run_update_task)
    return {
        "status": "Update started",
        "message": "Converting Google Sheets to ontology and uploading to Fuseki"
    }