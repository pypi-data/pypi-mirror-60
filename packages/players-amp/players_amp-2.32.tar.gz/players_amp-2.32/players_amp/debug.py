# players_amp
### written in Phyton 3.8.1 by Strolch

import os.path
import re

from appdirs import user_config_dir

from players_amp import api_functions


def debug():
    # reads settings.txt and save the data
    filename = "settings.txt"
    path = user_config_dir(appauthor="Strolch", appname="players_amp", roaming=False)
    filepath = os.path.join(path, filename)

    file = open(filepath, mode='r')
    settings = re.findall(r'"(.*?)"', file.read())
    file.close()

    server = settings[0]
    port = settings[1]
    username = settings[2]
    password = settings[3]
    header = {'Accept': 'application/json'}

    sessionid = api_functions.Login.session_id(server, port, username, password, header)
    instanceids = api_functions.GetInstances.instance_ids(server, port, header, sessionid)
    sessionids = api_functions.Login.session_ids(server, port, username, password, header, instanceids)
    usercount = api_functions.GetUpdates.usercount(server, port, header, sessionids, instanceids)

    print("session id (Mainpage): " + sessionid)

    i = 1
    while i < len(instanceids):
        print("instance id [" + str(i) + "]: " + instanceids[i])
        i += 1

    i = 1
    while i < len(sessionids):
        print("session id [" + str(i) + "]: " + sessionids[i])
        i += 1

    logouts = api_functions.Logout.instances(server, port, header, instanceids, sessionids)
    i = 0
    while i < len(logouts):
        if (logouts[i]).content == b'null':
            print("instance " + str(i) + " - Logout successful!")
        else:
            print("Error: instance " + str(i) + " - Logout UNSUCCESSFUL!")
        i += 1

    logout = api_functions.Logout.main(server, port, header, sessionid)
    if logout.content == b'null':
        print("Mainpage - Logout successful!")
    else:
        print("Error: Mainpage - Logout UNSUCCESSFUL!")

    print("playercount: " + usercount)
