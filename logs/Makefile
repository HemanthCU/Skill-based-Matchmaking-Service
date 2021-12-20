VERSION=v1
DOCKERUSER=hemanthcu

#
# You should probably update the docker.io user if you update this
#

build:
	docker build -f Dockerfile -t matchmaker-logs  .
push:
	docker tag matchmaker-logs  $(DOCKERUSER)/matchmaker-logs:$(VERSION)
	docker push $(DOCKERUSER)/matchmaker-logs:$(VERSION)
	docker tag matchmaker-logs  $(DOCKERUSER)/matchmaker-logs:latest
	docker push $(DOCKERUSER)/matchmaker-logs:latest