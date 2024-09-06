import os
import sys
import flask
from random import choice
from string import ascii_uppercase
from db import *
from common import *
import threading
from flask import request
from multiprocessing import Process

class Listener:

    def __init__(self, name, port, ipaddress):

        self.name       = name
        self.port       = port
        self.ipaddress  = ipaddress
        self.Path       = "data/listeners/{}/".format(self.name)
        self.filePath   = "{}files/".format(self.Path)
        self.agentsPath = "{}agents/".format(self.Path)
        self.isRunning  = False
        self.app        = flask.Flask(__name__)

        if os.path.exists(self.Path) == False:
            os.mkdir(self.Path)

        if os.path.exists(self.agentsPath) == False:
            os.mkdir(self.agentsPath)

        if os.path.exists(self.filePath) == False:
            os.mkdir(self.filePath)

        ####
        @self.app.route("/reg", methods=['POST'])
        def registerAgent():
            name     = ''.join(choice(ascii_uppercase) for i in range(6))
            remoteip = flask.request.remote_addr
            hostname = flask.request.form.get("name")
            Type     = flask.request.form.get("type")
            success("Agent {} checked in.".format(name))
            #TODO Create AgentsManager for agentsDB this is only a workaround
            #writeToDatabase(ListenersManager.agentsDB, Agent(name, self.name, remoteip, hostname, Type))
            return (name, 200)

        ####
        @self.app.route("/tasks/<name>", methods=['GET'])
        def serveTasks(name):
            if os.path.exists("{}/{}/tasks".format(self.agentsPath, name)):

                with open("{}{}/tasks".format(self.agentsPath, name), "r") as f:
                    task = f.read()
                    #clearAgentTasks(name)

                return(task,200)
            else:
                return ('',204)

        ####
        @self.app.route("/results/<name>", methods=['POST'])
        def receiveResults(name):
            result = flask.request.form.get("result")
            #displayResults(name, result)
            return ('',204)

        # Function for debug
        @self.app.route("/health", methods=['GET'])
        def health():
            success("HealthCheck works")
            return ('I am Alive',200)

        ####
        @self.app.route("/download/<name>", methods=['GET'])
        def sendFile(self,name):
            f    = open("{}{}".format(self.filePath, name), "rt")
            data = f.read()

            f.close()
            return (data, 200)

    def run(self):
        self.app.logger.disabled = True
        self.app.run(port=self.port, host=self.ipaddress, debug=True, use_reloader=False )

    def start(self):
        # self.server = Process(target=self.run)

        # cli = sys.modules['flask.cli']
        # cli.show_server_banner = lambda *x: None

        # self.daemon = threading.Thread(name = self.name,
        #                                target = self.server.start,
        #                                args = ())
        # self.daemon.daemon = True
        # self.daemon.start()

        # self.isRunning = True

        cli = sys.modules['flask.cli']
        cli.show_server_banner = lambda *x: None

        self.server_thread = threading.Thread(target=self.run)
        self.server_thread.daemon = True
        self.server_thread.start()
        self.isRunning = True

    def stop(self):
        pass
        # self.server.terminate()
        # self.server    = None
        # self.daemon    = None
        # self.isRunning = False
