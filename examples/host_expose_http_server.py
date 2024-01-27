import asyncio
import threading
from http.server import ThreadingHTTPServer
from http.server import SimpleHTTPRequestHandler

class MyHttpRequestHandler(SimpleHTTPRequestHandler):
    def end_headers (self):
        self.send_header('Access-Control-Allow-Origin', '*')
        SimpleHTTPRequestHandler.end_headers(self)

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        html = f"31" # how do I modify this line to serve files?
        self.wfile.write(bytes(html, "utf8"))

http_server = ThreadingHTTPServer(("0.0.0.0", 4457), MyHttpRequestHandler)
http_server_thread = threading.Thread(target=http_server.serve_forever)
http_server_thread.daemon = True
http_server_thread.start()

async def start_tunnel():
    from pyexpose.providers.localhost_run import LocalRunConnector
    connector = LocalRunConnector()
    async with connector.connect() as session:
        async with session.tunnel(4457) as tunnel:
            print("Started tunnel, You can access your local server at: ", tunnel.ip)
            await asyncio.sleep(100000)

asyncio.run(start_tunnel())