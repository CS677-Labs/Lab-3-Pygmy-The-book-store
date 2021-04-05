import flask
import requests
from flask import request, jsonify, Response, make_response
import logging
import os
from orders_db import appendOrderDetailsToDb

logging.basicConfig(filename='orders.log', level=logging.DEBUG)
orderServer = flask.Flask(__name__)
catalogServerIP = "127.0.0.1"

@orderServer.route('/books/<id>', methods=['POST'])
def placeOrder(id):
    id = int(id)
    
    f = open("config", "r")
    catalogServerIP = f.readline().rstrip('\r\n')
    f.close()
    
    catalogServerURL = f"http://{catalogServerIP}:5000/"
    # Do a lookup for this id
    logging.info("Looking up {} on catalog server".format(id))
    try:
        url=f"http://{catalogServerIP}:5000/books/{id}"
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
    response = requests.patch(url=catalogServerURL+"books/"+str(id), json={'count' : {'_operation' : 'decrement', 'value' : 1}})
    if response.status_code == 400 :
        return make_response(jsonify({"Error" : f"No stock for Book with ID {id}"}), 400)
    else :
        if response.status_code != 200 :
            return response

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
        response = make_response (jsonify(dataToReturn),200)

    return response

if __name__ == '__main__':
    orderServer.run(port=5001,debug=True)
