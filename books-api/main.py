import json
import logging
import uuid
import os
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# Data Persistence Configuration ---
DATA_FILE = "data/books-data.json"

# Use a simple in-memory list to store data loaded from the file
# This will be reloaded on server restart, but works for the CRUD demo.
books_db: List[Dict[str, any]] = []


# File Handling Functions (Simulating Database I/O) ---

def _load_data():
    """Loads book data from the JSON file into the in-memory database."""
    global books_db
    # with open(DATA_FILE, 'r') as f:
    #         books_db = json.load(f)
    #         logger.info(f"Successfully loaded {len(books_db)} records from {DATA_FILE}")
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

# # Load initial data when the application starts
_load_data()
# logger.info(books_db)



class Author(BaseModel):
    name: str = Field(min_length=3, description="The full name of the author")
    country: str = Field(min_length=2, max_length=50, description="The author's country of origin.")

    # Basemodel
class BookBase(BaseModel):
    title:str = Field(min_length=1, description="The title of the book")
    year:int = Field(gt=1980, lt=2025, description="The publication year of the book.")
    author: Author  

# Response model
class Book(BookBase):
    id: uuid.UUID = Field(description="The unique identifier for the book.")

@app.get("/healthz", status_code=status.HTTP_200_OK)
def health_check():
    file_exists = os.path.exists(DATA_FILE)

    status_detail = {
        "status": "OK",
        "service": "Book CRUD API",
        "Data_file_status": "Available" if file_exists else "Missing (Check deployment volume)"
    }

    logger.info(f"Health check performed. Data file status: {status_detail['Data_file_status']}")
    return status_detail


# post method
@app.post("/books/", response_model=Book, status_code=status.HTTP_201_CREATED)
def create_book(book_data: BookBase):

    new_id = uuid.uuid4()
    new_book = book_data.model_dump()
    new_book["id"] = str(new_id)

    books_db.append(new_book)
    _save_data()

    logger.info(f"Book created with ID: {new_book['id']}")
    return new_book


# @app.get("/books/", response_model=List[Book])
# def read_all_books():
#     logger.info(f"Reading all {len(books_db)} books.")
#     return books_db
@app.get("/books/", response_model=list[Book])
def read_all_books():
    """Retrieves a list of all books in the database."""
    logger.info(f"Reading all {len(books_db)} books.")
    # FastAPI automatically handles converting the list of dicts to the List[Book] response model
    return books_db

# # GET: Read one operation 
@app.get("/books/{book_id}", response_model=Book)
def read_single_book(book_id: str):

    try:
        target_uuid = uuid.UUID(book_id)
    except ValueError:
        logger.warning(f"Invalid UUID format provided:{book_id}") 

        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid book ID format: '{book_id}'. Must be a valid  UUID."
        )   
    
    for book in books_db:
        if book.get("id") == str(target_uuid):
             logger.info(f"Successfully retrived book with Id: {book_id}")
             return book

    logger.warning(f"Book not found with ID: {book_id}")    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Book with ID {book_id} not found."
    )


# Implement UPDATE endpoint
@app.put("/books/{book_id}", response_model=Book)
def update_book(book_id:str, book_data: BookBase):

    try:
        target_uuid = str(uuid.UUID(book_id))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid book ID format: '{book_id}'. Must be a valid UUID"
        )    

    found = False
    for i, book in enumerate(books_db):
        if book.get("id") == target_uuid:
            updated_book = book_data.model_dump()
            updated_book["id"] = target_uuid
            books_db[i] = updated_book
            _save_data()

            logger.info(f"Book updated with ID: {book_id}")
            found = True
            return updated_book
        
        if not found:
            logger.warning(f"Update failed. Book not found with ID: {book_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Book with ID {book_id} not found. Cannot update."
            )
        

# Implement DELETE operation
@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: str):

    """Deletes a book identified by its UUID. returns 204 No Content upon successful deletion""" 

    global books_db

    # try to validate the uuid format
    try:
        target_uuid = str(uuid.UUID(book_id))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid book ID format: '{book_id} Must be a valid UUID."
        )        
    # use a list comprehension to filter out the book to be deleted
    initial_length = len(books_db)
    books_db = [book for book in books_db if book.get("id")  != target_uuid]

    if len(books_db) <  initial_length:
        _save_data()
        logger.info(f"Book successfully deleted with ID: {book_id}")

        # return 204 NO Content for a successful deletion 
        return 
    else:
        # exception handling :if the book  was not in the list
         logger.warning(f"Deletd failed . book not found with ID: {book_id}")

         raise HTTPException(
             status_code=status.HTTP_404_NOT_FOUND, detail=f"Book with ID {book_id} not found. Cannot delete."
         )
    