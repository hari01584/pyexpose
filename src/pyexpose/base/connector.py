import re
import asyncio
import logging
import asyncssh
from typing import AsyncIterator, Callable, Generic, TypeVar
from abc import abstractmethod, ABC
from contextlib import asynccontextmanager

import pyexpose.base
from pyexpose.base.logger import logger

ExposeSessionVar = TypeVar("ExposeSessionVar", bound="pyexpose.base.ExposeSession")

class ExposeConnector(ABC, Generic[ExposeSessionVar]):
    """A factory class that represents a connection to a tunneling servers.

    """

    @abstractmethod
    def get_factory(self) -> Callable[[], ExposeSessionVar]:
        """Returns a factory function that creates a new :class:`ExposeSessionVar` instance.

        :return: A factory function that creates a new :class:`ExposeSessionVar` instance.
        :rtype: Callable[[], :class:`ExposeSessionVar`]
        """
        raise NotImplementedError("get_factory is not implemented")

    @abstractmethod
    @asynccontextmanager
    async def open_connection(self) -> AsyncIterator[asyncssh.SSHClientConnection]:
        """Opens a connection to the server, Override this for creating new connectors

        :return: :class:`asyncssh.SSHClientConnection`
        :rtype: AsyncIterator[:class:`asyncssh.SSHClientConnection`]
        """
        raise NotImplementedError("open_connection is not implemented")

    @asynccontextmanager
    async def connect_with_connection(self, connection: asyncssh.SSHClientConnection) -> AsyncIterator[ExposeSessionVar]:
        """Connects to the server using an existing connection.

        :param connection: The connection to use.
        :type connection: :class:`asyncssh.SSHClientConnection`
        :return: :class:`ExposeSession` that wraps around :class:`asyncssh.SSHClientConnection`
        :rtype: AsyncIterator[:class:`ExposeSession`]

        .. code-block:: python
            :caption: This is how to setup custom ssh tunneling service by taking example of `https://localhost.run/`, Requiring SSH connection to be done like `ssh -R 80:localhost:8080 nokey@localhost.run`
            :emphasize-lines: 3

            import asyncssh
            async with asyncssh.connect('localhost.run', username="nokey", password="", known_hosts=None) as conn:
                async with connector.connect_with_connection(conn) as session:
                    session.tunnel(<args>)
                    ...

        """
        async with connection as conn:
            stdin, stdout, stderr = await conn.open_session()
            yield ExposeSessionVar(conn, stdin, stdout, stderr)

    @asynccontextmanager
    async def connect(self) -> AsyncIterator[ExposeSessionVar]:
        """Connects to the server, using the default settings.

        :return: :class:`ExposeSession` that wraps around :class:`asyncssh.SSHClientConnection`
        :rtype: AsyncIterator[:class:`ExposeSession`]

        .. code-block:: python
            :caption: Use specific providers from `pyexpose.providers.localhost_run.LocalRunConnector()` or `pyexpose.providers.serveo.ServeoConnector()`
        
            from pyexpose.providers.serveo import ServeoConnector
            connector = ServeoConnector()
            async with connector.connect() as session:
                async with session.tunnel(8080) as tunnel:
                    print("serveo.net exposed ip is " + tunnel.ip + " port is " + tunnel.port)

        """
        async with self.open_connection() as conn:
            stdin, stdout, stderr = await conn.open_session()
            yield self.get_factory()(conn, stdin, stdout, stderr)