Welcome to pyexpose's documentation!
====================================

pyexpose is a Python library designed to streamline the process of exposing local services
to the internet using various SSH-based providers, such as serveo.net and localhost.run.

With pyexpose, developers can effortlessly share their local services with remote collaborators or external systems,
eliminating the need for manual configuration and exposing an abstraction layer for seamless integration.

Installation
------------

Install the ``pyexpose`` package with `pip
<https://pypi.org/project/pyexpose>`_:

.. code-block:: console

    $ pip install pyexpose

Or install the latest package directly from github
the ``async`` extra:

.. code-block:: console

    $ pip install git+https://github.com/hari01584/pyexpose

Example Usage
-------------

.. code-block:: python

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

See more usage and sample codes in package documentations and examples

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   pyexpose.base
   pyexpose.providers

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`