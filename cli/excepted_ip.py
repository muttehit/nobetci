from typing import Optional
import typer

from rich.table import Table

from app.db.models import ExceptedIP

from . import utils
from app.db import excepted_ips


app = typer.Typer(no_args_is_help=True)


@app.command(name="list")
def list_excepted_ips(
    ip: Optional[str] = typer.Option(
        None, *utils.FLAGS["ip"], help="Search by ip(s)"
    ),
):
    ips = excepted_ips.get_all(
        ExceptedIP.name.contains(ip) if ip is not None else True)

    utils.print_table(
        table=Table(
            "ID",
            "IP"
        ),
        rows=[
            (
                str(ip.id),
                ip.ip,
            )
            for ip in ips
        ],
    )


@app.command(name="add")
def add(ip: str = typer.Option(None, *utils.FLAGS["ip"], prompt=True)):
    if excepted_ips.get(ExceptedIP.ip == ip):
        utils.error(f'{ip} is excepted.')
    excepted_ips.add({"ip": ip})
    utils.success(f'{ip} successfully excepted.')


@app.command(name="delete")
def delete(ip: str = typer.Option(None, *utils.FLAGS["ip"], prompt=True)):
    excepted_ips.delete(ExceptedIP.ip == ip)
    utils.success(f'{ip} successfully deleted.')
