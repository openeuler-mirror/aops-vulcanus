#!/bin/bash
. ./install_aops.sh 
. ./install-aops-service.sh

function main(){
    echo -e "\nWelcome to one-click deployment of the aops.\n"
    while :
    do
        echo "===========================Menu==========================="
        echo "1. Install the agent client on a single or multiple machines."
        echo "2. Install the aops server."
        echo "Press q(Q) or another non-option key to exit."
        read -p "Select an operation procedure to continue: " step
        case $step in
            "1")
                install_agent_client
            ;;
            "2")
                install_aops_server
            ;;
            *)
                echo "Installation step is successfully exited."
                break
            ;;
        esac
    done
    
}

main