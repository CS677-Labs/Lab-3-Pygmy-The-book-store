import json
import os

from flask import Flask
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy, get_debug_queries


app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data', 'catalog.sqlite')
# app.config["SQLALCHEMY_ECHO"] = True
app.config["SQLALCHEMY_RECORD_QUERIES"] = True

db = SQLAlchemy(app)
ma = Marshmallow(app)


@app.after_request
def after_request(response):
    """
    This function is executed after the API request is completed.
    The queries executed are logged and the response is returned to the client that sent the API request.
    """
    for query in get_debug_queries():
        with open(os.path.join(basedir, 'logs', 'query_log.txt'), 'a') as f:
            f.write('Query: %s\nParameters: %s\n\n'
                % (query.statement, query.parameters))
    return response


class Book(db.Model):
    """
    Database model to store book details for the book store application.
    """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.VARCHAR)
    topic = db.Column(db.VARCHAR)
    count = db.Column(db.Integer)
    cost = db.Column(db.Float)
    __table_args__ = (
        db.CheckConstraint('count >= 0'),
        {})

    def __init__(self, title, topic, count, cost, ID = None):
        if ID != None :
            self.id = ID
        self.title = title
        self.topic = topic
        self.count = count
        self.cost = cost

class BookSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('id', 'title', 'topic', 'count')


if not os.path.exists(os.path.join(basedir, 'data', 'catalog.sqlite')):
    db.create_all()
    with open(os.path.join(basedir, 'data', 'book_details.json')) as f:  # book_details.json consists of the details of
        # each book like cost, number of copies available, title of the book and topic.
        # The database is initialised using this data.
        data = json.load(f)
    for book in data:
        new_book = Book(title=book['title'], topic=book['topic'], count=book['count'], cost=book['cost'])
        db.session.add(new_book)
    db.session.commit()
