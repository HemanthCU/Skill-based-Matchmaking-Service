VERSION=v1
DOCKERUSER=hemanthcu

#
# You should probably update the docker.io user if you update this
#

build:
	docker build -f DockerFile -t matchmaker-game-runner  .
push:
	docker tag matchmaker-game-runner  $(DOCKERUSER)/matchmaker-game-runner:$(VERSION)
	docker push $(DOCKERUSER)/matchmaker-game-runner:$(VERSION)
	docker tag matchmaker-game-runner  $(DOCKERUSER)/matchmaker-game-runner:latest
	docker push $(DOCKERUSER)/matchmaker-game-runner:latest