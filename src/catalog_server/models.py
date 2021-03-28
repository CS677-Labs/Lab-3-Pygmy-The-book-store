import json
import os

from flask import Flask
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy

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


if not os.path.exists(os.path.join(basedir, 'data', 'catalog.sqlite')):
    db.create_all()
    with open(os.path.join(basedir, 'data', 'book_details.json')) as f:
        data = json.load(f)
    for book in data:
        new_book = Book(book['title'], book['topic'], book['count'])
        db.session.add(new_book)
    db.session.commit()
