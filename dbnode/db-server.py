#
# DB server
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
playerdb = redis.Redis(host=redisHost, db=1)
gamedb = redis.Redis(host=redisHost, db=2, decode_responses=True)

##
## Set up rabbitmq connection
##
rabbitMQ = pika.BlockingConnection(
        pika.ConnectionParameters(host=rabbitMQHost))
rabbitMQChannel = rabbitMQ.channel()

rabbitMQChannel.queue_declare(queue='toMatchmaker')
rabbitMQChannel.queue_declare(queue='toPlayerDb')
rabbitMQChannel.exchange_declare(exchange='logs', exchange_type='topic')
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


def onReceived(channel, methodFrame, headerFrame, body):
    request = json.loads(body)
    reqType = request['reqType']
    if (reqType in ['getPlayerData']):
        playerTag = request['playerTag']
        playerScore = playerdb.get(playerTag)
        if playerScore is None:
            playerScore = "0"
            playerdb.set(playerTag, playerScore)
        if isinstance(playerScore, (bytes, bytearray)):
            playerScore = str(playerScore, 'UTF-8')
        respMessage = {
            "reqType" : "playerData",
            "playerTag" : playerTag,
            "playerScore" : playerScore
        }
        resp = json.dumps(respMessage)
        print("Returning player data of player = " + playerTag)
        rabbitMQChannel.basic_publish(exchange='', routing_key='toMatchmaker', body=resp.encode())
    elif (reqType in ['updateGameData']):
        playerList = request['playerList']
        for playerData in playerList:
            playerTag, gameScore = playerData[0], playerData[1]
            playerScore = playerdb.get(playerTag)
            playerScore = str(playerScore, 'UTF-8')
            if playerScore is None:
                playerScore = "0"
            playerScore1 = int(playerScore) + int(gameScore)
            playerScore = str(playerScore1)
            playerdb.set(playerTag, playerScore)
            print("Updated the score of " + playerTag + " to " + playerScore)
    elif (reqType in ['queuedGameData']):
        playerList = request['playerList']
        gameId = request['gameId']
        print("Stored the game data for game ID = " + gameId)
        for playerData in playerList:
            playerTag = playerData[0]
            gamedb.sadd(gameId, playerTag)
    channel.basic_ack(delivery_tag=methodFrame.delivery_tag)

rabbitMQChannel.basic_consume('toPlayerDb', onReceived)
try:
    rabbitMQChannel.start_consuming()
except KeyboardInterrupt:
    rabbitMQChannel.stop_consuming()
rabbitMQChannel.close()