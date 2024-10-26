from top_secret import secret
from datasets import import_data, export_csv
import requests
import typer


app = typer.Typer()


@app.command()
def top():
    return


@app.command()
def search():
    return


@app.command()
def salary():
    return


@app.command()
def skills():
    return


if __name__ == "__main__":
    app()
