import json
import os

from flask import Flask
from flask import request, jsonify, Response
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data', 'catalog.sqlite')
db = SQLAlchemy(app)
ma = Marshmallow(app)


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.VARCHAR)
    topic = db.Column(db.VARCHAR)
    count = db.Column(db.Integer)
    __table_args__ = (
        db.CheckConstraint('count >= 0'),
        {})

    def __init__(self, title, topic, count):
        self.title = title
        self.topic = topic
        self.count = count


class BookSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('id', 'title', 'topic', 'count')


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
    if not os.path.exists(os.path.join(basedir, 'data', 'catalog.sqlite')):
        db.create_all()
        with open(os.path.join(basedir, 'data', 'book_details.json')) as f:
            data = json.load(f)
        for book in data:
            new_book = Book(book['title'], book['topic'], book['count'])
            db.session.add(new_book)
        db.session.commit()

    app.run(debug=True)
