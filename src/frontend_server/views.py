import flask
from flask import request, jsonify, Response
import logging
import os
import requests

logging.basicConfig(filename='frontend.log', level=logging.WARNING)
flask = flask.Flask(__name__)

@flask.route('/books/<int:item_number>', methods=['GET'])
def lookup(item_number: int):    

    f = open("machines.txt", "r")
    catalogServerIP = f.readline()
    f.close()
    
    try:
        r = requests.get(f'http://{catalogServerIP}:5000/books/{item_number}')
    except requests.exceptions.RequestException as e:
        return f"Ughh! Catalog server seems to be down. Failed to fetch the book with item number {item_number}.", 501
    if r.status_code != 200:
        error_msg = f"Failed to fetch the book with item number {item_number}."
        if "message" in r.json():
            error_msg += " "+ r.json()["message"]
        return error_msg, r.status_code
    book = r.json()
    return book

@flask.route('/books', methods=['GET'])
def search():
    topic = request.args.get('topic')
    
    f = open("machines.txt", "r")
    catalogServerIP = f.readline()
    f.close()
    
    if topic is None:
        return "The request must send the query parameter \"topic\"", 400
    
    payload = {'topic':topic}
    try:
        r = requests.get(f'http://{catalogServerIP}:5000/books', params=payload)
    except requests.exceptions.RequestException as e:
        return f"Ughh! Catalog server seems to be down. Failed to fetch the books for the topic {topic}.", 501
    if r.status_code != 200:
        return f"Failed to fetch the books related to topic {topic}.", r.status_code
    books = r.json()
    return jsonify(books)

@flask.route('/books/<int:item_number>', methods=['POST'])
def buy(item_number: int):
    
    f = open("machines.txt", "r")
    catalogServerIP = f.readline()
    orderServerIP = f.readline()
    f.close()

    try:
        r = requests.post(f'http://{orderServerIP}:5001/books/{item_number}')
    except requests.exceptions.RequestException as e:
        return f"Ughh! Order server seems to be down. Failed to buy the book with item number {item_number}.", 501
        
    if r.status_code != 200:
        error_msg = f"Failed to buy the book with item number {item_number}."
        if "Error" in r.json():
            error_msg += " " + r.json()["Error"]
        return error_msg, r.status_code
    book = r.json()
    return book
    
if __name__ == '__main__':
    flask.run(debug=True)
