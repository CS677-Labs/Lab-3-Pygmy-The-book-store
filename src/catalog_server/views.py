from flask import request, jsonify, Response
from sqlalchemy import exc

from src.catalog_server.models import Book, BookSchema, db, app

book_schema = BookSchema()
books_schema = BookSchema(many=True)


# TODO error handling: catch more specific exceptions?
# Endpoint to create a new book item
@app.route("/books", methods=["POST"])
def add_book():
    # fixme Add validation here?
    new_book = Book(request.json['title'], request.json['topic'], request.json['count']['value'])
    try:
        db.session.add(new_book)
        db.session.commit()
    except:
        return Response(status=500, mimetype='application/json')
    return jsonify(book_schema.dump(new_book))


# Endpoint to return books on a given topic
@app.route("/books", methods=["GET"])
def get_books():
    filtered_books = Book.query.filter_by(topic=request.args.get('topic'))
    result = books_schema.dump(filtered_books)
    return jsonify(result)


# Endpoint to get details of a book given the id
@app.route("/books/<id>", methods=["GET"])
def book_detail(id):
    book = Book.query.get(id)
    if not book:
        return Response(f"Book with id {id} not found.", status=404, mimetype='application/json')
    return book_schema.jsonify(book)


# Endpoint to update details of a book
@app.route("/books/<id>", methods=["PATCH"])
def book_update(id):
    book = Book.query.get(id)
    book.topic = request.json.get('topic') or book.topic
    book.title = request.json.get('title') or book.title

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
        return Response(f"0 books remaining. Cannot {request.json['count'].get('_operation')}.", status=400,
                        mimetype='application/json')
    return book_schema.jsonify(book)


# Endpoint to delete a book
@app.route("/books/<id>", methods=["DELETE"])
def book_delete(id):
    book = Book.query.get(id)
    if not book:
        return Response(f"Book with id {id} not found.", status=404, mimetype='application/json')
    try:
        db.session.delete(book)
        db.session.commit()
    except:
        return Response(status=500, mimetype='application/json')
    return book_schema.jsonify(book)


if __name__ == '__main__':
    app.run(debug=True)
