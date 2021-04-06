import click
from book_requests import get_book, get_books_by_topic, buy_book

@click.group()
@click.argument("frontend_server", default="http://localhost:5002")
@click.pass_context
def bookstore(ctx, frontend_server: str):
    ctx.obj=f"http://{frontend_server}:5002"
    click.echo(f"Welcome to the World's Smallest Book Store!")

@click.command()
@click.argument("item_number", required=True)
@click.pass_context
def lookup(ctx, item_number: int):
    click.echo(f"Looking up item number {item_number}...")
    try:
        book = get_book(item_number, ctx.obj)
    except Exception as e:
        click.echo(str(e))
        return
    click.echo(book)

@click.command()
@click.option("--topic", required=True, help="The topic of the books to search for.")
@click.pass_context
def search(ctx, topic: str):
    click.echo(f"Searching for all the books related to topic {topic} ...")
    try:
        books = get_books_by_topic(topic, ctx.obj)
    except Exception as e:
        click.echo(str(e))
        return
    click.echo(books)
    

@click.command()
@click.argument("item_number", required=True)
@click.pass_context
def buy(ctx, item_number: int):
    click.echo(f"Looking up item number {item_number}...")
    try:
        book = buy_book(item_number, ctx.obj)
    except Exception as e:
        click.echo(str(e))
        return
    click.echo("Hooray! You bought the book.")
    click.echo(book)

bookstore.add_command(lookup)
bookstore.add_command(search)
bookstore.add_command(buy)

if __name__ == '__main__':
    FRONTEND_URL=""
    bookstore(obj=FRONTEND_URL)

