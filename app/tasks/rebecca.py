import asyncio
from app.config import PANEL_ADDRESS, PANEL_CUSTOM_NODES, PANEL_PASSWORD, PANEL_USERNAME
from app.models.panel import Panel
from app.service.check_service import CheckService
from app.service.rebecca_service import RebeccaService, TASKS
from app import user_limit_db, storage
from app.utils.panel.rebecca_panel import get_rebecca_nodes


async def start_rebecca_node_tasks():
    paneltype = Panel(
        username=PANEL_USERNAME,
        password=PANEL_PASSWORD,
        domain=PANEL_ADDRESS,
    )

    node_service = RebeccaService(CheckService(
        storage, user_limit_db))

    rebecca_nodes = await get_rebecca_nodes(paneltype)

    if PANEL_CUSTOM_NODES:
        rebecca_nodes = [
            m for m in rebecca_nodes if m.name in PANEL_CUSTOM_NODES]

    async with asyncio.TaskGroup() as tg:
        (not PANEL_CUSTOM_NODES or 'core' in PANEL_CUSTOM_NODES) and await node_service.create_core_task(paneltype, tg)

        for rebecca_node in rebecca_nodes:
            await node_service.create_node_task(paneltype, tg, rebecca_node)
        tg.create_task(
            node_service.handle_cancel_all(TASKS, paneltype),
            name="cancel_all",
        )
