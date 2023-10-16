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
    docker-compose build --no-cache
    rm ./aops-apollo/*.repo
    rm ./aops-diana/*.repo
    rm ./aops-zeus/*.repo
    rm ./hermes/*.repo
}

install_docker_compose(){
    docker_compose_installed=`rpm -q docker-compose`
    if [ $? -ne 0 ] ; then
        dnf install docker-compose -y
    else
        echo "docker-compose is already installed."
    fi
    docker_installed=`rpm -q docker`
    if [ $? -ne 0 ] ; then
        dnf install docker -y
    else
        echo "docker is already installed."
    fi
}

main(){
    install_docker_compose
    while :
    do
        echo "===========================Container arrangement==========================="
        echo "Welcome to the one-click deployment script, supporting pre-building of container images and start-stop of services."
        echo "Image Building (build): supports the generation of docker images for zeus, apollo, hermes services."
        echo "Service Start (start): the service types are divided into basic environment services and application services. Basic environment services include mysql, elasticsearch, redis, kafka, prometheus, which can be started by entering the 'start-env' option. Application services include apollo, zeus, hermes, which can be started by entering the 'start-service' option. please remember that, in the absence of a pre-existing environment, the correct order of using one-click startup services is to first execute "start-env" and then "start-service" Both steps are essential and cannot be skipped."
        echo "Stop Service (stop): enter 'stop-env' or 'stop-service' to stop the basic environment services and application services respectively. After the basic environment services are stopped, if the configuration items of the application services are not reconfigured, it will cause the application services to be unusable. Conversely, after stopping the application services, there is no impact on the basic environment services."
        echo "Enter to exit the operation (Q/q)."
        read -p "Please enter build, start-env, start-service, stop-env, stop-service, or q/Q to proceed to the next step: " operation
        case $operation in
            "build")
                docker_build
                docker image prune
            ;;
            "start-service")
                docker-compose up -d
                bash /opt/aops/scripts/aops-basedatabase.sh init zeus
                bash /opt/aops/scripts/aops-basedatabase.sh init apollo
            ;;
            "start-env")
                prometheus
                storage_es_data
                storage_mysql_data
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