#
# Game Runner
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
import random
import os
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
gamedb = redis.Redis(host=redisHost, db=2, decode_responses=True)                                                                           

##
## Set up rabbitmq connection
##
rabbitMQ = pika.BlockingConnection(
        pika.ConnectionParameters(host=rabbitMQHost))
rabbitMQChannel = rabbitMQ.channel()

rabbitMQChannel.queue_declare(queue='toPlayerDb')
rabbitMQChannel.queue_declare(queue='toWorker')
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
    if (reqType in ['queuedGameData']):
        gameId = request['gameId']
        gameId = str(gameId)
        if isinstance(gameId, (bytes, bytearray)):
            gameId = str(gameId, 'UTF-8')
        print("Game starting")
        print("Game ID = " + gameId)
        gameList = request['playerList']

        interList = []
        resList = []

        for player in gameList:
            randval = random.randrange(0, 1000, 1)
            interPlayer = (player[0], randval)
            interList.append(interPlayer)

        interList.sort(key = lambda x: x[1])

        for i, interPlayer in enumerate(interList):
            score = str(i)
            if isinstance(score, (bytes, bytearray)):
                score = str(score, 'UTF-8')
            resPlayer = (interPlayer[0], score)
            resList.append(resPlayer)

        print("Game results")
        for player in resList:
            print("player:")
            print(player[0])
            print("score:")
            print(player[1])
            print("\n")

        message = {
            "reqType" : "updateGameData",
            "playerList" : resList
        }
        message1 = json.dumps(message)
        rabbitMQChannel.basic_publish(exchange='', routing_key='toPlayerDb', body=message1.encode())
    else:
        print("Invalid request")
    channel.basic_ack(delivery_tag=methodFrame.delivery_tag)

rabbitMQChannel.basic_consume('toWorker', onReceived)
try:
    rabbitMQChannel.start_consuming()
except KeyboardInterrupt:
    rabbitMQChannel.stop_consuming()
rabbitMQChannel.close()