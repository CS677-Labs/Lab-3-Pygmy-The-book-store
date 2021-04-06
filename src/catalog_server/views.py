import json

from flask import request, jsonify, Response
from sqlalchemy import exc

from models import Book, BookSchema, db, app

book_schema = BookSchema()
books_schema = BookSchema(many=True)


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
    return jsonify([(dict(row)) for row in filtered_books])


# Endpoint to get details of a book given the id
@app.route("/books/<id>", methods=["GET"])
def book_detail(id):
    book = Book.query.with_entities(Book.cost, Book.count).filter_by(id=id).first()
    if not book:
        return Response(json.dumps({"message": f"Book with id {id} not found."}), status=404, mimetype='application/json')
    return jsonify(dict(book))


# Endpoint to update details of a book
@app.route("/books/<id>", methods=["PATCH"])
def book_update(id):
    # Handling concurrent requests
    book = db.session.query(Book).filter(Book.id==id).with_for_update().one()
    current_book_count = book.count
    book.topic = request.json.get('topic') or book.topic
    book.title = request.json.get('title') or book.title
    book.cost = request.json.get('cost') if 'cost' in request.json else book.cost

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
        return Response(json.dumps({"message": f"Current count = {current_book_count}. Cannot {request.json['count'].get('_operation')} by {request.json['count'].get('value')}."}), status=400,
                        mimetype='application/json')
    return book_schema.jsonify(book)


# Endpoint to delete a book
@app.route("/books/<id>", methods=["DELETE"])
def book_delete(id):
    book = Book.query.get(id)
    if not book:
        return Response(json.dumps({"message": f"Book with id {id} not found."}), status=404, mimetype='application/json')
    try:
        db.session.delete(book)
        db.session.commit()
    except:
        return Response(json.dumps({"message": f"Failed to delete book."}), status=500, mimetype='application/json')
    return book_schema.jsonify(book)


if __name__ == '__main__':
    app.run(debug=True)
