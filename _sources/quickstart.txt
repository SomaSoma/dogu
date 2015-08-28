.. _quickstart-label: 

Quick Start
===========

Summary
-------

|  Since dogu is an implementation of dogu-interface, which is an extension of the WSGI, dogu can be used as a replacement of Werkzeug.
|  So any WSGI app will run on dogu with slight change.


Installation
------------

**pip install dogu**



Flask Example
-------------

::

    from dogu.server import start, set_server
    from flask import Flask
    from flask import request


    app = Flask(__name__)

    @app.route("/")
    def hello():
        print(request.environ)
        return "Hello World!"

    server_setting = set_server(
        app=app,
        use_ssl=True,
        crt_file='server.crt',
        key_file='server.key',
        debug=True,
        use_http2=True,
        keep_alive_timeout=40,
        workers=20
    )

    start([server_setting])

