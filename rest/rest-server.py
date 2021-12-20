##
from flask import Flask, request, Response, jsonify
import platform
import io, os, sys
import pika, redis
import hashlib, requests
import json

##
## Configure test vs. production
##
redisHost = os.getenv("REDIS_HOST") or "localhost"
rabbitMQHost = os.getenv("RABBITMQ_HOST") or "localhost"

print("Connecting to rabbitmq({}) and redis({})".format(rabbitMQHost,redisHost))

##
## Set up redis connections
##
playerdb = redis.Redis(host=redisHost, db=1, decode_responses=True)
gamedb = redis.Redis(host=redisHost, db=1, decode_responses=True)

##
## Set up rabbitmq connection
##
rabbitMQ = pika.BlockingConnection(
        pika.ConnectionParameters(host=rabbitMQHost))
rabbitMQChannel = rabbitMQ.channel()

rabbitMQChannel.queue_declare(queue='toMatchmaker')
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

app = Flask("Server")

@app.route("/apiv1/addPlayer", methods=['POST'])
def addPlayer():
    data = request.json
    message = json.dumps(data)
    message1 = {
        "reqType" : "addPlayer",
        "playerTag" : message['playerTag']
    }
    log_debug(f"Sending request {message}")
    rabbitMQChannel.basic_publish(exchange='', routing_key='toMatchmaker', body=message1.encode())

    return json.dumps({
        "action": "queued"
    })


@app.route("/apiv1/showPlayerData", methods=['GET'])
def showPlayerData():
    data = request.json
    message = json.dumps(data)
    playerTag = message['playerTag']
    playerScore = playerdb.get(playerTag)
    playerScore = str(playerScore)
    if isinstance(playerScore, (bytes, bytearray)):
        playerScore = str(playerScore, 'UTF-8')
    retMessage = "<p>The player score is " + playerScore + "</p>"
    return retMessage

@app.route("/apiv1/showGameData", methods=['GET'])
def showPlayerData():
    data = request.json
    message = json.dumps(data)
    gameId = message['gameId']
    gameList = gamedb.smembers(gameId)
    retMessage = "<p>The game " + gameId + " was played between:"
    for player in gameList:
        retMessage = retMessage + " " + player
    retMessage = retMessage + "</p>"
    return retMessage

@app.route('/', methods=['GET'])
def hello():
    return '<h1> Matchmaking Server</h1><p> Use a valid endpoint </p>'

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000)