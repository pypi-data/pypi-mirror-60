# players_amp
### written in Phyton 3.8.1 by Strolch

import json

import requests


class GetUpdates:

    def usercount(server, port, header, sessionids, instanceids):
        otherendpoint_part1 = "/API/ADSModule/Servers/"
        otherendpoint_part2 = "/API/Core/GetUpdates"

        rückgabe = 0
        i = 1
        while i < len(instanceids):  # not really matter if instanceids sessionids
            data = {'SESSIONID': sessionids[i], }
            post = requests.post(
                url=('http://' + server + ":" + port + otherendpoint_part1 + instanceids[i] + otherendpoint_part2),
                data=json.dumps(data), headers=header)
            post = json.loads(post.content)
            rückgabe += post.get('Status').get('UserCount')
            i += 1

        return rückgabe
