import logging
from ssl import SSLError
from app.models.marznode import MarzNode
from app.models.panel import Panel
import httpx
import asyncio
import random

from app.notification.telegram import send_notification

logger = logging.getLogger(__name__)

async def get_token(panel_data: Panel) -> Panel | ValueError:
    payload = {
        "username": f"{panel_data.username}",
        "password": f"{panel_data.password}",
    }
    for attempt in range(20):
        for scheme in ["https","http"]:
            url = f"{scheme}://{panel_data.domain}/api/admins/token"
            try:
                async with httpx.AsyncClient(verify=False) as client:
                    response = await client.post(url, data=payload, timeout=5)
                    response.raise_for_status()
                json_obj = response.json()
                panel_data.token = json_obj["access_token"]
                return panel_data
            except httpx.HTTPStatusError:
                message = f"[{response.status_code}] {response.text}"
                await send_notification(message)
                logger.error(message)
                continue
            except SSLError:
                continue
            except Exception as error:
                message = f"An unexpected error occurred: {error}"
                await send_notification(message)
                logger.error(message)
                continue
        await asyncio.sleep(random.randint(2, 5) * attempt)
    message = (
        "Failed to get token after 20 attempts. Make sure the panel is running "
        + "and the username and password are correct."
    )
    await send_notification(message)
    logger.error(message)
    raise ValueError(message)

async def get_marznodes(panel_data: Panel) -> list[MarzNode] | ValueError:
    for attempt in range(20):
        get_panel_token = await get_token(panel_data)
        if isinstance(get_panel_token, ValueError):
            raise get_panel_token
        token = get_panel_token.token
        headers = {
            "Authorization": f"Bearer {token}",
        }
        all_nodes = []
        for scheme in ["https","http"]:
            url = f"{scheme}://{panel_data.domain}/api/nodes"
            try:
                async with httpx.AsyncClient(verify=False) as client:
                    response = await client.get(url, headers=headers, timeout=10)
                    response.raise_for_status()
                user_inform = response.json()
                for node in user_inform["items"]:
                    all_nodes.append(
                        MarzNode(
                            id=node["id"],
                            name=node["name"],
                            address=node["address"],
                            port=node['port'],
                            status=node["status"],
                            message=node["message"],
                        )
                    )
                return all_nodes
            except SSLError:
                continue
            except httpx.HTTPStatusError:
                message = f"[{response.status_code}] {response.text}"
                await send_notification(message)
                logger.error(message)
                continue
            except Exception as error:
                message = f"An unexpected error occurred: {error}"
                await send_notification(message)
                logger.error(message)
                print(message)
                continue
        await asyncio.sleep(random.randint(2, 5) * attempt)
    message = (
        "Failed to get nodes after 20 attempts. make sure the panel is running "
        + "and the username and password are correct."
    )
    await send_notification(message)
    logger.error(message)
    raise ValueError(message)

