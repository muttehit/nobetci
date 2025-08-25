import logging
from app.config import ACCEPTED, BAN_LAST_USER, DEFAULT_LIMIT, IUL, STL
from app.db.models import UserLimit
from app.models.user import User
from app.nobetnode import nodes
from app.notification.telegram import send_notification
from app.storage.base import BaseStorage
from app.db.db_base import DBBase

logger = logging.getLogger(__name__)


class CheckService:

    def __init__(self, storage: BaseStorage, specify_limit_db: DBBase):
        self._storage = storage
        self._specify_limit_db = specify_limit_db
        self._in_process_ips = []
        self.repeated_out_of_limits = []

    async def check(self, user: User):
        specify_user = self._specify_limit_db.get(
            UserLimit.name == user.name)

        user_limit = specify_user.limit if specify_user is not None else DEFAULT_LIMIT

        if user_limit == 0:
            return

        self._storage.add_user(user)

        users = self._storage.get_users(user.name)

        if len(users) > user_limit and user.ip not in self._in_process_ips:
            userByEmail = self._storage.get_user(user.name)
            userLast = self._storage.get_last_user(user.name)

            if userByEmail is None:
                return

            self.repeated_out_of_limits.append(user)

            rl_lenth = len(list(filter(lambda x: x.name == userByEmail.name and x.ip ==
                           userByEmail.ip, self.repeated_out_of_limits)))
            rl_last_lenth = len(list(filter(
                lambda x: x.name == userLast.name and x.ip == userLast.ip, self.repeated_out_of_limits)))

            if rl_lenth < STL or rl_last_lenth < STL:
                if abs(rl_lenth-rl_last_lenth) > IUL:
                    self.repeated_out_of_limits = [
                        r for r in self.repeated_out_of_limits if r.name != userByEmail.name and r.ip != userByEmail.ip]
                    self.repeated_out_of_limits = [
                        r for r in self.repeated_out_of_limits if r.name != user.name and r.ip != user.ip]
                    self._storage.delete_user(userByEmail.name, userByEmail.ip)
                return
            self.repeated_out_of_limits = [
                r for r in self.repeated_out_of_limits if r.name != userByEmail.name and r.ip != userByEmail.ip]
            self.repeated_out_of_limits = [
                r for r in self.repeated_out_of_limits if r.name != user.name and r.ip != user.ip]

            self._in_process_ips.append(userByEmail.ip)

            await self.ban_user(userLast if BAN_LAST_USER else userByEmail)

            self._in_process_ips.remove(userByEmail.ip)

            self._storage.delete_user(userByEmail.name, userByEmail.ip)

            log_message = 'banned user ' + userByEmail.name+" with ip " + userByEmail.ip + \
                '\nnode: '+userByEmail.node + "\ninbound: "+userByEmail.inbound
            if ACCEPTED:
                log_message += '\naccepted: '+userByEmail.accepted
            logger.info(log_message)
            await send_notification(log_message)

    async def ban_user(self, user: User):
        for node in nodes.keys():
            try:
                await nodes[node].BanUser(user)
            except Exception as err:
                logger.error('error: ', err)
