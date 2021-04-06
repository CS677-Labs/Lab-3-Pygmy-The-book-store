import requests
from typing import Dict, List

def get_book(item_number: int, FRONTEND_URL: str) -> Dict:
    """
    Fetches the book corresponding to item number item_number from the front end server.
    """
    try:
        response = requests.get(f"{FRONTEND_URL}/books/{item_number}")
        #r.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise Exception("Frontend server seems to be down. Failed to fetch the book.")
    if response.status_code != 200:
        raise Exception(str(response.text))
    return response.json()

def get_books_by_topic(topic: str, FRONTEND_URL: str) -> List[Dict]:
    payload = {"topic": topic}
    try:
        response = requests.get(f"{FRONTEND_URL}/books", params=payload)
    except requests.exceptions.RequestException as e:
        raise Exception(f"Frontend server seems to be down. Failed to fetch the books for topic {topic}.")
    if response.status_code != 200:
        raise Exception(f"Failed to fetch the requested data.")
    
    return response.json()

def buy_book(item_number: int, FRONTEND_URL: str) -> Dict:
    try:
        response = requests.post(f"{FRONTEND_URL}/books/{item_number}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Frontend server seems to be down. Failed to buy the book with item number {item_number}.")
    if response.status_code != 200:
        raise Exception(str(response.text))
    return response.json()

