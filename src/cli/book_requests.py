import requests
from typing import Dict, List

def get_book(item_number: int) -> Dict:
    """
    Fetches the book corresponding to item number item_number from the front end server.
    """
    response = requests.get(f"http://localhost:5002/books/{item_number}")
    # Todo: Add comments for exception handling
    if response.status_code == 400:
        raise Exception(f"Book with item number {item_number} does not exist")
    elif response.status_code != 200:
        raise Exception(f"Something Failed. Could not fetch the book with item number {item_number}.")
    return response.json()

def get_books_by_topic(topic: str) -> List[Dict]:
    payload = {"topic": topic}
    response = requests.get(f"http://localhost:5002/books", params=payload)
    # Todo: Add comments for exception handling.
    if response.status_code == 400:
        raise Exception(f"Failed to fetch the requested data")
    
    return response.json()

def buy_book(item_number: int) -> Dict:
    response = requests.post(f"http://localhost:5002/books/{item_number}")
    # Todo: Add comments for execption handling.
    if response.status_code != 200:
        raise Exception(f"Failed to buy the book")
    return response.json()


