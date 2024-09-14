import sys
import readline
from os import system
from collections import OrderedDict
from common import *
from managers import agentManager, listenerManager


class AutoComplete(object):
    def __init__(self, options):
        self.options = sorted(options)

    def complete(self, text, state):
        if state == 0:  # on first trigger, build possible matches
            if not text:
                self.matches = self.options[:]
            else:
                self.matches = [s for s in self.options
                                if s and s.startswith(text)]

        # return match indexed by state
        try:
            return self.matches[state]
        except IndexError:
            return None


class Menu:
    def __init__(self, name):
        self.name = name

        self.commands = OrderedDict()
        self.Commands = []

        self.commands["help"] = ["Show help.", ""]
        self.commands["home"] = ["Return home.", ""]
        self.commands["exit"] = ["Exit.", ""]

    # Functio to add a new menu element to collection
    def register_command(self, command, descr, args):
        self.commands[ command ] = [ descr, args ]

    # Function to show all available menu elements
    def showHelp(self):
        success("Avaliable commands: ")

        print(YELLOW)
        print(" Command                         Description                         Arguments")
        print("---------                       -------------                       -----------")

        for i in self.commands:
            print(" {}".format(i) + " " * (32 - len(i)) + "{}".format(self.commands[i][0]) + " " * (36 - len(self.commands[i][0])) + "{}".format(self.commands[i][1]))

        print(cRESET)

    # Function to clear current screen
    def clearScreen(self):
        system("clear")

    # Function to update Command array, needed for completer function
    def update_command(self):
        for command in self.commands:
            self.Commands.append( command )

    # Function to parse input with auto completion possible
    def parse(self):
        readline.set_completer(AutoComplete(self.Commands).complete)
        readline.parse_and_bind('bind ^I rl_complete')

        cmd = input(prompt(self.name))

        cmd = cmd.split()

        command = cmd[0]
        args = []

        for i in range(1,len(cmd)):
            args.append(cmd[i])

        return command, args

#------------------------------------------------------------------------------
############################
###### LISTENERS AREA ######
############################

def list_listeners():
    listenerManager.list_listeners()
def start_listener(args):
    listenerManager.start_listener(args)
def stop_listener(args):
    listenerManager.stop_listener(args)
def remove_listener(args):
    print("Called remove listener")

#------------------------------------------------------------------------------
def listeners_menu(command, args):
    if command == "help":
        Lmenu.showHelp()
    elif command == "home":
        home()
    elif command == "exit":
        Exit()
    elif command == "list":
        list_listeners()
    elif command == "start":
        start_listener(args)
    elif command == "stop":
        stop_listener(args)
    elif command == "remove":
        remove_listener(args)

#------------------------------------------------------------------------------
############################
###### AGENTS    AREA ######
############################
def viewAgents():
    agentManager.viewAgents()
def removeAgent(args):
    agentManager.removeAgent(args)
def renameAgent(args):
    agentManager.renameAgent(args)
def interactWithAgent(args):
    agentManager.interactWithAgent(args)

#------------------------------------------------------------------------------
def agents_menu(command, args):
    if command == "help":
        Amenu.showHelp()
    elif command == "home":
        home()
    elif command == "exit":
        Exit()
    if command == "list":
        viewAgents()
    elif command == "remove":
        removeAgent(args)
    elif command == "rename":
        renameAgent(args)
    elif command == "interact":
        interactWithAgent(args)


#------------------------------------------------------------------------------
def listeners_helper():
    Lmenu.clearScreen()
    while True:
        try:
            command, args = Lmenu.parse()
        except:
            continue

        if command not in listenersCommands:
            error("Invalid command.")
        else:
            listeners_menu(command, args)

#------------------------------------------------------------------------------
def agents_helper():
    Amenu.clearScreen()
    while True:
        try:
            command, args = Amenu.parse()
        except:
            continue

        if command not in agentCommands:
            error("Invalid command.")
        else:
            agents_menu(command, args)


#------------------------------------------------------------------------------
def home_menu(command, args):
    if command == "help":
        Hmenu.showHelp()
    elif command == "home":
        home()
    elif command == "exit":
        Exit()
    elif command == "agents":
        agents_helper()
    elif command == "listeners":
        listeners_helper()
    elif command == "payloads":
        print("Trying to acces payloads menu")
        #payloads_menu()


#------------------------------------------------------------------------------
def Exit():
    listenerManager.saveListeners()
    exit()

#------------------------------------------------------------------------------
def home():
    Hmenu.clearScreen()

    while True:
        # I need to continue on except to make sure the process is only closed with "exit" to save into db
        try:
            command, args = Hmenu.parse()
        except:
            continue

        if command not in homeCommands:
            error("Invalid command.")
        else:
            home_menu(command, args)


#------------------------------------------------------------------------------
Hmenu = Menu("c2")
Lmenu = Menu("listeners")
Amenu = Menu("agents")


#------------------------------------------------------------------------------
Hmenu.register_command("listeners", "Manage listeners.", "")
Hmenu.register_command("agents", "Manage active agents.", "")
Hmenu.register_command("payloads", "Generate payloads.", "")
Hmenu.update_command()
homeCommands = Hmenu.Commands

#------------------------------------------------------------------------------
Lmenu.register_command("list", "List active listeners.", "")
Lmenu.register_command("start", "Start a listener.", "<name> <port> <interface> | <name>")
Lmenu.register_command("stop", "Stop an active listener.","<name>")
Lmenu.register_command("remove", "Remove a listener.", "<name>")
Lmenu.update_command()
listenersCommands = Lmenu.Commands

#------------------------------------------------------------------------------
Amenu.register_command("list", "List active agents.", "")
Amenu.register_command("interact", "Interact with an agent.", "<name>")
Amenu.register_command("rename", "Rename agent.", "<agent> <new name>")
Amenu.register_command("remove", "Remove an agent.", "<name>")
Amenu.update_command()
agentCommands = Amenu.Commands
