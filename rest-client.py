#!/usr/bin/env python3

import requests
import json
import os
import sys

#
# Use localhost & port 5000 if not specified by environment variable REST
#
REST = os.getenv("REST") or "34.117.188.46"

##
# The following routine makes a JSON REST query of the specified type
# and if a successful JSON reply is made, it pretty-prints the reply
##


def mkReq(reqmethod, endpoint, data):
    print(f"Response to http://{REST}/{endpoint} request is")
    jsonData = json.dumps(data)
    response = reqmethod(f"http://{REST}/{endpoint}", data=jsonData,
                         headers={'Content-type': 'application/json'})
    if response.status_code == 200:
        jsonResponse = json.dumps(response.json(), indent=4, sort_keys=True)
        print(jsonResponse)
        return
    else:
        print(
            f"response code is {response.status_code}, raw response is {response.text}")
        return response.text

loop = True

while loop:
    print("Enter the option:")
    print("a) addPlayer")
    print("b) showPlayerData")
    print("c) showGameData")
    print("d) exit")
    opt = input()
    if opt in ['a', 'A']:
        playerTag = input("Enter the player tag: ")
        mkReq(requests.post, "apiv1/addPlayer",
            data={
                "playerTag" : playerTag
            })
    elif opt in ['b', 'B']:
        playerTag = input("Enter the player tag: ")
        mkReq(requests.get, "apiv1/showPlayerData",
            data={
                "playerTag" : playerTag
            })
    elif opt in ['c', 'C']:
        gameId = input("Enter the game ID: ")
        mkReq(requests.get, "apiv1/showGameData",
            data={
                "gameId" : gameId
            })
    elif opt in ['d', 'D']:
        loop = False
    else:
        print("Invalid option")
sys.exit(0)
