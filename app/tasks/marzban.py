import asyncio
import logging
from app.config import PANEL_ADDRESS, PANEL_CUSTOM_NODES, PANEL_PASSWORD, PANEL_USERNAME
from app.models.panel import Panel
from app.service.check_service import CheckService
from app.service.marzban_service import MarzbanService
from app.service.marzban_service import TASKS
from app import user_limit_db, storage
from app.tasks.nodes import nodes_startup
from app.utils.panel.marzban_panel import get_marzban_nodes
from app.db import node_db

logger = logging.getLogger(__name__)


async def start_marzban_node_tasks():
    await nodes_startup(node_db.get_all(True))

    paneltype = Panel(
        username=PANEL_USERNAME,
        password=PANEL_PASSWORD,
        domain=PANEL_ADDRESS,
    )

    node_service = MarzbanService(CheckService(storage, user_limit_db))

    marzban_nodes = await get_marzban_nodes(paneltype)

    if PANEL_CUSTOM_NODES:
        marzban_nodes = [
            m for m in marzban_nodes if m.name in PANEL_CUSTOM_NODES]

    async with asyncio.TaskGroup() as tg:
        (not PANEL_CUSTOM_NODES or 'core' in PANEL_CUSTOM_NODES) and await node_service.create_core_task(paneltype, tg)

        for marzban_node in marzban_nodes:
            await node_service.create_node_task(paneltype, tg, marzban_node)
        tg.create_task(
            node_service.handle_cancel_all(TASKS, paneltype),
            name="cancel_all",
        )
