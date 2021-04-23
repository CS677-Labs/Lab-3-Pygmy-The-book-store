import json
import logging
import sys
import requests
from flask import request, jsonify, Response
from sqlalchemy import exc
from urllib.parse import urlparse
import click
from models import Book, BookSchema, db, app

book_schema = BookSchema()
books_schema = BookSchema(many=True)
logging.basicConfig(filename='catalog.log', level=logging.DEBUG)

class Server:
    catalog_servers_urls=[]
    order_servers_urls=[]
    frontend_servers_urls=[]

# Function to read config file and populate info about diff catalog, order and frontend servers.
def load_config(config_file_path):
    catalog_port=5000
    order_port=5001
    frontend_port=5002
    with open(config_file_path, "r") as f:
        catalogServerIPs = f.readline().rstrip('\r\n').split(",")
        orderServerIPs = f.readline().rstrip('\r\n').split(",")
        frontendServerIPs = f.readline().rstrip('\r\n').split(",")
    for i,catalog_server_ip in enumerate(catalogServerIPs):
        Server.catalog_servers_urls.append(f"http://{catalog_server_ip}:{catalog_port+i*3}")
    for i,order_server_ip in enumerate(orderServerIPs):
        Server.order_servers_urls.append(f"http://{order_server_ip}:{order_port+i*3}")
    for i,frontend_server_ip in enumerate(frontendServerIPs):
        Server.frontend_servers_urls.append(f"http://{frontend_server_ip}:{frontend_port+i*3}")

def getFrontEndServerURL():
    return Server.frontend_servers_urls[0]


# Endpoint to create a new book item
@app.route("/books", methods=["POST"])
def add_book():
    new_book = Book(request.json['title'], request.json['topic'], request.json['count']['value'], request.json['cost'])
    try:
        db.session.add(new_book)
        db.session.commit()
    except:
        return Response(json.dumps({"message": "Failed to add book."}), status=500, mimetype='application/json')
    return jsonify(book_schema.dump(new_book))


# Endpoint to return books on a given topic
@app.route("/books", methods=["GET"])
def get_books():
    filtered_books = Book.query.with_entities(Book.id, Book.title).filter_by(topic=request.args.get('topic')).all()
    return jsonify([(dict(row)) for row in filtered_books])  # fixme using dump and jsonify directly results in an error


# Endpoint to get details of a book given the id
@app.route("/books/<id>", methods=["GET"])
def book_detail(id):
    book = Book.query.with_entities(Book.cost, Book.count).filter_by(id=id).first()
    if not book:
        return Response(json.dumps({"message": f"Book with id {id} not found."}), status=404,
                        mimetype='application/json')
    return jsonify(dict(book))  # fixme using dump and jsonify directly results in an error


# Endpoint to update details of a book
@app.route("/books/<id>", methods=["PATCH"])
def book_update(id):
    # Handling concurrent requests
    book = db.session.query(Book).filter(Book.id == id).with_for_update().one()
    current_book_count = book.count
    book.topic = request.json.get('topic') or book.topic
    book.title = request.json.get('title') or book.title
    book.cost = request.json.get('cost') if 'cost' in request.json else book.cost
    propagateToReplica = bool(request.json.get('propagate')) if 'propagate' in request.json else True

    if request.json['count'].get('_operation'):
        if request.json['count'].get('_operation') == 'increment':
            book.count = book.count + request.json['count']['value']
        else:
            book.count = book.count - request.json['count']['value']
    else:
        book.count = request.json.get('count', {}).get('value') if request.json.get('count') else book.count

    try:
        db.session.commit()
    except exc.IntegrityError:
        return Response(json.dumps({
                                       "message": f"Current count = {current_book_count}. Cannot {request.json['count'].get('_operation')} by {request.json['count'].get('value')}."}),
                        status=400,
                        mimetype='application/json')

    # Propagate this info to other replicas
    if propagateToReplica == True :
        for i, catalog_server_replica in enumerate(Server.catalog_servers_urls) :
            if i != node_num :
                url = f"{catalog_server_replica}/books/{id}"
                logging.info(f"Updating this write on replica {url}")
                requestJson = request.json
                requestJson['propagate'] = False
                response = requests.patch(url=url, json=requestJson)
                if response.status_code != 200 :
                    logging.info(f"Failed to update write on replica {catalog_server_replica}. Error - {response}")

        # Invalidate in memory cache entry for the given id (if any) in front end server
        response = requests.delete(url=getFrontEndServerURL() + "/cache/" + str(id))
        if response.status_code != 204:
            logging.error("Failed to invalidate frontend server's cache.")
        else:
            logging.info(f"Successfully invalidated frontend server's cache entry corresponding to ID {id}")

    return book_schema.jsonify(book)


# Endpoint to delete a book
@app.route("/books/<id>", methods=["DELETE"])
def book_delete(id):
    book = Book.query.get(id)
    if not book:
        return Response(json.dumps({"message": f"Book with id {id} not found."}), status=404,
                        mimetype='application/json')
    try:
        db.session.delete(book)
        db.session.commit()
    except:
        return Response(json.dumps({"message": f"Failed to delete book."}), status=500, mimetype='application/json')

    # Invalidate in memory cache entry for the given id (if any) in front end server
    response = requests.delete(url=getFrontEndServerURL() + "cache/" + str(id))
    if response.status_code != 204:
        logging.error("Failed to invalidate frontend server's cache.")
    else:
        logging.info(f"Successfully invalidated frontend server's cache entry corresponding to ID {id}")

    return book_schema.jsonify(book)


if __name__ == '__main__':
    global node_num
    node_num = int(sys.argv[1])
    load_config("config")
    o = urlparse(Server.catalog_servers_urls[node_num])
    app.run("0.0.0.0", port=o.port, debug=True)
