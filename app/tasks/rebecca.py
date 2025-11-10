import asyncio
import logging
from app.config import PANEL_ADDRESS, PANEL_CUSTOM_NODES, PANEL_PASSWORD, PANEL_USERNAME, SYNC_WITH_PANEL
from app.db.rebecca_db import RebeccaDB
from app.models.node import NodeStatus
from app.models.panel import Panel
from app.service.check_service import CheckService
from app.service.rebecca_service import RebeccaService, TASKS
from app import user_limit_db, storage
from app.tasks.nodes import nodes_startup
from app.utils.panel.rebecca_panel import get_rebecca_nodes, get_token
from app.db import models, node_db

logger = logging.getLogger(__name__)


async def start_rebecca_node_tasks():
    paneltype = Panel(
        username=PANEL_USERNAME,
        password=PANEL_PASSWORD,
        domain=PANEL_ADDRESS,
    )

    node_service = RebeccaService(CheckService(
        storage, SYNC_WITH_PANEL and RebeccaDB(await get_token(paneltype)) or user_limit_db))

    rebecca_nodes = await get_rebecca_nodes(paneltype, SYNC_WITH_PANEL)

    if PANEL_CUSTOM_NODES:
        rebecca_nodes = [
            m for m in rebecca_nodes if m.name in PANEL_CUSTOM_NODES]

    await nodes_startup(node_db.get_all(True) + (SYNC_WITH_PANEL and [models.Node(**{
        "id": 1000 + n.id,
        "name": n.name,
        "address": n.address,
        "port": n.nobetci_port,
        "status": NodeStatus.unhealthy,
        "message": ""
    }) for n in rebecca_nodes] or []))

    async with asyncio.TaskGroup() as tg:
        (not PANEL_CUSTOM_NODES or 'core' in PANEL_CUSTOM_NODES) and await node_service.create_core_task(paneltype, tg)

        for rebecca_node in rebecca_nodes:
            await node_service.create_node_task(paneltype, tg, rebecca_node)
        tg.create_task(
            node_service.handle_cancel_all(TASKS, paneltype),
            name="cancel_all",
        )
