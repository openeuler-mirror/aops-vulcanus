# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2023-2023. All rights reserved.
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
Description: unit tests for timed.py
"""
import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from vulcanus.timed import TimedTask, TimedTaskManager

TASK_NAME = "test_task"
TASK_TYPE = "test_type"


class MockTimedTask(TimedTask):
    """Mock implementation of abstract TimedTask."""

    def execute(self):
        pass


class TestTimedTaskCheck(unittest.TestCase):
    """Tests for TimedTask.check method."""

    def test_check_valid_cron(self):
        """Test check returns True for valid cron config."""
        config = {
            "task": TASK_NAME,
            "timed": {"trigger": "cron", "day_of_week": "0-6", "hour": "3"},
        }
        task = MockTimedTask(config)
        self.assertTrue(task.check())

    def test_check_valid_interval(self):
        """Test check returns True for valid interval config."""
        config = {
            "task": TASK_NAME,
            "timed": {"trigger": "interval", "minutes": 30},
        }
        task = MockTimedTask(config)
        self.assertTrue(task.check())

    def test_check_invalid_trigger(self):
        """Test check returns False for invalid trigger."""
        config = {
            "task": TASK_NAME,
            "timed": {"trigger": "invalid", "day_of_week": "0-6", "hour": "3"},
        }
        task = MockTimedTask(config)
        self.assertFalse(task.check())

    def test_check_missing_fields(self):
        """Test check returns False when required fields missing."""
        config = {
            "task": TASK_NAME,
            "timed": {"trigger": "cron"},
        }
        task = MockTimedTask(config)
        self.assertFalse(task.check())


class TestTimedTaskManagerParseConfig(unittest.TestCase):
    """Tests for TimedTaskManager._parse_config method."""

    def test_parse_config_valid(self):
        """Test _parse_config parses valid YAML config."""
        yaml_content = (
            "- task: test_task\n"
            "  type: test_type\n"
            "  enable: true\n"
            "  timed:\n"
            "    trigger: cron\n"
            "    day_of_week: 0-6\n"
            "    hour: 3\n"
        )
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()
            try:
                result = TimedTaskManager._parse_config(f.name)
                self.assertIn("test_task", result)
                self.assertEqual(result["test_task"]["type"], "test_type")
            finally:
                os.unlink(f.name)

    def test_parse_config_nonexistent(self):
        """Test _parse_config raises FileNotFoundError for missing file."""
        with self.assertRaises(FileNotFoundError):
            TimedTaskManager._parse_config("/nonexistent/file.yaml")

    def test_parse_config_empty(self):
        """Test _parse_config returns empty dict for empty YAML."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("[]\n")
            f.flush()
            try:
                result = TimedTaskManager._parse_config(f.name)
                self.assertEqual(result, {})
            finally:
                os.unlink(f.name)


class TestTimedTaskManagerInit(unittest.TestCase):
    """Tests for TimedTaskManager initialization."""

    @patch("vulcanus.timed.APScheduler")
    def test_init(self, mock_scheduler):
        """Test TimedTaskManager initializes correctly."""
        manager = TimedTaskManager()
        self.assertIsNotNone(manager.timed_scheduler)


if __name__ == "__main__":
    unittest.main()
