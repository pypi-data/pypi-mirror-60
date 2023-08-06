# players_amp
### written in Phyton 3.8.1 by Strolch

import json

import requests


class GetInstances:

    def instance_ids(server, port, header, sessionid):
        endpoint = "/API/ADSModule/GetInstances"
        data = {'SESSIONID': sessionid, }

        # makes an request, save the data as dict, and goes deep into it on the right level
        requestids = (
            requests.post(url=('http://' + server + ":" + port + endpoint), data=json.dumps(data), headers=header))
        requestids = json.loads(requestids.content)
        requestids = requestids.get('result')[0].get('AvailableInstances')

        # searches an suitable instanceid in loop, saves them into the array which it returns
        rückgabe = []
        i = 0
        while i < len(requestids):
            rückgabe.append(requestids[i]['InstanceID'])
            i += 1

        return rückgabe
