import click
from book_requests import get_book, get_books_by_topic, buy_book

@click.group()
def bookstore():
    click.echo("Welcome to the World's Smallest Book Store!")

@click.command()
@click.argument("item_number", required=True)
def lookup(item_number: int):
    click.echo(f"Looking up item number {item_number}...")
    try:
        #book = get_book(item_number)
        book = {"Item Number": item_number, "Name": "Some random name."}
    except Exception as e:
        click.echo(f"Failed - {str(e)}", err=True)
        return
    click.echo(book)

@click.command()
@click.argument("topic", required=True)
def search(topic: str):
    click.echo(f"Searching for all the books related to topic {topic}...")
    try:
        #books = get_books(topic)
        books = [{"Item Number": 1, "Name": "Some random name."}]
    except Exception as e:
        click.echo(f"Failed - {str(e)}", err=True)
        return
    click.echo(books)
    

@click.command()
@click.argument("item_number", required=True)
def buy(item_number: int):
    click.echo(f"Looking up item number {item_number}...")
    try:
        #book = get_book(item_number)
        book = {"Item Number": item_number, "Name": "Some random name."}
    except Exception as e:
        click.echo(f"Failed - {str(e)}", err=True)
        return
    click.echo("Hooray! You bought the book.")
    click.echo(book)

bookstore.add_command(lookup)
bookstore.add_command(search)
bookstore.add_command(buy)

if __name__ == '__main__':
    bookstore()

