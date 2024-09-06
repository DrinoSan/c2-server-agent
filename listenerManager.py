from collections import OrderedDict
import netifaces

import db
from common import *
from listener import Listener

class ListenersManager:
    listenersDB = "data/databases/listeners.db"
    agentsDB    = "data/databases/agents.db"

    def __init__(self):
        self.listeners = OrderedDict()

    def getListenersFromDB(self):
        return db.readFromDatabase(self.listenersDB)

    def writeListenersToDB(self, listener):
        db.writeToDatabase(self.listenersDB, listener )

    def listenerExists(self, name):
        return name in self.listeners # i expect not many elements in list so its okay to check with in

    def list_listeners(self):
        if len(self.listeners) == 0:
            print("No listeners set")
            return;

        success("Active listeners:")

        print(YELLOW)
        print(" Name                         IP:Port                                  Status")
        print("------                       ------------------                       --------")

        for i in self.listeners:
            if self.listeners[i].isRunning == True:
                status = "Running"
            else:
                status = "Stopped"

            print(" {}".format(self.listeners[i].name) + " " * (29 - len(self.listeners[i].name)) + "{}:{}".format(self.listeners[i].ipaddress, str(self.listeners[i].port)) + " " * (41 - (len(str(self.listeners[i].port)) + len(":{}".format(self.listeners[i].ipaddress)))) + status)

        print(cRESET)

    def stop_listener(self, args):
        if len(args) != 1:
            print("Wrong number of arguments | stop <name>")
            return 0

        if self.listenerExists( args[0] ) == False:
            print(f"Listener {args[0]} does not exist")
            return 0

        self.listeners[args[0]].stop()

    def start_listener(self, args):
        if len(args) == 1:
            if self.listenerExists( args[0] ) == False:
                print("Listener does not exist, create a new one or check spelling")
                return 0
            print(f"starting Listener {args[0]}")
            # TODO: make listener start
            self.listeners[args[0]].start()
            return 0
        elif len(args) != 3:
            print("Invalid Number of arguments <name> <port> <interface>")
            return 0

        try:
            port = int(args[1])
        except:
            print("Invalid Port number")
            return 0

        name  = args[0]
        iface = args[2]

        if len(netifaces.ifaddresses(iface)[netifaces.AF_INET]) == 0:
            print("something is wrong with your IPv4")
            return 0

        ipv4 = netifaces.ifaddresses(iface)[netifaces.AF_INET][0]["addr"]

        if( self.listenerExists(name) == True ):
            print(f"Listener {name} already exists")
            return 0

        self.listeners[name] = Listener(name, port, ipv4)
        progress("Starting listener {} on {}:{}.".format(name, ipv4, str(port)))

        try:
            self.listeners[name].start()
            success("Listener started.")
        except:
            # Something is really going wrong we need to remove the listener...
            error("Failed. Check your options.")
            del self.listeners[name]
            return 0

        print(f"Starting Listener with name {args[0]} on port {args[1]} on interface {args[2]}")
