import re
import asyncio
import asyncssh
from typing import AsyncIterator, Tuple
from abc import abstractmethod, ABC
from contextlib import asynccontextmanager

import pyexpose.base.tunnel
from pyexpose.base.logger import logger

class ExposeSession(ABC):
    """Wrapper around :class:`asyncssh.SSHClientConnection` that provides a context manager and 
    several utilities for interacting with the server, and tunnels.

    :ivar session: The underlying :class:`asyncssh.SSHClientConnection` that is used to communicate with the server.
    :vartype session: asyncssh.SSHClientConnection
    """
    def __init__(self, session: asyncssh.SSHClientConnection, stdin: asyncssh.stream.SSHWriter, stdout: asyncssh.stream.SSHReader, stderr: asyncssh.stream.SSHReader) -> None:
        """Initializes the session.

        :param session: The session to wrap around.
        :param stdin: The stdin stream.
        :param stdout: The stdout stream.
        :param stderr: The stderr stream.

        :type session: :class:`asyncssh.SSHClientConnection`
        :type stdin: :class:`asyncssh.stream.SSHWriter`
        :type stdout: :class:`asyncssh.stream.SSHReader`
        :type stderr: :class:`asyncssh.stream.SSHReader`
        """
        self.session = session
        self._stdin = stdin
        self._stdout = stdout
        self._stderr = stderr

    @abstractmethod
    async def parse_ip_port(self) -> Tuple[str, int]:
        """Parses the ip address and port from the server.

        :return: The ip address and port.
        :rtype: Tuple[:class:`str`, :class:`int`]
        """
        raise NotImplementedError("parse_ip_port is not implemented")

    @asynccontextmanager
    async def tunnel(self, local_port: int, local_host: str = 'localhost', remote_port: int = 80, remote_host: str = '') -> AsyncIterator[pyexpose.base.tunnel.ExposeTunnel]:
        """Creates a tunnel between the local and remote ports, this is equipvalent to running 
        the command `ssh -R <remote_host>:<remote_port>:<local_host>:<local_port> <server>`,
        which essentially forwards all the traffic from the remote_host:remote_port to the our
        local_host:local_port.

        :param local_port: The local port to forward traffic from. eg. 8080
        :param local_host: The local host to forward traffic from. eg. localhost
        :param remote_port: The remote port to forward traffic from to. eg. 80 means <server>:80 -> local_ip:local_port
        :param remote_host: The remote host to forward traffic from to. eg. <server>, or a custom domain. Defaults to '' (any).
        :type local_port: `int`
        :type local_host: `str`, optional
        :type remote_port: `int`, optional
        :type remote_host: `str`, optional

        :return: The listener that is listening for connections.
        :rtype: AsyncIterator[:class:`ExposeTunnel`]

        :raises: :class:`asyncssh.ChannelListenError` if the listener can't be opened or :class:`asyncio.TimeoutError` if <server> doesn't respond with the ip address and port.
                
        .. code-block:: python

            # Simple HTTP expose
            async with session.tunnel(8080) as tunnel:
    
        .. code-block:: python

            # Expose HTTPS (remote:443 -> localhost:8443)
            async with session.tunnel(8443, remote_port=443) as tunnel:
            
        .. code-block:: python

            # Tunnel TCP (remote:1234 -> localhost:2345)
            async with session.tunnel(2345, remote_port=1234) as tunnel:
            
        .. code-block:: python

            # Use custom subdomain/domain (if provider supports)
            async with session.tunnel(8080, remote_host="myreservedaddr.serveo.net") as tunnel:

        .. code-block:: python

            # Tunnel to something other than localhost, ie remote:443 -> notlocal:8080
            async with session.tunnel(8080, remote_port=443, local_host="notlocal") as tunnel:

        """
        async with self.session.forward_remote_port(remote_host, remote_port, local_host, local_port) as listener:
            ip, port = await self.parse_ip_port()

            logger.info(f"Forwarding {ip}:{port} -> {local_host}:{local_port}")

            yield pyexpose.base.tunnel.ExposeTunnel(ip, port, listener)

