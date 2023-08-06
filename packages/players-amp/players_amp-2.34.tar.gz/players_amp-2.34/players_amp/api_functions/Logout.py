# players_amp
### written in Phyton 3.8.1 by Strolch

import json

import requests


class Logout:

    # logout mainpage
    def main(server, port, header, sessionid):
        mainendpoint = "/API/Core/Logout"
        data = {'SESSIONID': sessionid}

        Rückgabe = requests.post(url=('http://' + server + ":" + port + mainendpoint), data=json.dumps(data),
                                 headers=header)
        return Rückgabe

    # logout game server instances
    def instances(server, port, header, instanceids, sessionids):
        otherendpoint_part1 = "/API/ADSModule/Servers/"
        otherendpoint_part2 = "/API/Core/Logout"

        i = 1
        Rückgabe = []
        while i < len(instanceids):
            # an game server logout loop :D
            data = {'SESSIONID': sessionids[i]}
            post = requests.post(
                url=('http://' + server + ":" + port + otherendpoint_part1 + instanceids[i] + otherendpoint_part2),
                data=json.dumps(data), headers=header)
            Rückgabe.append(post)
            i += 1
        return Rückgabe
