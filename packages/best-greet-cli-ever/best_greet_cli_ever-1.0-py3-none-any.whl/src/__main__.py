import click
from src.greetings import say_hello

@click.command()
@click.option('--name', default=None, help='The name of the person you would like to greet')
def greet(name):
    click.echo(say_hello(name))