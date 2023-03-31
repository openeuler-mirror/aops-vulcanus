#!/bin/bash

copy_aops_conf(){
    echo "[INFO] Create the /etc/aops/ folder and copy conf to the aops directory."
    mkdir -p /etc/aops
    cp ./conf/*.ini /etc/aops
}

prepare_dockerfile_repo(){
    echo "[INFO] Create the repo file for the dockerfile folder."
    cp ./conf/*.repo ./aops-apollo/
    cp ./conf/*.repo ./aops-diana/
    cp ./conf/*.repo ./aops-zeus/
    cp ./conf/*.repo ./hermes/
}

storage_mysql_data(){
    echo "[INFO] Create a mysql storage directory."
    if [ ! -d /opt/mysql ]; then
        mkdir -p /opt/mysql/data
        mkdir -p /opt/mysql/msyql-files
        mkdir -p /opt/mysql/init
    fi 
}

storage_es_data(){
    echo "[INFO] Create a data store directory and a log store directory for the es."
    if [ ! -d /opt/es ]; then
        mkdir -p /opt/es/data
        mkdir -p /opt/es/logs
        chmod 777 -R /opt/es
    fi
}

prometheus(){
    echo "[INFO] Create the prometheus working directory."
    if [ ! -d /etc/prometheus ]; then
        mkdir -p /etc/prometheus
        mkdir -p /opt/prometheus/data
    fi 
    cp ./conf/prometheus.yml /etc/prometheus/
}

docker_build(){
    copy_aops_conf
    prepare_dockerfile_repo
    storage_mysql_data
    storage_es_data
    prometheus
    docker-compose -f docker-compose-base-service.yml build --no-cache
    docker-compose build --no-cache
    rm ./aops-apollo/*.repo
    rm ./aops-diana/*.repo
    rm ./aops-zeus/*.repo
    rm ./hermes/*.repo
}

install_docker_compose(){
    installed_docker_compose=`rpm -ql docker-compose`
    if [ "$(echo $installed_docker_compose | grep "is not installed")" != "" ]; then
        dnf install docker-compose -y
    fi
}

main(){
    
    install_docker_compose
    while :
    do
        echo "===========================Container arrangement==========================="
        echo "1. Build the docker container (build)."
        echo "2. Start the container orchestration service (start-service/start-env)."
        echo "3. Stop all container services (stop-service/stop-env)."
        read "Enter to exit the operation (Q/q)."
        read -p "Select an operation procedure to continue: " operation
        case $operation in
            "build")
                docker_build
                docker image prune
            ;;
            "start-service")
                docker-compose up -d
            ;;
            "start-env")
                docker-compose -f docker-compose-base-service.yml up -d
            ;;
            "stop-service")
                docker-compose down
            ;;
            "stop-env")
                docker-compose -f docker-compose-base-service.yml down 
            ;;
            "Q")
                break
            ;;
            "q")
                break
            ;;
        esac
    done
}

main