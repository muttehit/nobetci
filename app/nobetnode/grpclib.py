import asyncio
import atexit
import logging
import ssl
import tempfile

from app.config import BAN_INTERVAL
from app.models.node import Node, NodeStatus
from app.models.user import User
from app.nobetnode.nobetnode_grpc import NobetServiceStub
from grpclib.client import Channel
from app.nobetnode.base import NobetNodeBase
from app.notification.telegram import send_notification
from .nobetnode_pb2 import User as PB2_User
from app.db import node_db
from app.db.models import Node as DbNode


logger = logging.getLogger(__name__)


def string_to_temp_file(content: str):
    file = tempfile.NamedTemporaryFile(mode="w+t")
    file.write(content)
    file.flush()
    return file


class NobetNodeGRPCLIB(NobetNodeBase):
    def __init__(
        self,
        node: Node,
        ssl_key: str,
        ssl_cert: str,
        usage_coefficient: int = 1,
    ):
        self.node = node
        self.id = node.id
        self.name = node.name
        self._address = node.address
        self._port = node.port

        self._key_file = string_to_temp_file(ssl_key)
        self._cert_file = string_to_temp_file(ssl_cert)

        ctx = ssl.create_default_context()
        ctx.load_cert_chain(self._cert_file.name, self._key_file.name)
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        self._channel = Channel(self._address, self._port, ssl=ctx)
        self._stub = NobetServiceStub(self._channel)
        self._monitor_task = asyncio.create_task(self._monitor_channel())
        self._streaming_task = None

        self._updates_queue = asyncio.Queue(1)
        self.synced = False
        self.usage_coefficient = usage_coefficient
        atexit.register(self._channel.close)

    async def BanUser(self, user: User):
        response = await self._stub.BanUser(PB2_User(
            ip=user.ip,
            banDuration=int(BAN_INTERVAL)
        ))
        logger.info(response)

        return response

    async def UnBanUser(self, user: User):
        response = await self._stub.UnBanUser(PB2_User(
            ip=user.ip
        ))
        logger.info(response)

        return response

    async def _monitor_channel(self):
        while state := self._channel._state:
            logger.debug("node %i channel state: %s", self.id, state.value)
            try:
                await asyncio.wait_for(self._channel.__connect__(), timeout=2)
            except Exception:
                node_db.update(DbNode.id == self.id, {
                               "status": NodeStatus.unhealthy})
                logger.debug("timeout for node, id: %i", self.id)
                await send_notification(f"timeout for node {self.name}, id: {self.id}")
                self.synced = False
            else:
                if not self.synced:
                    try:
                        ""
                    except:
                        pass
                    else:
                        self.synced = True
                        node_db.update(DbNode.id == self.id, {
                            "status": NodeStatus.healthy})
                        logger.info("Connected to node %i", self.id)
                        await send_notification(f"Connected to node {self.name}")
            await asyncio.sleep(10)

    def get_node(self):
        return self.node
