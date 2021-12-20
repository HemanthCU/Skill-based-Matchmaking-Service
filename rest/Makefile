VERSION=v4
DOCKERUSER=hemanthcu

build:
	docker build -f DockerFile -t matchmaker-rest .

push:
	docker tag matchmaker-rest $(DOCKERUSER)/matchmaker-rest:$(VERSION)
	docker push $(DOCKERUSER)/matchmaker-rest:$(VERSION)
	docker tag matchmaker-rest $(DOCKERUSER)/matchmaker-rest:latest
	docker push $(DOCKERUSER)/matchmaker-rest:latest
