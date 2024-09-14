import sys
import logging
import os

from menu import home
from menu import listenerManager

def main():

	if os.path.exists("./data/") == False:
		os.mkdir("./data/")

	if os.path.exists("./data/listeners/") == False:
		os.mkdir("./data/listeners/")

	if os.path.exists("./data/databases/") == False:
		os.mkdir("./data/databases/")

	log = logging.getLogger('werkzeug')
	log.disabled = True

	listenerManager.loadListeners()
	listenerManager.agentManager.updateAgents()

	home()

if __name__ == "__main__":
    main()
