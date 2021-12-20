VERSION=v1
DOCKERUSER=hemanthcu

#
# You should probably update the docker.io user if you update this
#

build:
	docker build -f DockerFile -t matchmaker-db  .
push:
	docker tag matchmaker-db  $(DOCKERUSER)/matchmaker-db:$(VERSION)
	docker push $(DOCKERUSER)/matchmaker-db:$(VERSION)
	docker tag matchmaker-db  $(DOCKERUSER)/matchmaker-db:latest
	docker push $(DOCKERUSER)/matchmaker-db:latest