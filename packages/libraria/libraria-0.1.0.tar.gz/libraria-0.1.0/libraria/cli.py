import click

from . import SearchClient, limit, logger


@click.command()
@click.option("-m", "--max", type=int, default=10, help="The maximum number of results to return")
@click.argument("keyword")
def cli(max: int, keyword: str):
    """
    A tool for searching San Francison Bay Area Library system.
    """
    for result in limit(SearchClient().search(keyword=keyword), max):
        print(result)
