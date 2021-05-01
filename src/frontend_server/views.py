import logging

import flask
import requests
from flask import request, jsonify, Response
from load_balancer import getCatalogServerURL, getOrderServerURL, Server
import time
import atexit

from apscheduler.schedulers.background import BackgroundScheduler
from threading import Lock

#logging.basicConfig(filename='frontend.log', level=logging.DEBUG)
logger=logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.FileHandler("frontend.log"))
flask = flask.Flask(__name__)
cache = {}
scheduler = BackgroundScheduler()

def check_servers():
    for catalog_server in Server.catalog_servers_urls:
        try:
            r = requests.get(f"{catalog_server[0]}/health")
            catalog_server[1]=(r.status_code==200 and r.json()["message"]=="Healthy")
        except requests.exceptions.RequestException:
            catalog_server[1]=False

    for order_server in Server.order_servers_urls:
        try:
            r = requests.get(f"{order_server[0]}/health")
            order_server[1]=(r.status_code==200 and r.json()["message"]=="Healthy")
        except requests.exceptions.RequestException:
            order_server[1]=False

scheduler.add_job(func=check_servers, trigger="interval", seconds=30)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

lock = Lock()
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
        Server.catalog_servers_urls.append([f"http://{catalog_server_ip}:{catalog_port+i*3}",True])
    for i,order_server_ip in enumerate(orderServerIPs):
        Server.order_servers_urls.append([f"http://{order_server_ip}:{order_port+i*3}", True])
    
load_config("config")

@flask.route('/books/<int:item_number>', methods=['GET'])
def lookup(item_number: int):
    global cache
    if item_number in cache:
        logger.info(f'{item_number} found in cache.')
        return cache[item_number]
    
    for i in range(2):            
        catalogServerURL = getCatalogServerURL()
        try:
            url = f'{catalogServerURL}/books/{item_number}'
            logger.debug(f"Trying to connect to {url}")
            r = requests.get(url)
            break
        except requests.exceptions.RequestException as e:
            logger.error(f"Exception occured. {e}. The catalog server with ip {catalogServerURL} seems to be down. Will retry the request with the other catalog servers.")
            if i == 0:
                check_servers()
                continue
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
    logger.info(f'Caching lookup results of {item_number}')
    return book


@flask.route('/books', methods=['GET'])
def search():
    topic = request.args.get('topic')

    if topic is None:
        return "The request must send the query parameter \"topic\"", 400

    payload = {'topic': topic}
    for i in range(2):    
        catalogServerURL = getCatalogServerURL()
        try:
            url = f'{catalogServerURL}/books'
            logger.info(f"Trying to connect to {url}")
            r = requests.get(url, params=payload)
            break
        except requests.exceptions.RequestException as e:
            logger.error(f"Exception occured. {e}. The catalog server with ip {catalogServerURL} seems to be down. Will retry the request with the other catalog servers.")
            if i == 0:
                check_servers()
                continue
            return f"Ughh! Catalog server seems to be down. Failed to fetch the books for the topic {topic}.", 501
    if r.status_code != 200:
        return f"Failed to fetch the books related to topic {topic}.", r.status_code
    books = r.json()
    return jsonify(books)


@flask.route('/books/<int:item_number>', methods=['POST'])
def buy(item_number: int):
    for i in range(2):
        orderServerURL = getOrderServerURL()
        try:
            url = f'{orderServerURL}/books/{item_number}'
            logger.info(f"Trying to connect to {url}")
            r = requests.post(url)
        except requests.exceptions.RequestException as e:
            logger.error(f"Exception occured. {e}. The order server with ip {orderServerURL} seems to be down. Will retry the request with the other order servers.")
            if i == 0:
                check_servers()
                continue
            return f"Ughh! Order server seems to be down. Failed to buy the book with item number {item_number}.", 501

        if r.status_code != 200:
            logger.error(f"The order server did not return 200 status code. The order server with ip {orderServerURL} seems to be down. Will retry the request with the other order servers.")

            if i == 0:
                check_servers()
                continue
            error_msg = f"Failed to buy the book with item number {item_number}."
            if "Error" in r.json():
                error_msg += " " + r.json()["Error"]
            return error_msg, r.status_code
        break
    book = r.json()
    return book


@flask.route('/cache/<int:item_number>', methods=['DELETE'])
def invalidate_cache(item_number: int):
    # Cache for the item_number to be invalidated here.
    logger.info(f'Invalidating cache for {item_number} if it exists')
    lock.acquire()
    cache.pop(item_number, None)
    lock.release()
    return Response(status=204)



if __name__ == '__main__':
    load_config("config")
    check_servers()
    flask.run(port=5002,debug=True)
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=check_servers, trigger="interval", seconds=5)
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())
