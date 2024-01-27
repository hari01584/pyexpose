import re
import asyncio
import asyncssh
from contextlib import asynccontextmanager
from typing import AsyncIterator, Callable

import pyexpose.base.connector
import pyexpose.base.session
from pyexpose.base.logger import logger

class LocalRunSession(pyexpose.base.session.ExposeSession):
    """Session for localhost.run service
    """
    async def parse_ip_port(self):
        pattern = re.compile(r'(https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*))')
        # # Contiguously try to look into stdin to find out ip address and port
        line = await asyncio.wait_for(self._stdout.readuntil(pattern), timeout=10)
        match = pattern.search(line).groups()
        return match[0], 80

class LocalRunConnector(pyexpose.base.connector.ExposeConnector):
    """Connector to `localhost.run` service, It only supports HTTP/HTTPS endpoints right now

    .. code-block:: python

        from pyexpose.providers.localhost_run import LocalRunConnector
        connector = LocalRunConnector()
        async with serveo.connect() as session:
            async with session.tunnel(8080) as tunnel:
                print("localhost.run exposed ip is " + tunnel.ip)

    """
    def get_factory(self) -> Callable[[], LocalRunSession]:
        return LocalRunSession

    @asynccontextmanager
    async def open_connection(self) -> AsyncIterator[asyncssh.SSHClientConnection]:
        async with asyncssh.connect('localhost.run', username="nokey", password="", known_hosts=None) as conn:
            yield conn