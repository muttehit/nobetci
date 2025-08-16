from typing import List, Optional
import typer

from rich.table import Table

from app.db.models import UserLimit
from app.models.user import User
from app.nobetnode import nodes

from . import utils
from app import user_limit_db


app = typer.Typer(no_args_is_help=True)


@app.command(name="list")
def list_users(
    name: Optional[str] = typer.Option(
        None, *utils.FLAGS["name"], help="Search by name(s)"
    ),
):
    users = user_limit_db.get_all(
        UserLimit.name.contains(name) if name is not None else True)

    utils.print_table(
        table=Table(
            "ID",
            "Name",
            "Limit"
        ),
        rows=[
            (
                str(user.id),
                user.name,
                str(user.limit)
            )
            for user in users
        ],
    )


@app.command(name="add")
def add(name: str = typer.Option(None, *utils.FLAGS["name"], prompt=True),
        limit: int = typer.Option(None, *utils.FLAGS["limit"], prompt=True)):
    user_limit_db.add({"name": name, "limit": limit})
    utils.success(f'{name}\'s limit successfully set to "{limit}".')


@app.command(name="delete")
def delete(name: str = typer.Option(None, *utils.FLAGS["name"], prompt=True)):
    user_limit_db.delete(UserLimit.name == name)
    utils.success(f'{name}\'s limit successfully deleted.')


@app.command(name="update")
def update(name: str = typer.Option(None, *utils.FLAGS["name"], prompt=True),
           limit: int = typer.Option(None, *utils.FLAGS["limit"], prompt=True)):
    user_limit_db.update(UserLimit.name == name, {"limit": limit})
    utils.success(f'{name}\'s limit successfully set to "{limit}".')


@app.command(name="unban")
def unban(name: str = typer.Option(None, *utils.FLAGS["name"], prompt=True),
          ip: str = typer.Option(None, *utils.FLAGS["ip"], prompt=True)):
    for node in nodes.keys():
        try:
            nodes[node].UnBanUser(User(name=name, status=None, ip=ip, count=0))
        except Exception as err:
            utils.error(f'Cannot unban user {name} with ip {ip}.')
    utils.success(f'{name}\'s with ip {ip} unbanned successfully.')
