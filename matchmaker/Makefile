VERSION=v1
DOCKERUSER=hemanthcu

build:
	docker buildx build -f DockerFile -t matchmaker-server . --platform=linux/amd64
push:
	docker tag matchmaker-server $(DOCKERUSER)/matchmaker-server:$(VERSION)
	docker push $(DOCKERUSER)/matchmaker-server:$(VERSION)
	docker tag matchmaker-server $(DOCKERUSER)/matchmaker-server:latest
	docker push $(DOCKERUSER)/matchmaker-server:latest

##
## The dirkcgrunwald/flair:latest container simply includes the FLAIR library
##

DOCKERUSER_FLAIR=dirkcgrunwald
build-base:
	docker build -f Dockerfile-flair -t flair .
push-base:
	docker tag flair $(DOCKERUSER_FLAIR)/flair:latest
	docker push $(DOCKERUSER_FLAIR)/flair:latest