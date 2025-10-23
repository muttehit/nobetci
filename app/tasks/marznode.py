import asyncio
from app.config import PANEL_ADDRESS, PANEL_CUSTOM_NODES, PANEL_PASSWORD, PANEL_USERNAME
from app.models.panel import Panel
from app.service.check_service import CheckService
from app.service.marznode_service import TASKS, MarzNodeService
from app.utils.panel import get_marznodes
from app import user_limit_db, storage

async def start_marznode_tasks():
    paneltype = Panel(
        username=PANEL_USERNAME,
        password=PANEL_PASSWORD,
        domain=PANEL_ADDRESS,
    )

    node_service = MarzNodeService(CheckService(
        storage, user_limit_db))

    marznodes = await get_marznodes(paneltype)

    if PANEL_CUSTOM_NODES:
        marznodes = [m for m in marznodes if m.name in PANEL_CUSTOM_NODES]

    async with asyncio.TaskGroup() as tg:
        for marznode in marznodes:
            await node_service.create_node_task(paneltype, tg, marznode)
        tg.create_task(
            node_service.handle_cancel_all(TASKS, paneltype),
            name="cancel_all",
        )