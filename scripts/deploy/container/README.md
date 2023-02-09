# 介绍

本方案使用**docker+docker-compose**部署aops服务及关联服务

# 结构

一键化系统部署的目录结构及文件的说明

| 文件夹/文件                     | 功能                                                         |
| ------------------------------- | ------------------------------------------------------------ |
| aops-apollo                     | apollo服务的Dockerfile文件                                   |
| aops-diana                      | diana服务的Dockerfile文件                                    |
| aops-zeus                       | zeus服务的Dockerfile文件                                     |
| conf                            | zeus、apollo、diana服务的配置文件；yum的repo源文件、prometheus的配置文件 |
| hermes                          | hermes应用的Dockerfile文件、nginx的配置文件（default.conf）  |
| mysql                           | mysql容器构建的Dockerfile、初始化创建数据库的sql文件         |
| docker-compose-base-service.yml | 基本的软件服务，包含了mysql、elasticsearch、prometheus、kafka等服务的配置 |
| docker-compose.yml              | aops服务的容器化部署配置                                     |
| run.sh                          | 一键化服务部署的入口脚本，包含启动、停止、构建等功能         |

# 配置说明

- docker-compose-base-service.yml

```yml
services:
  mysql:
    build:
      context: ./mysql
      dockerfile: Dockerfile
  elasticsearch:
    image: elasticsearch:7.13.1
  prometheus:
    image: prom/prometheus
  zookeeper:
    image: zookeeper
    container_name: zookeeper
  kafka:
    image: ubuntu/kafka:latest
    container_name: kafka
```

> 基础服务在services配置节下共包含mysql、elasticsearch、prometheus、zookeeper、kafka等5个服务，**在启动过程中，如果不需要某一个服务启动，请手动修改此文件，将指定服务配置注释**

- docker-compose.yml

```yml
services:
  hermes:
    build:
      context: ./hermes
      dockerfile: Dockerfile
  apollo:
    build:
      context: ./aops-apollo
      dockerfile: Dockerfile
  diana:
    build:
      context: ./aops-diana
      dockerfile: Dockerfile
  zeus:
    build:
      context: ./aops-zeus
      dockerfile: Dockerfile
```

> docker-compose下共包含hermes、apollo、diana、zeus服务，**如需控制服务的启动个数，请手动修改此文件，注释指定配置**

- **run.sh**

```shell
main(){
    docker-compose -v 
    if [ $? != 0 ]; then
        install_docker_compose
    fi
    while :
    do
        echo "===========================Container arrangement==========================="
        echo "1. Build the docker container (build)."
        echo "2. Start the container orchestration service (start)."
        echo "3. Stop all container services (stop)."
        read -p "Select an operation procedure to continue: " operation
        case $operation in
            "build")
                docker_build
                docker image prune
            ;;
            "start")
            	# 服务启动时，不需要基础服务时，可以将本行代码注释，默认启动时包含基础服务
                docker-compose -f docker-compose-base-service.yml up -d
                sleep 15
                docker-compose up -d
            ;;
            "stop")
                # 服务启动时，不需要基础服务时，可以将本行代码注释，默认启动时包含基础服务
                docker-compose -f docker-compose-base-service.yml down 
                docker-compose down
            ;;
            *)
                break
            ;;
        esac
    done
}
```

> 一键化部署服务时，请运行此脚本

# 运行

使用一键化部署服务时，请在当前目录下执行 **./run.sh** ，根据交互提示，输入接下来的操作步骤

- build

> 重新构建aops服务，生成新的docker镜像

- start

> 启动基础服务（mysql、elasticsearch、kafka）和aops服务（hermes、apollo、diana、zeus）

- stop

> 停止所有服务，包含基础服务（mysql、elasticsearch、kafka）