import unittest
from unittest.mock import Mock
from pyexpose.providers.serveo import ServeoConnector
from unittest import IsolatedAsyncioTestCase

class TestServeo(IsolatedAsyncioTestCase):
    def setUp(self):
        self.serveo = ServeoConnector()
        # enable_logging()

    async def test_connect(self):
        async with self.serveo.connect() as session:
            assert session is not None

    async def test_forward_http(self):
        async with self.serveo.connect() as session:
            async with session.tunnel(8080) as tunnel:
                assert tunnel.ip is not None
                assert tunnel.port is not None
                assert "serveo.net" in tunnel.ip

if __name__ == '__main__':
    unittest.main()
