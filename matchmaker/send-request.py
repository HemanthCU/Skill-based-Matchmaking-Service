#!/usr/bin/env python3

#
# The example sends a single JSON formatted request to the worker
# using the RabbitMQ message queues assuming you are port-forwarding
# the requests to the host on which you run this.
#
# The request defines a model and a sentences list containing multiple sentences.
#
import io,os
import sys, platform
import pika
import json

#
# Unless you have set the RABBITMQ_HOST environment variable, use localhost
#
rabbitMQHost = os.getenv("RABBITMQ_HOST") or "localhost"

#
# This is the payload format used in the solution. It doesn't specify a callback,
# so you'll need to test that out another way or modify this example.
#

workerJson = {
    "reqType" : "addPlayer",
    "playerTag" : "123367"
}

rabbitMQ = pika.BlockingConnection(
    pika.ConnectionParameters(host=rabbitMQHost))
rabbitMQChannel = rabbitMQ.channel()

#
# Define or rabbitMQ queues / exchanges
#
rabbitMQChannel.queue_declare(queue='toMatchmaker')
rabbitMQChannel.exchange_declare(exchange='logs', exchange_type='topic')
infoKey = f"{platform.node()}.worker.info"
debugKey = f"{platform.node()}.worker.debug"
#
# A helpful function to send a log message
#
def log_debug(message, key=debugKey):
    print("DEBUG:", message, file=sys.stderr)
    rabbitMQChannel.basic_publish(
        exchange='logs', routing_key=key, body=message)

formattedJson = json.dumps(workerJson)
log_debug(f"Sending request {formattedJson}")
rabbitMQChannel.basic_publish(exchange='',routing_key='toMatchmaker', body=formattedJson)
