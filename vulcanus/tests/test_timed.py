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
    """Tests for TimedTaskManager config parsing via init."""

    def test_parse_config_valid(self):
        """Test TimedTaskManager init parses valid YAML config."""
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
                manager = TimedTaskManager(config_path=f.name)
                self.assertIn(TASK_NAME, manager.timed_config)
                self.assertEqual(manager.timed_config[TASK_NAME]["type"], TASK_TYPE)
            finally:
                os.unlink(f.name)

    def test_parse_config_nonexistent(self):
        """Test TimedTaskManager init raises FileNotFoundError for missing file."""
        with self.assertRaises(FileNotFoundError):
            TimedTaskManager(config_path="/nonexistent/file.yaml")

    def test_parse_config_empty(self):
        """Test TimedTaskManager init returns empty dict for empty YAML."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("[]\n")
            f.flush()
            try:
                manager = TimedTaskManager(config_path=f.name)
                self.assertEqual(manager.timed_config, {})
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
