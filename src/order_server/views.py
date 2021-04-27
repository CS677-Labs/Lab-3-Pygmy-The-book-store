import logging

import flask
import requests
from flask import jsonify, make_response, request, Response
from urllib.parse import urlparse
import sys

from orders_db import appendOrderDetailsToDb, insertRowToDB, getAllRowsFromDb, resync_database
from enum import Enum



class State(Enum) :
    INIT = 0
    RUNNING = 1



class Server:
    catalog_servers_urls=[]
    order_servers_urls=[]
    frontend_servers_urls=[]



logging.basicConfig(filename='orders.log', level=logging.DEBUG)
orderServer = flask.Flask(__name__)



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



# End point for a buy request.
@orderServer.route('/books/<id>', methods=['POST'])
def placeOrder(id):
    id = int(id)

    # Do a lookup for this id
    logging.info("Looking up {} on catalog server".format(id))
    try:
        url=f"{catalogServerURL}/books/{id}"
        logging.info(f"Trying to connect to {url}")
        response = requests.get(url)
    except requests.exceptions.RequestException as e:
        logging.error(f"Exception occured. {e}")
        return make_response (jsonify({"Error" : f"Ughh! Catalog server seems to be down."}),  501)
    lookupResult = True
    
    if response.status_code == 404 :
        return make_response (jsonify({"Error" : f"Book with ID {id} not found"}),  404)

    else :
        responseJson = response.json()
        if responseJson["count"] == 0 :
            return make_response(jsonify({"Error" : f"No stock for Book with ID {id}"}), 400)
    
    # Reduce count for this id
    logging.info("Updating catalog server now")
    response = requests.patch(url=f"{catalogServerURL}/books/{id}", json={'count' : {'_operation' : 'decrement', 'value' : 1}})
    if response.status_code == 400 :
        return make_response(jsonify({"Error" : f"No stock for Book with ID {id}"}), 400)
    else :
        if response.status_code != 200 :
            return response

    # Create a new row in orders.db
    dataToReturn = appendOrderDetailsToDb(id, "Success")
    response = None
    if dataToReturn is None :
        response = make_response (
            jsonify ( 
                {"Error" : "Failed to update details of this order. Please try again"} 
            ),
            500,
        )
    else :
        # Now push this new row to other replicas.
        for i, order_server_replica in enumerate(Server.order_servers_urls) :
            if i != node_num :
                url = f"{order_server_replica}/orders"
                logging.info(f"Updating this new row on {order_server_replica}")
                response = requests.post(url=url, json=dataToReturn)
                if response.status_code != 200 :
                    logging.info(f"Failed to update order details to replica {order_server_replica}. Error - {response}")
        
        response = make_response (jsonify(dataToReturn),200)

    global node_state
    node_state = State.RUNNING

    return response




# End point used by order server to insert order details to other replicas.
@orderServer.route('/orders', methods=['POST'])
def insertOrderDetails():    
    
    logging.info("Inserting new row to orders.db")

    dataToReturn = insertRowToDB(request.json)
    response = None
    if dataToReturn is None :
        response = make_response (
            jsonify ( 
                {"Error" : "Failed to update details of this order. Please try again"} 
            ),
            500,
        )
    else :
        response = make_response (jsonify(dataToReturn),200)
    
    global node_state
    node_state = State.RUNNING
    
    return response



# Endpoint to return all rows. Will be used for resync
@orderServer.route("/table", methods=["GET"])
def get_allRows():
    global node_state
    if node_state != State.INIT :
        all_orders = getAllRowsFromDb()
        return make_response(jsonify(all_orders), 200)
    else :
        # Since the server is in INIT state, no writes have been performed.
        # No data to return.
        return Response(status=204)



if __name__ == '__main__':
    global node_num
    node_num = int(sys.argv[1])
    global node_state
    node_state = State.INIT

    load_config("config")
    
       # Try to connect with other replicas to ensure this one is in sync with the others.
    for i, order_server_replica in enumerate(Server.order_servers_urls) :
        if i != node_num :
            url = f"{order_server_replica}/table"
            logging.info(f"Trying to sync with replica with node num {node_num} - {order_server_replica}")
            try :
                response = requests.get(url=url)
                if response.status_code == 204 :
                    logging.info(f"Replica {node_num} - {order_server_replica} is also in INIT state. We are in sync")
                    break

                if response.status_code == 200 :
                    logging.info(f"Replica {node_num} - {order_server_replica} is in RUNNING state. We will sync our DB with that of the replica")
                    resync_database(response.json())
                    break
            except :
                logging.info(f"Replica {node_num} - {order_server_replica} did not return valid status. It may not be up yet.")

    global catalogServerURL
    catalogServerURL = Server.catalog_servers_urls[node_num]
    
    o = urlparse(Server.order_servers_urls[node_num])
    orderServer.run("0.0.0.0",port=o.port, debug=True)