# -*- coding:utf-8 -*-

import json
import os
import threading
import time

from tornado.web import RequestHandler
from tornado.websocket import WebSocketHandler, WebSocketClosedError


class PageHandler(RequestHandler):

    def get(self):
        """ Rendering templates/watch.html """

        host = self.settings["host"]
        port = self.settings["port"]
        url = "%s:%s" % (host, port)

        self.render("watch.html", url=url)


class WsHandler(WebSocketHandler):

    def check_origin(self, origin):
        return True


    def open(self):
        """ Websocket onopen """

        self.finished = False
        self.option = "play" # default option


    def on_message(self, params):
        """ Websocket onmessage
            Start the background thread to read the specified file
            and send the data to the browser

        :param params: The parameters requested by the browser
        :type params: dict
        """

        params = json.loads(params)

        if params["action"] == "watch":
            filePath = params["filePath"]

            if not os.path.isfile(filePath):
                return self.write_message("Invalid logfile.")
    
            threading.Thread(target=self.send_message, args=[filePath, ]).start()

        elif params["action"] == "control":
            self.option = params["option"]


    def send_message(self, filePath):
        """ read the specified file, send the data to the browser

        :param filePath: Specifies the file to be read
        :type filePath: str
        """

        with open(filePath, "rb") as fd:
            fd.seek(0, 2)
            position = fd.tell()
    
            try:
                while not self.finished:
                    if self.option == "play":
                        content = fd.readline()
    
                        if content:
                            self.write_message(content + b"\r")
    
                    elif self.option == "repeat":
                        self.option = "play"
                        fd.seek(position)     
    
                    time.sleep(0.05)
    
            except WebSocketClosedError:
                pass


    def on_close(self):
        """ Websocket onclose """

        self.finished = True

