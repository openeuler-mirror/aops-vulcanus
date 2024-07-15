#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2023. All rights reserved.
# licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN 'AS IS' BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# ******************************************************************************/
from flask import Flask
from flask.blueprints import Blueprint
from flask_restful import Api
from vulcanus.database.helper import create_database_engine, make_mysql_engine_url
from vulcanus.database.proxy import MysqlProxy, RedisProxy
from vulcanus.conf import configuration


def _register_blue_point(urls):
    api = Api()
    for view, url in urls:
        api.add_resource(view, url, endpoint=view.__name__)
    return api


def _set_database_engine(settings):
    engine = create_database_engine(
        make_mysql_engine_url(settings), settings.mysql.pool_size, settings.mysql.pool_recycle
    )
    setattr(MysqlProxy, "engine", engine)


def init_application(name: str, settings, register_urls: list = None, config: dict = None):
    """
    Init application

    Args:
        name(str): The name of the microservice, e.g zeus apollo
        settings: privatized configuration of services,read the configuration content of zeus.ini apollo.ini
                e.g settings = Config("zeus.ini", default_config)

        register_urls: route list of the service, e.g
            [
                (cve_repo_view.VulImportYumRepo, VUL_REPO_IMPORT),
                (cve_repo_view.VulGetYumRepo, VUL_REPO_GET),
            ]
        config: flask configuration item, e.g
            {
                "MAX_CONTENT_LENGTH": 1024
            }

    Returns:
        app: flask application
    """
    service_module = __import__(name)

    app = Flask(service_module.__name__)

    # Unique configuration for flask service initialization
    if config:
        for config_item, config_content in config.items():
            app.config[config_item] = config_content

    # url routing address of the api service
    # register the routing address into the blueprint
    if register_urls:
        api = _register_blue_point(register_urls)
        api.init_app(app)
        app.register_blueprint(Blueprint('manager', __name__))

    # sync service config
    _set_database_engine(settings)
    for config in [config for config in dir(settings) if not config.startswith("_")]:
        setattr(configuration, config, getattr(settings, config))

    # init redis connect
    RedisProxy()
    return app
