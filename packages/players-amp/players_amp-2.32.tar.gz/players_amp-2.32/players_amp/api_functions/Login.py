# players_amp
### written in Phyton 3.8.1 by Strolch

import json

import requests


class Login:

    # Logs into the mainpage and returns its sessionid
    def session_id(server, port, username, password, header):
        mainendpoint = "/API/Core/Login"
        data = {'username': username, 'password': password, 'token': "", 'rememberMe': 'false'}

        post = (
            requests.post(url=('http://' + server + ":" + port + mainendpoint), data=json.dumps(data), headers=header))

        return (json.loads(post.content).get('sessionID'))

    # Logs into all game server instances and return the sessionids within an array
    def session_ids(server, port, username, password, header, instanceids):
        otherendpoint_part1 = "/API/ADSModule/Servers/"
        otherendpoint_part2 = "/API/Core/Login"
        data = {'username': username, 'password': password, 'token': "", 'rememberMe': 'false'}

        i = 0
        rückgabe = []
        while i < len(instanceids):
            # logs into an game server instance and saves its sessionid into the array
            post = requests.post(
                url=('http://' + server + ":" + port + otherendpoint_part1 + instanceids[i] + otherendpoint_part2),
                data=json.dumps(data), headers=header)
            post = json.loads(post.content).get('sessionID')
            rückgabe.append(post)
            i += 1

        return rückgabe
