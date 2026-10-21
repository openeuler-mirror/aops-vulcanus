#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.
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
Unit test of vulcanus.database.proxy with mock, no real service needed
"""
import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

from sqlalchemy.exc import SQLAlchemyError

from vulcanus.database.proxy import (
    ElasticsearchProxy,
    MysqlProxy,
    PromDbProxy,
    RedisProxy,
    connect_database,
)
from vulcanus.exceptions import DatabaseConnectionFailed, DatabaseError
from vulcanus.restful.resp import state


class FakeSession:
    """
    Mock of sqlalchemy session
    """

    def __init__(self, raise_error=False):
        self.raise_error = raise_error
        self.closed = False
        self.committed = False
        self.rollbacked = False

    def add(self, _):
        if self.raise_error:
            raise SQLAlchemyError("insert error")

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rollbacked = True

    def close(self):
        self.closed = True

    def query(self, *args, **kwargs):
        if self.raise_error:
            raise SQLAlchemyError("query error")
        return MagicMock()


class TestConnectDatabaseDecorator(unittest.TestCase):
    """
    Test of connect_database decorator
    """

    def test_connect_database_no_exception(self):
        class Demo:
            @connect_database(status=state.DATABASE_CONNECT_ERROR, return_value=None)
            def func(self):
                return state.SUCCEED, "data"

        self.assertEqual(Demo().func(), (state.SUCCEED, "data"))

    def test_connect_database_connection_failed(self):
        class Demo:
            @connect_database(status=state.DATABASE_CONNECT_ERROR)
            def func(self):
                raise DatabaseConnectionFailed("connect failed")

        self.assertEqual(Demo().func(), state.DATABASE_CONNECT_ERROR)

    def test_connect_database_connection_failed_with_return_value(self):
        class Demo:
            @connect_database(status=state.DATABASE_CONNECT_ERROR, return_value="mock value")
            def func(self):
                raise DatabaseConnectionFailed("connect failed")

        self.assertEqual(Demo().func(), (state.DATABASE_CONNECT_ERROR, "mock value"))


class TestMysqlProxy(unittest.TestCase):
    """
    Test of MysqlProxy with mock engine and session
    """

    def setUp(self):
        MysqlProxy.engine = MagicMock()
        self.mysql_proxy = MysqlProxy()
        self.mysql_proxy.session = FakeSession()

    def tearDown(self):
        MysqlProxy.engine = None

    def test_init_without_engine(self):
        MysqlProxy.engine = None
        with self.assertRaises(DatabaseError):
            MysqlProxy()

    def test_connect_success(self):
        with patch("vulcanus.database.proxy.sessionmaker") as mock_sessionmaker:
            mock_sessionmaker.return_value.return_value = FakeSession()
            self.assertTrue(self.mysql_proxy.connect())
            self.assertIsNotNone(self.mysql_proxy.session)

    def test_connect_fail(self):
        with patch("vulcanus.database.proxy.sessionmaker") as mock_sessionmaker:
            mock_sessionmaker.return_value.configure.side_effect = SQLAlchemyError("error")
            self.assertFalse(self.mysql_proxy.connect())

    def test_enter_exit(self):
        with patch("vulcanus.database.proxy.sessionmaker") as mock_sessionmaker:
            mock_sessionmaker.return_value.return_value = FakeSession()
            proxy = self.mysql_proxy.__enter__()
            self.assertEqual(proxy, self.mysql_proxy)

            self.mysql_proxy.__exit__(None, None, None)
            self.assertTrue(self.mysql_proxy.session.closed)

    def test_exit_with_attribute_error(self):
        error = AttributeError("error")
        with self.assertRaises(SQLAlchemyError):
            self.mysql_proxy.__exit__(error, error, None)

    def test_insert_success(self):
        result = self.mysql_proxy.insert(dict, {"a": 1})
        self.assertTrue(result)
        self.assertTrue(self.mysql_proxy.session.committed)

    def test_insert_fail(self):
        self.mysql_proxy.session = FakeSession(raise_error=True)
        result = self.mysql_proxy.insert(dict, {"a": 1})
        self.assertFalse(result)
        self.assertTrue(self.mysql_proxy.session.rollbacked)

    def test_select_success(self):
        result = self.mysql_proxy.select([dict], {"a": 1})
        self.assertTrue(result[0])

    def test_select_fail(self):
        self.mysql_proxy.session = FakeSession(raise_error=True)
        result = self.mysql_proxy.select([dict], {"a": 1})
        self.assertFalse(result[0])
        self.assertEqual(result[1], [])

    def test_delete_success(self):
        result = self.mysql_proxy.delete(dict, {"a": 1})
        self.assertTrue(result)

    def test_delete_fail(self):
        self.mysql_proxy.session = FakeSession(raise_error=True)
        result = self.mysql_proxy.delete(dict, {"a": 1})
        self.assertFalse(result)
        self.assertTrue(self.mysql_proxy.session.rollbacked)


class TestElasticsearchProxy(unittest.TestCase):
    """
    Test of ElasticsearchProxy with mock client
    """

    def setUp(self):
        ElasticsearchProxy._es_db = MagicMock()

    def tearDown(self):
        ElasticsearchProxy._es_db = None

    def test_init_with_host_port(self):
        ElasticsearchProxy._es_db = None
        with patch("vulcanus.database.proxy.Elasticsearch") as mock_es:
            ElasticsearchProxy(host="127.0.0.1", port=9200)
            mock_es.assert_called_once()

    def test_init_connection_failed(self):
        from urllib3.exceptions import LocationValueError

        ElasticsearchProxy._es_db = None
        with patch("vulcanus.database.proxy.Elasticsearch", side_effect=LocationValueError("error")):
            with self.assertRaises(DatabaseConnectionFailed):
                ElasticsearchProxy(host="127.0.0.1", port=9200)

    def test_query_success(self):
        ElasticsearchProxy._es_db.search.return_value = {"hits": {"hits": []}}
        proxy = ElasticsearchProxy(host="127.0.0.1", port=9200)
        result = proxy.query("test_index", {"query": {}})
        self.assertTrue(result[0])
        self.assertEqual(result[1], {"hits": {"hits": []}})

    def test_query_not_found(self):
        from elasticsearch import NotFoundError

        ElasticsearchProxy._es_db.search.side_effect = NotFoundError(404, "no index")
        proxy = ElasticsearchProxy(host="127.0.0.1", port=9200)
        result = proxy.query("test_index", {"query": {}})
        self.assertEqual(result, (True, []))

    def test_query_es_exception(self):
        from elasticsearch import ElasticsearchException

        ElasticsearchProxy._es_db.search.side_effect = ElasticsearchException("error")
        proxy = ElasticsearchProxy(host="127.0.0.1", port=9200)
        result = proxy.query("test_index", {"query": {}})
        self.assertEqual(result, (False, []))

    def test_scan_success(self):
        mock_doc = {"_source": {"name": "test"}}
        with patch("vulcanus.database.proxy.helpers.scan", return_value=[mock_doc]):
            proxy = ElasticsearchProxy(host="127.0.0.1", port=9200)
            result = proxy.scan("test_index", {"query": {}})
            self.assertEqual(result, (True, [{"name": "test"}]))

    def test_scan_es_exception(self):
        from elasticsearch import ElasticsearchException

        with patch("vulcanus.database.proxy.helpers.scan", side_effect=ElasticsearchException("error")):
            proxy = ElasticsearchProxy(host="127.0.0.1", port=9200)
            result = proxy.scan("test_index", {"query": {}})
            self.assertEqual(result, (False, []))

    def test_count_success(self):
        ElasticsearchProxy._es_db.count.return_value = {"count": 5}
        proxy = ElasticsearchProxy(host="127.0.0.1", port=9200)
        result = proxy.count("test_index", {"query": {}})
        self.assertEqual(result, (True, 5))

    def test_count_es_exception(self):
        from elasticsearch import ElasticsearchException

        ElasticsearchProxy._es_db.count.side_effect = ElasticsearchException("error")
        proxy = ElasticsearchProxy(host="127.0.0.1", port=9200)
        result = proxy.count("test_index", {"query": {}})
        self.assertEqual(result, (False, 0))

    def test_create_index_success(self):
        ElasticsearchProxy._es_db.indices.exists.return_value = False
        proxy = ElasticsearchProxy(host="127.0.0.1", port=9200)
        self.assertTrue(proxy.create_index("test_index", {"mappings": {}}))
        ElasticsearchProxy._es_db.indices.create.assert_called_once()

    def test_create_index_already_exists(self):
        ElasticsearchProxy._es_db.indices.exists.return_value = True
        proxy = ElasticsearchProxy(host="127.0.0.1", port=9200)
        self.assertTrue(proxy.create_index("test_index", {"mappings": {}}))
        ElasticsearchProxy._es_db.indices.create.assert_not_called()

    def test_create_index_fail(self):
        from elasticsearch import ElasticsearchException

        ElasticsearchProxy._es_db.indices.exists.side_effect = ElasticsearchException("error")
        proxy = ElasticsearchProxy(host="127.0.0.1", port=9200)
        self.assertFalse(proxy.create_index("test_index", {"mappings": {}}))

    def test_insert_success(self):
        proxy = ElasticsearchProxy(host="127.0.0.1", port=9200)
        self.assertTrue(proxy.insert("test_index", {"name": "test"}, document_id="1"))

    def test_insert_fail(self):
        from elasticsearch import ElasticsearchException

        ElasticsearchProxy._es_db.index.side_effect = ElasticsearchException("error")
        proxy = ElasticsearchProxy(host="127.0.0.1", port=9200)
        self.assertFalse(proxy.insert("test_index", {"name": "test"}))

    def test_exists_success(self):
        ElasticsearchProxy._es_db.exists.return_value = True
        proxy = ElasticsearchProxy(host="127.0.0.1", port=9200)
        self.assertEqual(proxy.exists("test_index", "1"), (True, True))

    def test_exists_fail(self):
        from elasticsearch import ElasticsearchException

        ElasticsearchProxy._es_db.exists.side_effect = ElasticsearchException("error")
        proxy = ElasticsearchProxy(host="127.0.0.1", port=9200)
        self.assertEqual(proxy.exists("test_index", "1"), (False, None))

    def test_insert_bulk(self):
        proxy = ElasticsearchProxy(host="127.0.0.1", port=9200)
        with patch("vulcanus.database.proxy.helpers.bulk") as mock_bulk:
            result = proxy.insert_bulk("test_index", [{"name": "a"}])
            self.assertTrue(result)
            mock_bulk.assert_called_once()

    def test_update_bulk(self):
        proxy = ElasticsearchProxy(host="127.0.0.1", port=9200)
        with patch("vulcanus.database.proxy.helpers.bulk") as mock_bulk:
            result = proxy.update_bulk("test_index", [{"_id": "1", "doc": {"name": "a"}}])
            self.assertTrue(result)
            mock_bulk.assert_called_once()

    def test_bulk_empty_action(self):
        proxy = ElasticsearchProxy(host="127.0.0.1", port=9200)
        self.assertTrue(proxy._bulk([]))

    def test_bulk_fail(self):
        from elasticsearch import ElasticsearchException

        with patch("vulcanus.database.proxy.helpers.bulk", side_effect=ElasticsearchException("error")):
            proxy = ElasticsearchProxy(host="127.0.0.1", port=9200)
            self.assertFalse(proxy._bulk([{"_index": "test_index"}]))

    def test_delete_success(self):
        proxy = ElasticsearchProxy(host="127.0.0.1", port=9200)
        self.assertTrue(proxy.delete("test_index", {"query": {}}))

    def test_delete_fail(self):
        from elasticsearch import ElasticsearchException

        ElasticsearchProxy._es_db.delete_by_query.side_effect = ElasticsearchException("error")
        proxy = ElasticsearchProxy(host="127.0.0.1", port=9200)
        self.assertFalse(proxy.delete("test_index", {"query": {}}))

    def test_delete_index_success(self):
        proxy = ElasticsearchProxy(host="127.0.0.1", port=9200)
        self.assertTrue(proxy.delete_index("test_index"))

    def test_delete_index_fail(self):
        from elasticsearch import TransportError

        ElasticsearchProxy._es_db.indices.delete.side_effect = TransportError("error")
        proxy = ElasticsearchProxy(host="127.0.0.1", port=9200)
        self.assertFalse(proxy.delete_index("test_index"))

    def test_update_settings_success(self):
        proxy = ElasticsearchProxy(host="127.0.0.1", port=9200)
        proxy.update_settings(max_result_window=1000)
        ElasticsearchProxy._es_db.indices.put_settings.assert_called_once()

    def test_update_settings_fail(self):
        from elasticsearch import ElasticsearchException

        ElasticsearchProxy._es_db.indices.put_settings.side_effect = ElasticsearchException("error")
        proxy = ElasticsearchProxy(host="127.0.0.1", port=9200)
        proxy.update_settings(max_result_window=1000)

    def test_make_es_paginate_body_with_page(self):
        body = {}
        ElasticsearchProxy._make_es_paginate_body({"page": 2, "size": 10}, body)
        self.assertEqual(body.get("from"), 10)
        self.assertEqual(body.get("size"), 10)

    def test_make_es_paginate_body_with_sort(self):
        body = {}
        ElasticsearchProxy._make_es_paginate_body({"sort": "time", "direction": "dsc"}, body)
        self.assertEqual(body.get("sort"), [{"time": {"order": "dsc", "unmapped_type": "keyword"}}])

    def test_make_es_paginate_body_default_direction(self):
        body = {}
        ElasticsearchProxy._make_es_paginate_body({"sort": "time"}, body)
        self.assertEqual(body.get("sort")[0]["time"]["order"], "asc")

    def test_general_body_with_data(self):
        body = ElasticsearchProxy._general_body({"username": "admin"})
        self.assertEqual(body["query"]["bool"]["must"], [{"term": {"username": "admin"}}])

    def test_general_body_without_data(self):
        body = ElasticsearchProxy._general_body()
        self.assertEqual(body["query"]["bool"]["must"], [])


class TestPromDbProxy(unittest.TestCase):
    """
    Test of PromDbProxy with mock prometheus client
    """

    def setUp(self):
        patcher = patch("vulcanus.database.proxy.PrometheusConnect")
        self.mock_prom_connect = patcher.start()
        self.addCleanup(patcher.stop)
        self.mock_prom = self.mock_prom_connect.return_value
        self.mock_prom.check_prometheus_connection.return_value = True

    def test_init_success(self):
        proxy = PromDbProxy(host="127.0.0.1", port=9090)
        self.mock_prom_connect.assert_called_once_with(url="http://127.0.0.1:9090", disable_ssl=True)

    def test_init_connection_failed(self):
        self.mock_prom.check_prometheus_connection.return_value = False
        with self.assertRaises(DatabaseConnectionFailed):
            PromDbProxy(host="127.0.0.1", port=9090)

    def test_connected_true(self):
        proxy = PromDbProxy(host="127.0.0.1", port=9090)
        self.assertTrue(proxy.connected)

    def test_connected_false_on_error(self):
        from requests.exceptions import ConnectionError

        proxy = PromDbProxy(host="127.0.0.1", port=9090)
        self.mock_prom.check_prometheus_connection.side_effect = ConnectionError("error")
        self.assertFalse(proxy.connected)

    def test_query_success(self):
        self.mock_prom.get_metric_range_data.return_value = [{"metric": {}, "values": []}]
        proxy = PromDbProxy(host="127.0.0.1", port=9090)
        time_range = [1600000000, 1600086400]
        result = proxy.query("127.0.0.1", time_range, "up")
        self.assertTrue(result[0])
        self.assertEqual(result[1], [{"metric": {}, "values": []}])

    def test_query_empty_data(self):
        self.mock_prom.get_metric_range_data.return_value = []
        proxy = PromDbProxy(host="127.0.0.1", port=9090)
        result = proxy.query("127.0.0.1", [1600000000, 1600086400], "up")
        self.assertEqual(result, (True, []))

    def test_query_api_exception(self):
        from prometheus_api_client import PrometheusApiClientException

        self.mock_prom.get_metric_range_data.side_effect = PrometheusApiClientException("error")
        proxy = PromDbProxy(host="127.0.0.1", port=9090)
        result = proxy.query("127.0.0.1", [1600000000, 1600086400], "up", {"label": "value"})
        self.assertFalse(result[0])
        self.assertEqual(
            result[1], [{"host_id": "127.0.0.1", "name": "up", "label": {"label": "value"}}]
        )

    def test_query_value_error(self):
        self.mock_prom.get_metric_range_data.side_effect = ValueError("error")
        proxy = PromDbProxy(host="127.0.0.1", port=9090)
        result = proxy.query("127.0.0.1", [1600000000, 1600086400], "up")
        self.assertFalse(result[0])

    def test_combine_condition_with_label(self):
        result = PromDbProxy._combine_condition({"label": "value"}, "instance=~\"host\"")
        self.assertEqual(result, '{instance=~"host",label="value"}')

    def test_combine_condition_without_label(self):
        result = PromDbProxy._combine_condition(None, "instance=~\"host\"")
        self.assertEqual(result, '{instance=~"host"}')


class TestRedisProxy(unittest.TestCase):
    """
    Test of RedisProxy with mock redis client
    """

    def setUp(self):
        RedisProxy.redis_connect = None

    def tearDown(self):
        RedisProxy.redis_connect = None

    def test_init_success(self):
        with patch("vulcanus.database.proxy.Redis") as mock_redis:
            mock_redis.return_value.ping.return_value = True
            proxy = RedisProxy.__wrapped__(host="127.0.0.1", port=6379)
            mock_redis.assert_called_once()
            mock_redis.return_value.ping.assert_called_once()

    def test_init_connection_failed(self):
        import redis

        with patch("vulcanus.database.proxy.Redis", side_effect=redis.ConnectionError("error")):
            with self.assertRaises(DatabaseConnectionFailed):
                RedisProxy.__wrapped__(host="127.0.0.1", port=6379)

    def test_close(self):
        with patch("vulcanus.database.proxy.Redis") as mock_redis:
            mock_redis.return_value.ping.return_value = True
            proxy = RedisProxy.__wrapped__(host="127.0.0.1", port=6379)
            proxy.close()
            RedisProxy.redis_connect.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
