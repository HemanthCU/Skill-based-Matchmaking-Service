#!/bin/sh
kubectl apply -f redis/redis-deployment.yaml
kubectl apply -f redis/redis-service.yaml
kubectl apply -f rabbitmq/rabbitmq-deployment.yaml
kubectl apply -f rabbitmq/rabbitmq-service.yaml

kubectl apply -f rest/rest-deployment.yaml
kubectl apply -f rest/rest-service.yaml

kubectl apply -f logs/logs-deployment.yaml

kubectl apply -f dbnode/db-deployment.yaml

kubectl apply -f matchmaker/matchmaker-deployment.yaml
kubectl apply -f worker/game-runner-deployment.yaml
kubectl apply -f ingress.yaml