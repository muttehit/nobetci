from typing import List, Optional
import typer

from rich.table import Table

from app.db.models import Node

from . import utils
from app.db import node_db, tls_db


app = typer.Typer(no_args_is_help=True)


@app.command(name="list")
def list_nodes(
    name: Optional[str] = typer.Option(
        None, *utils.FLAGS["name"], help="Search by name(s)"
    ),
):
    users = node_db.get_all(Node.name.contains(
        name) if name is not None else True)

    utils.print_table(
        table=Table(
            "ID",
            "Name",
            "address",
            "port",
            "status"
        ),
        rows=[
            (
                str(user.id),
                user.name,
                user.address,
                str(user.port),
                user.status
            )
            for user in users
        ],
    )


@app.command(name="add")
def add(name: str = typer.Option(None, *utils.FLAGS["name"], prompt=True),
        host: str = typer.Option(None, *utils.FLAGS["host"], prompt=True),
        port: int = typer.Option(None, *utils.FLAGS["port"], prompt=True)):
    node_db.add({"name": name, "address": host, "port": port,
                "status": "healthy", "message": ""})
    utils.success(
        f'Node with name {name} successfully added with "{host}:{port}".')


@app.command(name="delete")
def delete(id: str = typer.Option(None, *utils.FLAGS["id"], prompt=True)):
    node_db.delete(Node.id == id)
    utils.success(f'Node with id {id} successfully deleted.')


@app.command(name="settings")
def settings():
    typer.echo(typer.style(tls_db.get(True).cert), err=True)
