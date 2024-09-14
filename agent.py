import os
import menu
from shutil import rmtree
import time

from common import *
import db

agents = []
agentsDB = "data/databases/agents.db"

class Agent:
    def __init__(self, agentName, listenerName, remoteIP, hostname, Type):
        self.name = agentName
        self.listener = listenerName
        self.remoteIP = remoteIP
        self.hostname = hostname
        self.Type = Type

        self.sleept    = 3
        self.Path      = "data/listeners/{}/agents/{}/".format(self.listener, self.name)
        self.tasksPath = "{}tasks".format(self.Path, self.name)

        if os.path.exists(self.Path) == False:
            os.mkdir(self.Path)

        self.menu = menu.Menu(self.name)

        self.menu.register_command("shell", "Execute a shell command.", "<command>")
        self.menu.register_command("sleep", "Change agent's sleep time.", "<time (s)>")
        self.menu.register_command("clear", "Clear tasks.", "")
        self.menu.register_command("quit", "Task agent to quit.", "")

        self.menu.update_command()

        self.Commands = self.menu.Commands


    def writeTask(self, task):
        if self.Type == "w":
            task = task

        with open(self.tasksPath, "w") as f:
            f.write(task)

    def clearTasks(self):
        if os.path.exists(self.tasksPath):
            os.remove(self.tasksPath)

    def update(self):
        self.menu.name = self.name
        self.Path      = "data/listeners/{}/agents/{}/".format(self.listener, self.name)
        self.tasksPath = "{}tasks".format(self.Path, self.name)

        if os.path.exists(self.Path) == False:
            os.mkdir(self.Path)

    def rename(self, newname):
        task    = "rename " + newname
        self.writeTask(task)

        progress("Waiting for agent.")
        while os.path.exists(self.tasksPath):
            error(f"Task path: {self.tasksPath} still exists")
            pass

        return 0


    def shell(self, args):
        if len(args) == 0:
            error("Missing command.")
            return

        command = " ".join(args)
        task    = "shell " + command

        error(f"Writing shell task: {task}")
        self.writeTask(task)


    def sleep(self, args):
        if len(args) != 1:
            error("Invalid arguments.")
            return

        time = args[0]
        try:
            temp = int(time)
        except:
            error("Invalid time.")
            return 0

        task = "sleep {}".format(time)
        self.writeTask(task)
        self.sleept = int(time)
        db.removeFromDatabase(agentsDB, self.name)
        db.writeToDatabase(agentsDB, self)

    def QuitandRemove(self):
        self.Quit()

        rmtree(self.Path)
        db.removeFromDatabase(agentsDB,self.name)

        menu.home()

        return 0

    def Quit(self):
        self.writeTask("quit")

        progress("Waiting for agent.")

        for i in range(self.sleept):
            if os.path.exists(self.tasksPath):
                time.sleep(1)
            else:
                break

        return 0

    def doThings( self, command, args ):
        if command == "help":
            self.menu.showHelp()
        elif command == "home":
            menu.home()
        elif command == "exit":
            menu.Exit()
        elif command == "shell":
            self.shell(args)
        elif command == "sleep":
            self.sleep(args)
        elif command == "clear":
            self.clearTasks()
        elif command == "quit":
            self.QuitandRemove()

    def interact(self):
        self.menu.clearScreen()

        while True:
            try:
                command, args = self.menu.parse()
            except:
                continue

            if command not in self.Commands:
                error("Invalid command.")
            else:
                self.doThings(command, args)
