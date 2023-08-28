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
Time:
Author:
Description:
"""
import unittest
from unittest import mock
from elasticsearch import Elasticsearch
from vulcanus.database.proxy import ElasticsearchProxy
from vulcanus.common import hash_value


class TestElasticsearchProxy(unittest.TestCase):
    def setUp(self):
        self.es_proxy = ElasticsearchProxy(host="127.0.0.1", port=9200)

    @mock.patch.object(Elasticsearch, 'exists')
    def test_exists_should_true_when_exists_data(self, mock_exists):
        mock_exists.return_value = True
        document_id = hash_value("90d0a61e32a811ee8677000c29766160_" + str(1))
        _, exists = self.es_proxy.exists(index="TASK_INDEX", document_id=document_id)
        self.assertEqual(exists, True)

    @mock.patch.object(Elasticsearch, 'exists')
    def test_exists_should_false_when_not_exists(self, mock_exists):
        mock_exists.return_value = False
        document_id = hash_value("90d0a61e32a811ee8677000c29766160_" + str(1))
        _, exists = self.es_proxy.exists(index="TASK_INDEX", document_id=document_id)
        self.assertEqual(exists, False)

    def test_make_es_paginate_body_should_contain_from_and_size_when_exists_page_and_size(self):
        body = {
            "query": {
                "bool": {"must": [{"term": {"task_id": "90d0a61e32a811ee8677000c29766160"}}, {"term": {"host_id": 1}}]}
            }
        }
        paginate_param = dict(page=1, size=10)
        ElasticsearchProxy._make_es_paginate_body(paginate_param, body)
        self.assertEqual(body["from"], 0)

    def test_make_es_paginate_body_should_not_contain_from_and_size_when_no_page_and_size(self):
        body = {
            "query": {
                "bool": {"must": [{"term": {"task_id": "90d0a61e32a811ee8677000c29766160"}}, {"term": {"host_id": 1}}]}
            }
        }
        paginate_param = dict()
        ElasticsearchProxy._make_es_paginate_body(paginate_param, body)
        self.assertEqual(body.get("from"), None)
