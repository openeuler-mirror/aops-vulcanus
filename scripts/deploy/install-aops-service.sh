#!/bin/bash
. ./aops-basedatabase.sh

function check_install_result(){
    rpm=$1
    installed_package=`rpm -ql $rpm`
    if [ "$(echo $installed_package | grep "is not installed")" != "" ]; then
        echo "[ERROR] Install $rpm failed!"
        return
    fi
    echo "[INFO] $rpm was successfully installed."
}

function install(){
    install_rpm=${1##*/}
    rpm=$(echo ${install_rpm%-*-*})
    echo "[INFO] Start install '$rpm' package."
    dnf localinstall $1 -y
    check_install_result $rpm
}

function default_openeuler_2203_repo(){
    cat >>/tmp/install-aops/repos/openEuler.repo <<EOF
[aops-install]
name=aops-install
baseurl=https://repo.openeuler.org/openEuler-22.03-LTS/update/$basearch
enabled=1
gpgcheck=1
gpgkey=https://repo.openeuler.org/openEuler-22.03-LTS/OS/$basearch/RPM-GPG-KEY-openEuler
EOF
}

function install_repo_pkg(){
    rpm_pkg=$1
    repo=$2
    if [ -z "$repo_file" ]; then
        repo=/tmp/install-aops/repos 
        default_openeuler_2203_repo
    fi
    dnf install -y $rpm_pkg --setopt=reposdir=$repo
    rm -rf /tmp/install-aops/repos/openEuler.repo
    check_install_result $rpm
}

function install_rpms(){
    echo "[INFO] The system starts to install the aops service software package."
    read -p "Enter the full path of the rpm to be installed or the folder where the rpm is stored: " install_rpm
    
    if [ -z "$install_rpm" ]; then
        echo "[ERROR] No valid rpm or folder was entered."
        return
    fi

    # 是存在的文件
    if [ -f $install_rpm ]; then
        install $install_rpm
    # 文件夹
    elif [ -d $install_rpm ]; then
        rpm_file_count=`ls $install_rpm/*.rpm -l | grep "^-" | wc -l`
        if [ "$(echo $rpm_file_count | grep "No such file or directory")" != "" ]; then
            echo "[WARNING] No rpm that meets the conditions exists in the directory."
            return
        fi
        for rpm in $install_rpm/*.rpm; do
		    install $rpm
        done
    # 需要安装的包名
    else
        read -p "Specify the repo source you want to use: " repo_file
        install_repo_pkg $install_rpm $repo_file
    fi
}

function update_aops_config(){
    read -p "Please enter the server ip address,if you need to bind 0.0.0.0, press Enter: " ip
    is_valid_ip $ip
    valid_ip=$?
    if [ "$valid_ip" != 0 ]; then
        echo "[WARNING] The entered ip address is null or invalid."
        return
    fi
    echo "[INFO] Configuration file of the aops service is update,default ip address binding is '$ip'."
    sed -i "/apollo/,/ip/c[apollo]\nip=$ip" /etc/aops/apollo.ini
    sed -i "/zeus/,/ip/c[zeus]\nip=$ip" /etc/aops/zeus.ini

    if [ "$ip" != "0.0.0.0" ]; then
        # 如果不是0.0.0.0的ip时，将zeus的连接替换
        sed -i "/zeus/,/ip/c[zeus]\nip=$ip" /etc/aops/apollo.ini
        sed -i "/apollo/,/ip/c[apollo]\nip=$ip" /etc/aops/zeus.ini
    fi
}

function is_valid_ip() {
    ip=$1
    valid_check=$(echo $ip|awk -F. '$1<=255&&$2<=255&&$3<=255&&$4<=255{print "yes"}')
    if echo $ip|grep -E "^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$">/dev/null; then
        if [ ${valid_check:-no} == "yes" ]; then
            echo "[INFO] IP $ip available."
            return 0
        else
            echo "[ERROR] IP $ip not available!"
            return 1
        fi
    else
        echo "[ERROR] IP format error!"
        return 1
    fi
}

function config_remote_database_service(){
    echo "[INFO] Config remote database service."
    read -p "Select whether you want to configure mysql or eleasticearch (mysql/elasticsearch): " database
    if [ "$database" != "mysql" ] && [ "$database" != "elasticsearch" ]; then
        echo "[WARNING] Database configuration can only be 'mysql' or 'elasticsearch'."
        return
    fi
    read -p "Remote database ip: " remote_ip
    is_valid_ip $remote_ip
    valid_ip=$?
    if [ "$remote_ip" == "0.0.0.0" ] || [ "$valid_ip" != 0 ]; then
        echo "[WARNING] The entered ip address is null or invalid."
        return
    fi
    read -p "Database port number: " database_port

    # mysql config
    if [ "$database" == "mysql" ]; then
        sed -i "/mysql/,/ip/c[mysql]\nip=$remote_ip" /etc/aops/apollo.ini
        sed -i "/mysql/,/ip/c[mysql]\nip=$remote_ip" /etc/aops/zeus.ini
        if [ "$database_port" != "" ]; then
            sed -i "/mysql/,/port/c[mysql]\nip=$remote_ip\nport=$database_port" /etc/aops/apollo.ini
            sed -i "/mysql/,/port/c[mysql]\nip=$remote_ip\nport=$database_port" /etc/aops/zeus.ini
        fi
        return
    fi

    # elasticsearch config
    if [ "$database" == "elasticsearch" ]; then
        sed -i "/elasticsearch/,/ip/c[elasticsearch]\nip=$remote_ip" /etc/aops/apollo.ini
        sed -i "/elasticsearch/,/ip/c[elasticsearch]\nip=$remote_ip" /etc/aops/zeus.ini
        if [ "$database_port" != "" ]; then
            sed -i "/elasticsearch/,/port/c[elasticsearch]\nip=$remote_ip\nport=$database_port" /etc/aops/apollo.ini
            sed -i "/elasticsearch/,/port/c[elasticsearch]\nip=$remote_ip\nport=$database_port" /etc/aops/zeus.ini
        fi
        return
    fi
}

function install_or_config_databases(){
    echo "[INFO] Start install or configer databases."
    while :
    do
        echo "===========================install or configer databases==========================="
        echo "1. Install the mysql or elasticsearch (i)."
        echo "2. Configure the remote mysql or elasticsearch service (c)."
        echo "Press q(Q) or another non-option key to exit."
        read -p "Select an operation procedure to continue: " operation
        case $operation in
            "i")
                install_database
                ;;
            "c")
                config_remote_database_service
                ;;
            *)
                break
            ;;
        esac
    done
}

function start_or_stop_service(){
    while :
    do
        echo "===========================start or stop service==========================="
        read -p "Please enter the service you want to start or stop e.g(start/stop aops-apollo): " service
        input=$(echo $service | grep -E "start|stop")
        if [ "$service" == "" ] || [ "$input" == "" ]; then
            echo "[INFO] Exit the service start or stop."
            break
        fi
        systemctl $service
        if [ $? == 0 ]; then
            cmd=($service)
            systemctl status ${cmd[1]}
        fi
    done
}

function install_aops_server(){
    echo "[INFO] The aops server installation starts."
    while :
    do
        echo "===========================install aops server==========================="
        echo "1. Install or update the aops software package (iu)."
        echo "2. Install or configure mysql and elasticsearch (ic)."
        echo "3. Update the aops service configuration (uc)."
        echo "4. Start or stop the service (ss)."
        echo "Press q(Q) or another non-option key to exit."
        read -p "Select an operation procedure to continue: " operation
        case $operation in
            "iu")
                install_rpms
            ;;
            "ic")
                install_or_config_databases
            ;;
            "uc")
                update_aops_config
            ;;
            "ss")
                start_or_stop_service
            ;;
            "1")
                install_rpms
            ;;
            "2")
                install_or_config_databases
            ;;
            "3")
                update_aops_config
            ;;
            "4")
                start_or_stop_service
            ;;
            *)
                break
            ;;
        esac
    done
}
