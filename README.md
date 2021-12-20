# Skill-based matchmaking service


The goal of my project is to create a service for online games to aggregate and group similarly skilled players into the same lobbies and run servers for the created lobbies. Subsequently, the results of these games should be stored back into the database when the game completes. The game itself is a placeholder for any massively multiplayer game over the internet where skill based matchmaking is required, which is becoming an increasingly common occurrence in today's internet driven world

Deploy the project locally by running deploy-local-dev.sh

Deploy it to GKE by running deploy-all.sh after running the following commands

```
gcloud config set compute/zone us-central1-b
gcloud container clusters create --preemptible mykube
```
And then running the following commands just before deploying the ingress
```
kubectl create clusterrolebinding cluster-admin-binding \
  --clusterrole cluster-admin \
  --user $(gcloud config get-value account)

kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.0.4/deploy/static/provider/cloud/deploy.yaml
gcloud container clusters update mykube --update-addons=HttpLoadBalancing=ENABLED
```

Further description of the project can be found in the attached written report and the following youtube video:
https://www.youtube.com/watch?v=GErmK6LQSTo
