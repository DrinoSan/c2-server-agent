import os
import pickle
from collections import OrderedDict

def readFromDatabase(database):
    data = []

    with open(database, 'rb') as d:
        while True:
            try:
                data.append(pickle.load(d))
            except EOFError:
                break

    return data

def writeToDatabase(database,newData):
    with open(database, "ab") as d:
        pickle.dump(newData, d, pickle.HIGHEST_PROTOCOL)

def removeFromDatabase(database,name):
    data = readFromDatabase(database)
    final = OrderedDict()

    for i in data:
        final[i.name] = i

    del final[name]

    with open(database, "wb") as d:
        for i in final:
            pickle.dump(final[i], d , pickle.HIGHEST_PROTOCOL)

def clearDatabase(database):

    if os.path.exists(database):
        os.remove(database)
    else:
        pass
