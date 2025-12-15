import os
import logging
import importlib.util
import sys
import hashlib
import subprocess
from datetime import datetime
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from apscheduler.schedulers.background import BackgroundScheduler

# Configuration
SCRIPT_PATH = os.path.join(os.getcwd(), "tools/python/converter/csv2ont.py")
TTL_PATH = "/app/src/ontology/AREMA-ontology.ttl"

app = FastAPI(
    title="AREMA Ontology Manager",
    description="API service for managing AREMA ontology conversions with automatic polling",
    version="2.0.0"
)
logger = logging.getLogger("OntologyManager")
logging.basicConfig(level=logging.INFO)

# Global state
is_updating = False
last_file_hash = None
last_check_time = None
last_update_time = None
scheduler = BackgroundScheduler()


class UpdateRequest(BaseModel):
    mock_mode: bool = False
    auto_commit: bool = True


def get_file_hash(file_path: str) -> str:
    """Calculate SHA256 hash of a file."""
    if not os.path.exists(file_path):
        return None
    
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def git_commit_and_push(file_path: str) -> bool:
    """Commit and push changes to git repository."""
    try:
        # Get GitHub token from environment
        github_token = os.environ.get("GITHUB_TOKEN")
        if not github_token:
            logger.error("GITHUB_TOKEN not set - cannot push to GitHub")
            return False
        
        # Fix git ownership issue for mounted directory
        subprocess.run(["git", "config", "--global", "--add", "safe.directory", "/app"], 
                      cwd="/app", check=False)
        
        # Configure git
        subprocess.run(["git", "config", "user.name", "AREMA Ontology Bot"], 
                      cwd="/app", check=False)
        subprocess.run(["git", "config", "user.email", "ontology@atlas-regenmat.ch"], 
                      cwd="/app", check=False)
        
        # Set remote URL with token for this push only (doesn't affect local config)
        github_url = f"https://x-access-token:{github_token}@github.com/sdsc-ordes/arema-ontology.git"
        
        # Add the file
        result = subprocess.run(["git", "add", file_path], 
                              cwd="/app", capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"Git add failed: {result.stderr}")
            return False
        
        # Check if there are changes to commit
        result = subprocess.run(["git", "diff", "--cached", "--quiet"], 
                              cwd="/app", capture_output=True)
        if result.returncode == 0:
            logger.info("No changes to commit")
            return True
        
        # Commit
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result = subprocess.run(
            ["git", "commit", "-m", f"Auto-update ontology from Google Sheets at {timestamp}"],
            cwd="/app", capture_output=True, text=True
        )
        if result.returncode != 0:
            logger.error(f"Git commit failed: {result.stderr}")
            return False
        
        # Pull latest changes first (rebase to avoid merge commits)
        result = subprocess.run(["git", "pull", "--rebase", github_url, "main"], 
                              cwd="/app", capture_output=True, text=True)
        if result.returncode != 0:
            logger.warning(f"Git pull failed (may not be critical): {result.stderr}")
            # Continue anyway - might just be up to date
        
        # Push using HTTPS with token
        result = subprocess.run(["git", "push", github_url, "HEAD:main"], 
                              cwd="/app", capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"Git push failed: {result.stderr}")
            return False
        
        logger.info(f"Successfully committed and pushed {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"Git operation failed: {str(e)}")
        return False


def run_conversion_logic(mock_mode: bool, auto_commit: bool = True):
    """Execute the ontology conversion script."""
    global is_updating, last_file_hash, last_update_time
    try:
        logger.info(f"Starting Update. Mock Mode: {mock_mode}, Auto-commit: {auto_commit}")
        
        # Set Env Vars for the script
        if mock_mode:
            os.environ["INPUT_SOURCE"] = "local_file"
            os.environ["INPUT_FILE_PATH"] = "/app/data/mock_input.csv"
        else:
            os.environ["INPUT_SOURCE"] = "google_sheets"

        # Check if script exists
        if not os.path.exists(SCRIPT_PATH):
            logger.error(f"Script not found at: {SCRIPT_PATH}")
            return

        # Dynamic Import & Execution
        spec = importlib.util.spec_from_file_location("csv2ont", SCRIPT_PATH)
        csv2ont_module = importlib.util.module_from_spec(spec)
        sys.modules["csv2ont"] = csv2ont_module
        spec.loader.exec_module(csv2ont_module)
        
        if hasattr(csv2ont_module, 'main'):
            csv2ont_module.main()
            logger.info("Ontology Update Completed.")
            
            # Update hash and timestamp
            last_file_hash = get_file_hash(TTL_PATH)
            last_update_time = datetime.now()
            
            # Git commit and push if requested
            if auto_commit:
                logger.info("Attempting to commit and push changes...")
                if git_commit_and_push("src/ontology/AREMA-ontology.ttl"):
                    logger.info("Changes committed and pushed successfully")
                else:
                    logger.warning("Failed to commit and push changes")
        else:
            logger.warning("No main() found. Module level code ran.")
            
    except Exception as e:
        logger.error(f"Update Failed: {str(e)}", exc_info=True)
    finally:
        is_updating = False


def scheduled_check():
    """Check for changes in Google Sheet and trigger update if needed."""
    global is_updating, last_check_time, last_file_hash
    
    if is_updating:
        logger.info("Skipping scheduled check - update already in progress")
        return
    
    try:
        last_check_time = datetime.now()
        logger.info(f"Running scheduled check at {last_check_time}")
        
        # Get current hash before fetching new data
        old_hash = last_file_hash or get_file_hash(TTL_PATH)
        
        # Mark as updating to prevent concurrent checks
        is_updating = True
        logger.info("Fetching latest data from Google Sheets...")
        
        # Run conversion to generate new TTL
        run_conversion_logic(mock_mode=False, auto_commit=False)
        
        # Check if file changed
        new_hash = get_file_hash(TTL_PATH)
        
        if old_hash != new_hash:
            logger.info("Changes detected! Committing and pushing to trigger SKOHub rebuild...")
            # Git commit and push to trigger GitHub Actions
            git_commit_and_push("src/ontology/AREMA-ontology.ttl")
        else:
            logger.info("No changes detected in Google Sheet")
            
    except Exception as e:
        logger.error(f"Scheduled check failed: {str(e)}")
    finally:
        is_updating = False


@app.on_event("startup")
def start_scheduler():
    """Start the background scheduler on app startup."""
    global last_file_hash
    
    # Initialize the file hash
    last_file_hash = get_file_hash(TTL_PATH)
    logger.info(f"Initial file hash: {last_file_hash}")
    
    # Schedule the check every 5 minutes
    scheduler.add_job(scheduled_check, 'interval', minutes=5, id='check_updates')
    scheduler.start()
    logger.info("Scheduler started - checking for updates every 5 minutes")


@app.on_event("shutdown")
def shutdown_scheduler():
    """Shutdown the scheduler on app shutdown."""
    scheduler.shutdown()
    logger.info("Scheduler shutdown")


@app.get("/")
async def root():
    """Service status and scheduler info."""
    return {
        "service": "AREMA Ontology Manager",
        "version": "2.0.0",
        "status": "running",
        "updating": is_updating,
        "scheduler": {
            "active": scheduler.running if hasattr(scheduler, 'running') else True,
            "check_interval": "5 minutes",
            "last_check": last_check_time.isoformat() if last_check_time else None,
            "last_update": last_update_time.isoformat() if last_update_time else None
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "updating": is_updating}


@app.put("/update")
async def trigger_update(req: UpdateRequest, background_tasks: BackgroundTasks):
    """
    Trigger an ontology update.
    
    - **mock_mode**: If true, uses local mock data instead of Google Sheets
    - **auto_commit**: If true, automatically commits and pushes changes to git
    """
    global is_updating
    if is_updating:
        raise HTTPException(
            status_code=409,
            detail="Update already in progress"
        )

    is_updating = True
    background_tasks.add_task(run_conversion_logic, req.mock_mode, req.auto_commit)
    return {
        "status": "Update started",
        "mode": "mock" if req.mock_mode else "production",
        "auto_commit": req.auto_commit
    }


@app.get("/status")
async def get_status():
    """Get the current status of the ontology manager."""
    return {
        "updating": is_updating,
        "script_path": SCRIPT_PATH,
        "script_exists": os.path.exists(SCRIPT_PATH)
    }
