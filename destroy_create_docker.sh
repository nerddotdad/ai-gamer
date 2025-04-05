#! /bin/bash

delete_deploy() {
    kubectl delete -f ai-model-deployment.yaml
}

build_docker_image() {
    docker build -t nerddotdad/ai-gamer:latest .
    if (( $? == 0 )); then return 0; else exit 1; fi
}

push_docker_image() {
    docker push nerddotdad/ai-gamer:latest
    if (( $? == 0 )); then return 0; else exit 1; fi
}

create_deploy() {
    kubectl apply -f ai-model-deployment.yaml
    if (( $? == 0 )); then return 0; else exit 1; fi
}


delete_deploy
build_docker_image
push_docker_image
create_deploy