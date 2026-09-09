# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2022-2022. All rights reserved.
# licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# ******************************************************************************/
"""
Description: unit tests for multi_thread_handler.py
"""
import time
import unittest

from vulcanus.multi_thread_handler import MultiThreadHandler

TASKS = [1, 2, 3, 4, 5]


def simple_func(x):
    return x * 2


def slow_func(x):
    time.sleep(0.01)
    return x


def error_func(x):
    raise ValueError("test error")


class TestMultiThreadHandlerInit(unittest.TestCase):
    """Tests for MultiThreadHandler initialization."""

    def test_init(self):
        """Test MultiThreadHandler initializes with func, tasks, workers."""
        handler = MultiThreadHandler(simple_func, TASKS, 2)
        self.assertEqual(handler.func, simple_func)
        self.assertEqual(handler.tasks, TASKS)
        self.assertEqual(handler.workers, 2)


class TestMultiThreadHandlerCreateThread(unittest.TestCase):
    """Tests for MultiThreadHandler.create_thread method."""

    def test_create_thread_empty_tasks(self):
        """Test create_thread with empty tasks does nothing."""
        handler = MultiThreadHandler(simple_func, [], 2)
        handler.create_thread()
        self.assertEqual(len(handler.thread_pool), 0)

    def test_create_thread_with_tasks(self):
        """Test create_thread creates threads for each task."""
        handler = MultiThreadHandler(simple_func, TASKS, 2)
        handler.create_thread()
        self.assertEqual(len(handler.thread_pool), len(TASKS))

    def test_create_thread_auto_workers(self):
        """Test create_thread auto-calculates workers."""
        handler = MultiThreadHandler(simple_func, TASKS, None)
        handler.create_thread()
        self.assertEqual(len(handler.thread_pool), len(TASKS))

    def test_create_thread_with_callback(self):
        """Test create_thread with callback function."""
        callback_results = []
        handler = MultiThreadHandler(simple_func, TASKS[:2], 2)
        handler.create_thread(call_back=lambda f: callback_results.append(f.result()))
        time.sleep(0.1)
        self.assertEqual(len(callback_results), 2)


class TestMultiThreadHandlerGetResult(unittest.TestCase):
    """Tests for MultiThreadHandler.get_result method."""

    def test_get_result_success(self):
        """Test get_result returns results from all threads."""
        handler = MultiThreadHandler(simple_func, TASKS, 2)
        handler.create_thread()
        results = handler.get_result()
        self.assertEqual(len(results), len(TASKS))
        self.assertIn(2, results)
        self.assertIn(10, results)

    def test_get_result_with_error(self):
        """Test get_result handles thread errors gracefully."""
        handler = MultiThreadHandler(error_func, [1], 1)
        handler.create_thread()
        results = handler.get_result()
        self.assertEqual(len(results), 1)
        self.assertIn("message", results[0])


if __name__ == "__main__":
    unittest.main()
