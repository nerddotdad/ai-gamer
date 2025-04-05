#! /bin/bash

delete_deploy() {
    kubectl delete -f ai-gamer-minerl-navdense-deployment.yaml
}

build_docker_image() {
    docker build -t nerddotdad/ai-gamer-minerl-navdense:latest .
    if (( $? == 0 )); then return 0; else exit 1; fi
}

push_docker_image() {
    docker push nerddotdad/ai-gamer-minerl-navdense:latest
    if (( $? == 0 )); then return 0; else exit 1; fi
}

create_deploy() {
    kubectl apply -f ai-gamer-minerl-navdense-deployment.yaml
    if (( $? == 0 )); then return 0; else exit 1; fi
}

watch_log() {
    kubectl logs -f $(kubectl get pods | grep ai-gamer-minerl-navdense | awk '{print $1}')
    echo "watch logs"
    echo "kubectl logs -f $(kubectl get pods | grep ai-gamer-minerl-navdense | awk '{print $1}')"
}

delete_deploy
build_docker_image
push_docker_image
create_deploy
sleep 5
watch_log