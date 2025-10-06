import json
import logging
from typing import List, Dict, Any
from fastapi import FastAPI

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# Data Persistence Configuration ---
DATA_FILE = "data/books-data.json"

# Use a simple in-memory list to store data loaded from the file
# This will be reloaded on server restart, but works for the CRUD demo.
books_db: List[Dict[str, Any]] = []


# File Handling Functions (Simulating Database I/O) ---

def _load_data():
    """Loads book data from the JSON file into the in-memory database."""
    global books_db
    try:
        with open(DATA_FILE, 'r') as f:
            books_db = json.load(f)
            logger.info(f"Successfully loaded {len(books_db)} records from {DATA_FILE}")
    except FileNotFoundError:
        logger.warning(f"{DATA_FILE} not found. Initializing with empty database.")
        books_db = []
    except json.JSONDecodeError:
        logger.error(f"Error decoding JSON from {DATA_FILE}. Initializing with empty database.")
        books_db = []

def _save_data():
    """Saves the current state of the in-memory database back to the JSON file."""
    try:
        with open(DATA_FILE, 'w') as f:
            # Use indent=2 for readability in the file
            json.dump(books_db, f, indent=2)
        logger.info(f"Successfully saved {len(books_db)} records to {DATA_FILE}")
    except Exception as e:
        logger.error(f"Failed to save data to {DATA_FILE}: {e}")

# Load initial data when the application starts
_load_data()
logger.info(books_db)
