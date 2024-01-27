import unittest
from unittest.mock import Mock
from pyexpose.base.logger import enable_logging
from pyexpose.providers.localhost_run import LocalRunConnector
from unittest import IsolatedAsyncioTestCase

class TestLocalRun(IsolatedAsyncioTestCase):
    def setUp(self):
        self.connector = LocalRunConnector()
        # enable_logging()

    async def test_connect(self):
        async with self.connector.connect() as session:
            assert session is not None

    async def test_forward_http(self):
        async with self.connector.connect() as session:
            async with session.tunnel(8080) as tunnel:
                assert tunnel.ip is not None
                assert tunnel.port is not None
                assert "lhr.life" in tunnel.ip

if __name__ == '__main__':
    unittest.main()
