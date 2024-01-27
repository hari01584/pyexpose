import re
import asyncio
import asyncssh
from contextlib import asynccontextmanager
from typing import AsyncIterator, Callable

import pyexpose.base.connector
import pyexpose.base.session

class ServeoSession(pyexpose.base.session.ExposeSession):
    """Session for serveo
    """
    async def parse_ip_port(self):
        pattern = re.compile(r'Forwarding .*? from (.*)[:(\d+)]?')
        # # Contiguously try to look into stdin to find out ip address and port
        line = await asyncio.wait_for(self._stdout.readuntil(pattern), timeout=10)
        match = pattern.search(line).groups()

        # Get the ip address and port from the regex
        if len(match) == 2:
            ip, port = match # Tcp forward
        else:
            ip, port = match[0], 80 # Http forward
        
        return ip, int(port)

class ServeoConnector(pyexpose.base.connector.ExposeConnector):
    """Provider to connect to `serveo.net`, a free ssh tunneling service.
    
    .. code-block:: python

        from pyexpose.providers.serveo import ServeoConnector
        connector = ServeoConnector()
        async with connector.connect() as session:
            async with session.tunnel(8080) as tunnel:
                print("serveo.net exposed ip is " + tunnel.ip)

    """
    def get_factory(self) -> Callable[[], ServeoSession]:
        return ServeoSession

    @asynccontextmanager
    async def open_connection(self) -> AsyncIterator[asyncssh.SSHClientConnection]:
        async with asyncssh.connect('serveo.net', password="", known_hosts=None) as conn:
            yield conn