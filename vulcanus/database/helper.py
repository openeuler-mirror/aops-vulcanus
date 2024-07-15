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
"""
Time: 2021-12-21 11:47:57
Author: peixiaochao
Description: functions about of database proxy
"""
import time
import math
from sqlalchemy import create_engine
from sqlalchemy.sql.expression import desc, asc

from vulcanus.restful.resp.state import PARTIAL_SUCCEED, SUCCEED


def make_mysql_engine_url(configuration):
    """
    Create engine url of mysql

    Args:
        configuration (Config): configuration object of certain module

    Returns:
        str: url of engine
    """
    mysql_host = configuration.mysql.host
    mysql_port = configuration.mysql.port
    username = configuration.mysql.username
    password = configuration.mysql.password
    mysql_database_name = configuration.mysql.database
    if username and password:
        url = f"mysql+pymysql://{username}:{password}@{mysql_host}:{mysql_port}/{mysql_database_name}"
    else:
        url = f"mysql+pymysql://@{mysql_host}:{mysql_port}/{mysql_database_name}"

    return url


def create_database_engine(url, pool_size, pool_recycle):
    """
    Create database connection pool

    Args:
        url(str): engine url
        pool_size(int): size of pool
        pool_recycle(int): time that pool recycle the connection

    Returns:
        engine
    """
    engine = create_engine(url, pool_size=pool_size, pool_recycle=pool_recycle, pool_pre_ping=True)
    return engine


def create_tables(base, engine, tables=None):
    """
    Create all tables according to metadata of Base.

    Args:
        base (instance): sqlalchemy.ext.declarative.declarative_base(), actually a registry instance
        engine(instance): _engine.Engine instance
        tables (list): table object list
    """
    base.metadata.create_all(engine, tables=tables)


def drop_tables(base, engine):
    """
    Drop all tables according to metadata of Base.

    Args:
        base (instance): sqlalchemy.ext.declarative.declarative_base(), actually a registry instance
        engine(instance): _engine.Engine instance
    """
    base.metadata.drop_all(engine)


def timestamp_datetime(value):
    """
    transfer unix time to formatted timestamp.

    Args:
        value (int): unix time.

    Returns:
        str: formatted time.
    """
    time_format = "%Y-%m-%dT%H:%M:%S%z"
    time_struct = time.localtime(value)
    return time.strftime(time_format, time_struct)


def timestr_unix(time_str):
    """
    transfer formatted timestamp to unix time.

    Args:
        time_str (str): formated time string.

    Returns:
        int: unix time.
    """
    time_format_with_hill = "%Y-%m-%dT%H:%M:%S.%f%z"

    time_str = time_str[:26] + time_str[-6:]
    time_format = time.strptime(time_str, time_format_with_hill)
    return int(time.mktime(time_format))


def sort_and_page(query_result, column, direction, per_page, page):
    """
    Sort and paginate the query result
    Args:
        query_result (sqlalchemy.orm.query.Query): query result
        column (sqlalchemy.orm.attributes.InstrumentedAttribute/
            sqlalchemy.sql.functions.count/None): the column that sort based on
        direction (str/None): desc or asc
        per_page (int/None): number of record per page, if per_page = None, return all
        page (int/None): which page to return, if page = None, return all

    Returns:
        sqlalchemy.orm.query.Query
    """
    total_page = 1
    total_count = query_result.count()

    if not total_count:
        return query_result, total_page

    direction = desc if direction == "desc" else asc

    # when column is a sqlalchemy.sql.functions.count object, like func.count(Hots.host_id),
    # it has no boolean value, so "if column:" here is not available
    if column is not None:
        query_result = query_result.order_by(direction(column))

    if page and per_page:
        page = int(page)
        per_page = int(per_page)
        total_page = math.ceil(total_count / per_page)
        query_result = query_result.offset((page - 1) * per_page).limit(per_page)

    return query_result, total_page


def judge_return_code(result, default_stat):
    """
    Generate return result according to result

    Args:
        result(dict)
        default_stat(int): default error status code

    Returns:
        int: status code
    """
    if result.get("succeed_list") or result.get("update_list"):
        if result.get("fail_list"):
            return PARTIAL_SUCCEED
        else:
            return SUCCEED
    if result.get("fail_list"):
        return default_stat
    return SUCCEED


def combine_return_codes(default_stat, *args):
    """
    Combine multiple return codes into one code
    Args:
        default_stat: default error status code, if all codes in args are not success,
        will return default error code
        *args: multiple status code

    Returns:

    """
    if PARTIAL_SUCCEED in args:
        return PARTIAL_SUCCEED
    if SUCCEED in args:
        if len(set(args)) > 1:
            return PARTIAL_SUCCEED
        return SUCCEED
    return default_stat
