#!/bin/bash
. /usr/bin/aops-vulcanus
REPO_CONFIG_FILE="/etc/yum.repos.d/aops_elascticsearch.repo"
INSTALL_SOFTWARE=$1

function check_es_status() {
  visit_es_response=$(curl -s -XGET http://127.0.0.1:9200)
  if [[ "${visit_es_response}" =~ "You Know, for Search" ]]; then
    echo "[ERROR] The service is running, please close it manually and try again."
    exit 1
  fi
}

function create_es_repo() {
  echo "[INFO] Start to create ES official installation repo"

  if [ ! -f ${REPO_CONFIG_FILE} ]; then
    touch ${REPO_CONFIG_FILE}
  fi
  echo "[aops_elasticsearch]
name=Elasticsearch repository for 7.x packages
baseurl=https://artifacts.elastic.co/packages/7.x/yum
gpgcheck=1
gpgkey=https://artifacts.elastic.co/GPG-KEY-elasticsearch
enabled=1
autorefresh=1
type=rpm-md" >${REPO_CONFIG_FILE}
  # create repo file failed
  if [ ! -f ${REPO_CONFIG_FILE} ]; then
    echo "[ERROR] aops_elasticsearch.repo file creation failed!"
    echo "Please confirm whether you have permission!"
    exit 1
  fi

  echo "[INFO] Create ES repo success"
}

function download_install_es() {
  echo "[INFO] start to download and install elasticsearch"
  # check repo
  es_repo=$(yum repolist | grep "aops_elasticsearch")
  if [ -z "${es_repo}" ]; then
    echo "[ERROR] not found elasticsearch repo,please check config file in /etc/yum.repos.d"
    exit 1
  fi

  if yum install elasticsearch-7.14.0-1 -y; then
    echo "[INFO]download and install elasticsearch success"
  else
    echo "[ERROR] install elasticsearch failed"
    exit 1
  fi

}

function start_elasticsearch_service() {
  echo "[INFO] start to start elasticsearch service"
  sudo /bin/systemctl daemon-reload
  sudo /bin/systemctl enable elasticsearch.service
  sudo /bin/systemctl start elasticsearch.service
  for i in {1..12}; do
    visit_es_response=$(curl -s -XGET http://127.0.0.1:9200)
    if [[ "${visit_es_response}" =~ "You Know, for Search" ]]; then
      echo "[INFO] elasticsearch start success"
      exit 0
    fi
    sleep 5
  done

  echo "[ERROR] elasticsearch start failed,please check /var/log/elasticsearch/elasticsearch.log"
  exit 1
}

function download_install_mysql() {
  echo "[INFO] start to download and install mysql"

  if yum install mysql-server -y; then
    echo "[INFO] download and install mysql success"
  else
    echo "[ERROR] install mysql failed"
    echo "[ERROR] Please check the files under the /etc/yum.repos.d/ is config correct"
    exit 1
  fi
}

function download_install_redis() {
  echo "[INFO] start to download and install redis"

  if yum install redis -y; then
    echo "[INFO] download and install redis success"
  else
    echo "[ERROR] install redis failed"
    echo "[ERROR] Please check the files under the /etc/yum.repos.d/ is config correct"
    exit 1
  fi
}

function start_mysql_service() {
  echo "[INFO] start to start mysql service"
  sudo systemctl start mysqld
  for i in {1..12}; do
    mysql_pid=$(pgrep mysqld)
    if [[ -n ${mysql_pid} ]]; then
      echo "[INFO] mysql start success"
      exit 0
    fi
    sleep 2
  done

  echo "[ERROR] mysql start failed,please check /var/log/mysql/mysql.log"
  exit 1
}

function install_database() {
  if [ "${INSTALL_SOFTWARE}" = "elasticsearch" ]; then
    check_es_status
    create_es_repo
    download_install_es
    start_elasticsearch_service
  elif [ "${INSTALL_SOFTWARE}" = "mysql" ]; then
    download_install_mysql
    start_mysql_service
  elif [ "${INSTALL_SOFTWARE}" = "redis" ]; then
    download_install_redis
    sudo systemctl start redis
  else
    echo "Failed to parse parameters, please use 'elasticsearch/mysql/redis'"
  fi
}

function main(){
  operation=$1
  service=$2
  case $operation in
    "init")
        if [ "${service}" != "zeus" ] && [ "${service}" != "apollo" ] && [ "${service}" != "diana" ]; then
          echo "[ERROR] Table initialization service can only be zeus apollo or diana"
          echo "[INFO] e.g 'aops-basedatabase init zeus' 'aops-basedatabase init apollo' or 'aops-basedatabase init diana'"
          exit 1
        fi
        config_file="/etc/aops/$service.ini"
        sql="/opt/aops/database/$service.sql"
        init_database_and_table $config_file $sql
    ;;
    "install")
        install_database $service
    ;;
    *)  
        echo "[WARNING] Only init and install operations are supported"
    ;;
esac
}

main $1 $2