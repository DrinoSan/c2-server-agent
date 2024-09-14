from collections import OrderedDict
from shutil import rmtree

from common import *
import db

agentsDB = "data/databases/agents.db"

class AgentManager:
    def __init__(self):
        self.agents = OrderedDict()

    def updateAgents(self):
        data = db.readFromDatabase(agentsDB)

        for agent in data:
            self.agents[agent.name] = agent


    def checkAgentsEmpty(self):
        self.updateAgents()

        if len(self.agents) == 0:
            return True

        return False

    def viewAgents(self):
        if self.checkAgentsEmpty() == True:
            error("No agents running")
            return

        success("Active Agents:")

        print(YELLOW)
        print(" Name                         Listener                         External IP                         Hostname")
        print("------                       ----------                       -------------                       ----------")

        for i in self.agents:
            print(" {}".format(self.agents[i].name) + " " * (29 - len(self.agents[i].name)) + "{}".format(self.agents[i].listener) + " " * (33 - len(self.agents[i].listener)) + self.agents[i].remoteIP + " " * (36 - len(self.agents[i].remoteIP)) + self.agents[i].hostname)

        print(cRESET)

    def isValidAgent(self, name, s):
        self.updateAgents()
        vAgents = []
        for agent in self.agents:
            vAgents.append(self.agents[agent].name)

        if name in vAgents:
            return True
        else:
            if s == 1:
                error("Invalid agent.")
                return False
            else:
                return False

    def removeAgent(self,args):
        if len(args) != 1:
            error("Invalid arguments.")
        else:
            name = args[0]
            if self.isValidAgent(name, 1):
                self.taskAgentToQuit(name)
                rmtree(self.agents[name].Path)
                db.removeFromDatabase(agentsDB,name)
                self.updateAgents()
            else:
                pass

    def renameAgent(self,args):
        if len(args) != 2:
            error("Invalid arguments.")
            return 0

        name    = args[0]
        newname = args[1]

        if self.isValidAgent(name, 1) == True:
            if self.isValidAgent(newname, 0) == True:
                error("Agent {} already exists.".format(newname))
                return 0

            self.agents[name].rename(newname)

            if os.path.exists(self.agents[name].Path):
                rmtree(self.agents[name].Path)

            db.removeFromDatabase(agentsDB, name)
            self.agents[name].name = newname
            self.agents[name].update()
            db.writeToDatabase(agentsDB, self.agents[name])

            self.updateAgents()

        else:
            return 0


    def taskAgentToQuit(self,name):
        self.agents[name].Quit()

    def addAgent(self,agent):
        print("Adding agent to agents list")
        self.agents[agent.name] = agent

    def interactWithAgent(self,args):
        if len(args) != 1:
            error("Invalid arguments.")
            return

        name = args[0]
        if name not in self.agents:
            error("Agent {} not present, check spelling".format(name))
            return

        self.agents[name].interact()
