# players_amp
### written in Phyton 3.8.1 by Strolch

import os.path
import re

from appdirs import user_config_dir

from players_amp import api_functions


def main():
    try:

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

        api_functions.Logout.instances(server, port, header, instanceids, sessionids)
        api_functions.Logout.main(server, port, header, sessionid)

        print(usercount)

    except:

        print("Unfortunately, there was an problem.")
        print("Please try it again with players_amp.debug to see the errors!")
        print("amp.debug uses no exception handling and prints more information")
