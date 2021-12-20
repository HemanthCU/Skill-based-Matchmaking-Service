#
# Matchmaker server
#
import pickle
import platform
import io
import os
import sys
import pika
import redis
import hashlib
import json
import requests
import bisect

from flair.models import TextClassifier
from flair.data import Sentence


hostname = platform.node()

##
## Configure test vs. production
##
redisHost = os.getenv("REDIS_HOST") or "localhost"
rabbitMQHost = os.getenv("RABBITMQ_HOST") or "localhost"

print(f"Connecting to rabbitmq({rabbitMQHost}) and redis({redisHost})")

##
## Set up redis connections
##
db = redis.Redis(host=redisHost, db=1)                                                                           

##
## Set up rabbitmq connection
##
rabbitMQ = pika.BlockingConnection(
        pika.ConnectionParameters(host=rabbitMQHost))
rabbitMQChannel = rabbitMQ.channel()

rabbitMQChannel.queue_declare(queue='toMatchmaker')
rabbitMQChannel.queue_declare(queue='toPlayerDb')
rabbitMQChannel.queue_declare(queue='toWorker')
rabbitMQChannel.exchange_declare(exchange='logs', exchange_type='topic')

playerList = []
gameId = 1

infoKey = f"{platform.node()}.worker.info"
debugKey = f"{platform.node()}.worker.debug"
def log_debug(message, key=debugKey):
    print("DEBUG:", message, file=sys.stdout)
    rabbitMQChannel.basic_publish(
        exchange='logs', routing_key=key, body=message)
def log_info(message, key=infoKey):
    print("INFO:", message, file=sys.stdout)
    rabbitMQChannel.basic_publish(
        exchange='logs', routing_key=key, body=message)

def getPlayerData(playerTag):
    print("Getting player data of " + playerTag + " from db")
    # Add player to queue after getting player data from redis
    req = {
        "reqType" : "getPlayerData",
        "playerTag" : playerTag
    }
    message = json.dumps(req)
    rabbitMQChannel.basic_publish(exchange='', routing_key='toPlayerDb', body=message.encode())

def getGameList():
    print("Attempting to create a game")
    global playerList
    threshhold = 3
    for i, playerData in enumerate(playerList):
        if i >= 3 and i <= len(playerList) - 3:
            minPlayerScore = int(playerList[i - 3][1])
            maxPlayerScore = int(playerList[i + 2][1])
            playerScore = int(playerData[1])
            if minPlayerScore >= playerScore - threshhold and maxPlayerScore <= playerScore + threshhold:
                gameList = playerList[i - 3:i + 3]
                playerList = [ele for ele in playerList if ele not in gameList]
                return gameList
    return None

def addPlayerAndProcessQueue(playerTag, playerScore):
    print("Adding player " + playerTag + " to the queue")
    global playerList
    global gameId
    playerData = (playerTag, playerScore)
    playerList.append(playerData)
    playerList.sort(key = lambda x: x[1])
    print("Current list of players in the queue in sorted order:")
    for player in playerList:
        print("Player = " + str(player[0]) + " Score = " + str(player[1]))
    if len(playerList) >= 6:
        gameList = getGameList()
        if gameList is None:
            print("No game can be formed with the current players in queue")
        else:
            newGameId = gameId
            gameId += 1
            newGameId = str(newGameId)
            if isinstance(newGameId, (bytes, bytearray)):
                newGameId = str(newGameId, 'UTF-8')
            print("Game initiated with game ID = " + newGameId)
            message = {
                "reqType" : "queuedGameData",
                "gameId" : newGameId,
                "playerList" : gameList
            }
            message1 = json.dumps(message)
            print("Sending list of players in the game with game ID = " + newGameId + " to the db and game runners")
            rabbitMQChannel.basic_publish(exchange='', routing_key='toPlayerDb', body=message1.encode())
            rabbitMQChannel.basic_publish(exchange='', routing_key='toWorker', body=message1.encode())

def onReceived(channel, methodFrame, headerFrame, body):
    request = json.loads(body)
    reqType = request['reqType']
    if (reqType in ['addPlayer']):    
        playerTag = request['playerTag']
        getPlayerData(playerTag)
    elif (reqType in ['playerData']):
        playerTag = request['playerTag']
        playerScore = request['playerScore']
        addPlayerAndProcessQueue(playerTag, playerScore)
    else:
        print("Invalid request")
    channel.basic_ack(delivery_tag=methodFrame.delivery_tag)

rabbitMQChannel.basic_consume('toMatchmaker', onReceived)
try:
    rabbitMQChannel.start_consuming()
except KeyboardInterrupt:
    rabbitMQChannel.stop_consuming()
rabbitMQChannel.close()