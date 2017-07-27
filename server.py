# -*- coding:utf-8 -*-

import os
import sys

home = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, home)

try:
    from ConfigParser import ConfigParser
except ImportError:
    from configparser import ConfigParser

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.web import Application

from handlers.watch import PageHandler, WsHandler


class Server(Application):

    def __init__(self):
        """ Initialization Configration """

        cf = ConfigParser()
        cf.optionxform = str
        cf.read(home + "/etc/server.conf")

        self.host = cf.get("listen", "host")
        self.port = cf.getint("listen", "port")

        handlers = [
            (r"/", PageHandler),
            (r"/ws", WsHandler),
        ]

        settings = dict(
            host = self.host,
            port = self.port,
            static_path = os.path.join(home, "static"),
            template_path = os.path.join(home, "templates")
        )
        
        super(Server, self).__init__(handlers, **settings)


if __name__ == "__main__":
    app = Server()
    server = HTTPServer(app)
    server.listen(app.port, app.host)
    IOLoop.instance().start()
