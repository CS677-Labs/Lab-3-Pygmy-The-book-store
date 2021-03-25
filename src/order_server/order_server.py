import flask
from flask import request, jsonify
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

@orderServer.route('/', methods=['POST'])
def makeOrder():
    status = "Success"
    # Check if an itemNum was provided as part of the URL.
    # If itemNum is provided, try to place the order.
    # If no itemNum is provided, return error.
    if 'itemNum' in request.args:
        itemNum = int(request.args['itemNum'])

        # Do a lookup for that itemNum
        lookupResult = lookupItem(itemNum)

        if lookupResult is True :
            appendOrderDetailsToDb(itemNum, "Success")
            updateCatalogServer()
            status = "Success"
        else :
            appendOrderDetailsToDb(itemNum, "Failed")
            status = "Failed"
            
    else:
        logging.error("itemNum is not part of the request.")
        status = "Error"

    returnJson = { "Status" : status }

    return returnJson

orderServer.run()