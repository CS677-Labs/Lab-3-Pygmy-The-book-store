import flask
from flask import request, jsonify, make_response
import logging
import os
from orders_db import appendOrderDetailsToDb

logging.basicConfig(filename='Orders.log', level=logging.DEBUG)
orderServer = flask.Flask(__name__)

def updateCatalogServer() :
    logging.info("Updating catalog server now")

def lookupItem(itemNum) :
    logging.info("Looking up {} on catalog server".format(itemNum))
    return True

@orderServer.route('/buy/<id>', methods=['POST'])
def placeOrder(id):
    id = int(id)
    # Do a lookup for that id
    lookupResult = lookupItem(id)
    dataToReturn = None
    if lookupResult is True :
        dataToReturn = appendOrderDetailsToDb(id, "Success")
        if dataToReturn is not None :
            updateCatalogServer()
        
    else :
        dataToReturn = appendOrderDetailsToDb(id, "Failed")

    response = None
    if dataToReturn is None :
        response = make_response (
            jsonify ( 
                {"Error" : "Failed to update details of this order. Please try again"} 
            ),
            500,
        )
    else :
        response = make_response (
            jsonify ( 
                {"Order details" : dataToReturn} 
            ),
            200,
        )

    return response

orderServer.run(port=5001,debug=True)