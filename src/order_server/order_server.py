import logging

import flask
import requests
from flask import jsonify, make_response

from orders_db import appendOrderDetailsToDb

logging.basicConfig(filename='Orders.log', level=logging.DEBUG)
orderServer = flask.Flask(__name__)
catalogServerURL = "http://127.0.0.1:5000/"

@orderServer.route('/books/<id>', methods=['POST'])
def placeOrder(id):
    id = int(id)
    
    # Do a lookup for this id
    logging.info("Looking up {} on catalog server".format(id))
    try:
        response = requests.get(url=catalogServerURL+"books/"+str(id))
    except requests.exceptions.RequestException:
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

orderServer.run(port=5001,debug=True)