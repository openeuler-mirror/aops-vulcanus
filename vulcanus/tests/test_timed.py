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
TRIGGER_CRON = "cron"
TRIGGER_INTERVAL = "interval"
TRIGGER_INVALID = "invalid"
DAY_OF_WEEK = "day_of_week"
HOUR = "hour"


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
            "timed": {TRIGGER_CRON: TRIGGER_CRON, DAY_OF_WEEK: "0-6", HOUR: "3"},
        }
        task = MockTimedTask(config)
        self.assertTrue(task.check())

    def test_check_valid_interval(self):
        """Test check returns True for valid interval config."""
        config = {
            "task": TASK_NAME,
            "timed": {TRIGGER_INTERVAL: TRIGGER_INTERVAL, "minutes": 30},
        }
        task = MockTimedTask(config)
        self.assertTrue(task.check())

    def test_check_invalid_trigger(self):
        """Test check returns False for invalid trigger."""
        config = {
            "task": TASK_NAME,
            "timed": {TRIGGER_INVALID: TRIGGER_INVALID, DAY_OF_WEEK: "0-6", HOUR: "3"},
        }
        task = MockTimedTask(config)
        self.assertFalse(task.check())

    def test_check_missing_fields(self):
        """Test check returns False when required fields missing."""
        config = {
            "task": TASK_NAME,
            "timed": {TRIGGER_CRON: TRIGGER_CRON},
        }
        task = MockTimedTask(config)
        self.assertFalse(task.check())


class TestTimedTaskManagerParseConfig(unittest.TestCase):
    """Tests for TimedTaskManager._parse_config method."""

    def test_parse_config_valid(self):
        """Test _parse_config parses valid YAML config."""
        yaml_content = (
            f"- task: {TASK_NAME}\n"
            f"  type: {TASK_TYPE}\n"
            "  enable: true\n"
            "  timed:\n"
            f"    trigger: {TRIGGER_CRON}\n"
            f"    {DAY_OF_WEEK}: 0-6\n"
            f"    {HOUR}: 3\n"
        )
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()
            try:
                result = TimedTaskManager._parse_config(f.name)
                self.assertIn(TASK_NAME, result)
                self.assertEqual(result[TASK_NAME]["type"], TASK_TYPE)
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
