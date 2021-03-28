import flask
from flask import request, jsonify, Response
import logging
import os
import requests

logging.basicConfig(filename='frontend.log', level=logging.WARNING)
flask = flask.Flask(__name__)


@flask.route('/books/<int:item_number>', methods=['GET'])
def lookup(item_number: int):    
    # Todo: Fetch the url from a config file rather than hardcoding it.
    r = requests.get(f'http://localhost:5000/{item_number}')
    if r.status_code != 200:
        return r.text, r.status_code
    book = r.json()
    return book

@flask.route('/books', methods=['GET'])
def search():
    topic = request.args.get('topic')
    if topic is None:
        return "The request must have the topic query parameter", 400
    # Todo: Fetch the url from a config file rather than hardcoding it.
    payload = {'topic':topic}
    r = requests.get(f'http://localhost:5000', params=payload)
    if r.status_code != 200:
        return f"Failed to fetch the books related to topic {topic}", r.status_code
    books = r.json()
    return books

@flask.route('/books/<int:item_number>', methods=['POST'])
def buy(item_number: int):
    # Todo: Fetch the url from a config file rather than hardcoding it.
    r = requests.post(f'http://localhost:5001/{item_number}')
    if r.status_code != 200:
        return f"Failed to buy the book with item number {item_number}", r.status_code
    book = r.json()
    return book
    
if __name__ == '__main__':
    flask.run(debug=True, port=5002)