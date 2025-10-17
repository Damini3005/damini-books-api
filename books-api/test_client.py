import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"
BOOK_ENDPOINT = f"{BASE_URL}/books/"
HEADERS = {"Content-Type": "application/json"}
NEW_BOOK_ID = ""
# URL = f"{BASE_URL}/books/{NEW_BOOK_ID}"
def print_response(title,response, expected_status):
  print(f"\n--- {title} ---")
  print(f"URL: {response.url}")
  print(f"Method: {response.request.method}")
  print(f"Expected Status: {expected_status}, Received Status: {response.status_code}")
  

  try:
    print(f"Response Body: {json.dumps(response.json(),indent=2)}")
  except requests.exceptions.JSONDecodeError:
     print(f"Response Body: {response.text}")
  print("-"* 30)
  return response


def test_create_book():
    """Tests the POST /books/ endpoint."""
    global NEW_BOOK_ID
    
    print("\n\n##################### 1. TEST CREATE (POST) #####################")
    new_book_data = {
        "title": "Cosmic Rails",
        "year": 2024,
        "author": {
            "name": "Alex K.",
            "country": "USA"
        }
    }
    
    response = requests.post(BOOK_ENDPOINT, headers=HEADERS, json=new_book_data)
    response = print_response("POST: Create New Book", response, 201)
    
    if response.status_code == 201:
        NEW_BOOK_ID = response.json().get("id")
        print(f"Successfully created book. Captured ID: {NEW_BOOK_ID}")
    
    return response.status_code == 201

def test_read_all():
    """Tests the GET /books/ endpoint."""
    print("\n\n##################### 2. TEST READ ALL (GET) #####################")
    response = requests.get(BOOK_ENDPOINT)
    return print_response("GET: Read All Books", response, 200).status_code == 200

def test_update_book_id():
    """Tests the PUT /books/{book_id} endpoint."""
    global NEW_BOOK_ID

    print("\n\n##################### 3. UPDATE BOOK (PUT) #####################")

    # Hardcode or use the one created from POST
    NEW_BOOK_ID = "e22137d5-2e0f-48e0-a430-6644d6e98b0f"
    
    if not NEW_BOOK_ID:
        print("No book ID found! Please run test_create_book() first.")
        return False

    
    url = f"{BASE_URL}/books/{NEW_BOOK_ID}"

    updated_book_data = {
        "title": "Cosmic Rail - Updated",
        "year": 2024,
        "author": {
            "name": "John K.",
            "country": "USA"
        }
    }

    response = requests.put(url, headers=HEADERS, json=updated_book_data)
    response = print_response("PUT: Update Book", response, 200)

    return response.status_code == 200



test_read_all()
# test_create_book()
test_update_book_id()
