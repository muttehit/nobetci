import logging
import ssl
from ssl import SSLError
from app.config import PANEL_CUSTOM_NODES, PANEL_NODE_RESET
from app.models.panel import Panel
from app.models.rebecca_node import RebeccaNode
from app.notification.telegram import send_notification
from app.service.check_service import CheckService
import random
import websockets
import asyncio
from app.notification import reload_ad

from app.utils.panel.rebecca_panel import get_rebecca_nodes, get_token
from app.utils.parser import parse_log_to_user

logger = logging.getLogger(__name__)

TASKS = []

task_node_mapping = {}


class RebeccaService:

    def __init__(self, check_service: CheckService):
        self._check_service = check_service

    async def get_nodes_logs(self, panel_data: Panel, node: RebeccaNode) -> None:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        for scheme in ["wss", "ws"]:
            while True:
                interval = random.choice(("0.9", "1.3", "1.5", "1.7"))
                get_panel_token = await get_token(panel_data)
                if isinstance(get_panel_token, ValueError):
                    raise get_panel_token
                token = get_panel_token.token
                try:
                    url = f"{scheme}://{panel_data.domain}/api/node/{node.id}/logs?interval={interval}&token={token}"
                    async with websockets.connect(
                        url,
                        ssl=ssl_context if scheme == "wss" else None,
                    ) as ws:
                        log_message = (
                            "Establishing connection for"
                            + f" rebecca node number {node.id} name: {node.name}"
                        )
                        logger.info(log_message)
                        await send_notification(log_message)
                        while True:
                            logs = await ws.recv()
                            logs = logs.split('\n')
                            for log in logs:
                                log = parse_log_to_user(log)
                                if log:
                                    log.node = node.name
                                    asyncio.create_task(
                                        self._check_service.check(log))
                except SSLError:
                    break
                except Exception as error:
                    log_message = (
                        f"Failed to connect to this rebecca node [rebecca node id: {node.id}]"
                        + f" [rebecca node name: {node.name}]"
                        + f" [rebecca node ip: {node.address}] [rebecca node message: {node.message}]"
                        + f" [Error Message: {error}] trying to connect 10 second later!"
                    )
                    logger.error(log_message)
                    await send_notification(log_message)
                    await asyncio.sleep(10)
                    continue

    async def get_core_logs(self, panel_data: Panel) -> None:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        for scheme in ["wss", "ws"]:
            while True:
                interval = random.choice(("0.9", "1.3", "1.5", "1.7"))
                get_panel_token = await get_token(panel_data)
                if isinstance(get_panel_token, ValueError):
                    raise get_panel_token
                token = get_panel_token.token
                try:
                    url = f"{scheme}://{panel_data.domain}/api/core/logs?interval={interval}&token={token}"
                    async with websockets.connect(
                        url,
                        ssl=ssl_context if scheme == "wss" else None,
                    ) as ws:
                        log_message = (
                            "Establishing connection for"
                            + f" rebecca core"
                        )
                        logger.info(log_message)
                        await send_notification(log_message)
                        while True:
                            logs = await ws.recv()
                            logs = logs.split('\n')
                            for log in logs:
                                log = parse_log_to_user(log)
                                if log:
                                    log.node = "core"
                                    asyncio.create_task(
                                        self._check_service.check(log))
                except SSLError:
                    break
                except Exception as error:
                    log_message = (
                        f"Failed to connect to this rebecca core"
                        + f" [Error Message: {error}] trying to connect 10 second later!"
                    )
                    logger.error(log_message)
                    await send_notification(log_message)
                    await asyncio.sleep(10)
                    continue

    async def handle_cancel_all(self, tasks: list[asyncio.Task], panel_data: RebeccaNode) -> None:
        async with asyncio.TaskGroup() as tg:
            while True:
                await asyncio.sleep(PANEL_NODE_RESET)
                reload_ad()
                for task in tasks:
                    logger.info(f"Cancelling {task.get_name()}...")
                    task.cancel()
                    tasks.remove(task)

                (not PANEL_CUSTOM_NODES or 'core' in PANEL_CUSTOM_NODES) and asyncio.create_task(
                    self.create_core_task(panel_data, tg))

                rebecca_nodes = await get_rebecca_nodes(panel_data)
                if PANEL_CUSTOM_NODES:
                    rebecca_nodes = [
                        m for m in rebecca_nodes if m.name in PANEL_CUSTOM_NODES]
                for rebecca_node in rebecca_nodes:
                    asyncio.create_task(self.create_node_task(
                        panel_data, tg, rebecca_node))
                    await asyncio.sleep(3)

    async def create_node_task(self,
                               panel_data: Panel, tg: asyncio.TaskGroup, node: RebeccaNode
                               ) -> None:
        task = tg.create_task(
            self.get_nodes_logs(panel_data, node), name=f"Task-{node.id}-{node.name}"
        )
        TASKS.append(task)
        task_node_mapping[task] = node

    async def create_core_task(self,
                               panel_data: Panel, tg: asyncio.TaskGroup
                               ) -> None:
        task = tg.create_task(
            self.get_core_logs(panel_data), name=f"Task-0-core"
        )
        TASKS.append(task)
