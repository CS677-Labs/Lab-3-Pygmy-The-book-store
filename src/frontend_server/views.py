import logging

import flask
import requests
from flask import request, jsonify, Response
from load_balancer import getCatalogServerURL, getOrderServerURL, Server

logging.basicConfig(filename='frontend.log', level=logging.DEBUG)
flask = flask.Flask(__name__)
cache = {}
from threading import Lock

lock = Lock()


@flask.route('/books/<int:item_number>', methods=['GET'])
def lookup(item_number: int):
    global cache
    if item_number in cache:
        logging.info(f'{item_number} found in cache.')
        return cache[item_number]

    catalogServerURL = getCatalogServerURL()

    try:
        url = f'http://{catalogServerURL}/books/{item_number}'
        logging.debug(f"Trying to connect to {url}")
        r = requests.get(url)
    except requests.exceptions.RequestException as e:
        logging.error(f"Exception occured. {e}")
        return f"Ughh! Catalog server seems to be down. Failed to fetch the book with item number {item_number}.", 501
    if r.status_code != 200:
        error_msg = f"Failed to fetch the book with item number {item_number}."
        if "message" in r.json():
            error_msg += " " + r.json()["message"]
        return error_msg, r.status_code
    book = r.json()
    lock.acquire()
    cache[item_number] = book
    lock.release()
    logging.info(f'Caching lookup results of {item_number}')
    return book


@flask.route('/books', methods=['GET'])
def search():
    topic = request.args.get('topic')

    catalogServerURL = getCatalogServerURL()

    if topic is None:
        return "The request must send the query parameter \"topic\"", 400

    payload = {'topic': topic}
    try:
        url = f'http://{catalogServerURL}/books'
        logging.info(f"Trying to connect to {url}")
        r = requests.get(url, params=payload)
    except requests.exceptions.RequestException as e:
        logging.error(f"Exception occured. {e}")
        return f"Ughh! Catalog server seems to be down. Failed to fetch the books for the topic {topic}.", 501
    if r.status_code != 200:
        return f"Failed to fetch the books related to topic {topic}.", r.status_code
    books = r.json()
    return jsonify(books)


@flask.route('/books/<int:item_number>', methods=['POST'])
def buy(item_number: int):
    orderServerURL = getOrderServerURL()

    try:
        url = f'http://{orderServerURL}/books/{item_number}'
        logging.info(f"Trying to connect to {url}")
        r = requests.post(url)
    except requests.exceptions.RequestException as e:
        logging.error(f"Exception occured. {e}")
        return f"Ughh! Order server seems to be down. Failed to buy the book with item number {item_number}.", 501

    if r.status_code != 200:
        error_msg = f"Failed to buy the book with item number {item_number}."
        if "Error" in r.json():
            error_msg += " " + r.json()["Error"]
        return error_msg, r.status_code
    book = r.json()
    return book


@flask.route('/cache/<int:item_number>', methods=['DELETE'])
def invalidate_cache(item_number: int):
    # Cache for the item_number to be invalidated here.
    logging.info(f'Invalidating cache for {item_number} if it exists')
    lock.acquire()
    cache.pop(item_number, None)
    lock.release()
    return Response(status=204)


# Function to read config file and populate info about diff catalog, order and frontend servers.
def load_config(config_file_path):
    catalog_port=5000
    order_port=5001
    frontend_ports=5002
    with open(config_file_path, "r") as f:
        catalogServerIPs = f.readline().rstrip('\r\n').split(",")
        orderServerIPs = f.readline().rstrip('\r\n').split(",")
        frontendServerIPs = f.readline().rstrip('\r\n').split(",")
    for i,catalog_server_ip in enumerate(catalogServerIPs):
        Server.catalog_servers_urls.append(f"http://{catalog_server_ip}:{catalog_port+i*3}")
    for i,order_server_ip in enumerate(orderServerIPs):
        Server.order_servers_urls.append(f"http://{order_server_ip}:{order_port+i*3}")

if __name__ == '__main__':
    load_config("config")
    flask.run(port=5002,debug=True)
