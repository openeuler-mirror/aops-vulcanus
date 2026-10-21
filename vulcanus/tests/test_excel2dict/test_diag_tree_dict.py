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
Description: unit tests for excel2dict/diag_tree_dict.py with mock sheet,
no real excel file needed
"""
import unittest
from unittest.mock import MagicMock, patch

from vulcanus.excel2dict.diag_tree_dict import (
    DiagBook,
    DiagNode,
    DiagTree,
    PaintingRuleError,
    generate_tree_dict,
)

# Number of useless columns at the end of the sheet, see DiagTree.__generate_tree
USELESS_COL_NUM = 7


class FakeSheet:
    """
    Mock of xlrd sheet, rows is a list of lists
    """

    def __init__(self, rows):
        self.rows = rows
        self.nrows = len(rows)
        self.ncols = max(len(row) for row in rows)

    def cell_value(self, row, col):
        if col >= len(self.rows[row]):
            return ""
        return self.rows[row][col]

    def make_useless(self):
        """
        Pad every row to ncols + USELESS_COL_NUM columns, emulating
        the 7 useless columns of mind master's export
        """
        for row in self.rows:
            row.extend([""] * (USELESS_COL_NUM - (len(row) - self.ncols)))
        self.ncols += USELESS_COL_NUM


def make_rows(node_rows):
    """
    Build raw rows: first row is the tree name, second row is empty,
    then node rows
    """
    return [["Memory", ""]] + [[""]] + node_rows


class TestPaintingRuleError(unittest.TestCase):
    """
    Test of PaintingRuleError
    """

    def test_painting_rule_error_message(self):
        error = PaintingRuleError("error message")
        self.assertEqual(str(error), "error message")

    def test_painting_rule_error_default_message(self):
        error = PaintingRuleError()
        self.assertEqual(str(error), "")


class TestDiagBook(unittest.TestCase):
    """
    Test of DiagBook with mock workbook
    """

    def test_get_diag_table_success(self):
        mock_workbook = MagicMock()
        mock_workbook.sheet_names.return_value = ["diag"]
        with patch("vulcanus.excel2dict.diag_tree_dict.xlrd.open_workbook", return_value=mock_workbook):
            diag_book = DiagBook("mock_path.xlsx")
        mock_workbook.sheet_by_name.assert_called_once_with("diag")

    def test_get_diag_table_no_diag_sheet(self):
        mock_workbook = MagicMock()
        mock_workbook.sheet_names.return_value = ["other"]
        with patch("vulcanus.excel2dict.diag_tree_dict.xlrd.open_workbook", return_value=mock_workbook):
            with self.assertRaises(PaintingRuleError):
                DiagBook("mock_path.xlsx")


class TestDiagNode(unittest.TestCase):
    """
    Test of DiagNode
    """

    def test_init_leaf(self):
        node = DiagNode("cn|eng")
        self.assertTrue(node.is_leaf)
        self.assertEqual(node.name, "cn|eng")
        self.assertEqual(node.children, {})

    def test_init_not_leaf(self):
        node = DiagNode("subtree")
        self.assertFalse(node.is_leaf)

    def test_children_all_leaves_true(self):
        node = DiagNode("parent")
        node.children["a"] = DiagNode("a|a_eng")
        node.children["b"] = DiagNode("b|b_eng")
        self.assertTrue(node.children_all_leaves())

    def test_children_all_leaves_false(self):
        node = DiagNode("parent")
        node.children["a"] = DiagNode("a|a_eng")
        node.children["b"] = DiagNode("subtree")
        self.assertFalse(node.children_all_leaves())

    def test_children_all_trees_true(self):
        node = DiagNode("parent")
        node.children["a"] = DiagNode("subtree1")
        node.children["b"] = DiagNode("subtree2")
        self.assertTrue(node.children_all_trees())

    def test_children_all_trees_false(self):
        node = DiagNode("parent")
        node.children["a"] = DiagNode("subtree")
        node.children["b"] = DiagNode("b|b_eng")
        self.assertFalse(node.children_all_trees())

    def test_to_dict_leaf(self):
        node = DiagNode("cn|eng")
        node.check_item = "eng"
        node.name = "cn"
        result = node.to_dict()
        self.assertEqual(
            result,
            {"node name": "cn", "value": None, "check item": "eng", "msg": ""},
        )

    def test_to_dict_default_condition_all_leaves(self):
        node = DiagNode("parent")
        node.children["cn1"] = DiagNode("cn1|eng1")
        node.children["cn2"] = DiagNode("cn2|eng2")
        result = node.to_dict()
        self.assertEqual(result["condition"], "cn1 && cn2")
        self.assertEqual(len(result["children"]), 2)

    def test_to_dict_default_condition_all_trees(self):
        node = DiagNode("parent")
        child1 = DiagNode("subtree1")
        child1.children["cn1"] = DiagNode("cn1|eng1")
        child2 = DiagNode("subtree2")
        child2.children["cn2"] = DiagNode("cn2|eng2")
        node.children["subtree1"] = child1
        node.children["subtree2"] = child2
        result = node.to_dict()
        self.assertEqual(result["condition"], "subtree1 || subtree2")

    def test_to_dict_defined_condition(self):
        node = DiagNode("parent")
        node.diag_condition = "cn1 || cn2"
        node.children["cn1"] = DiagNode("cn1|eng1")
        node.children["cn2"] = DiagNode("cn2|eng2")
        result = node.to_dict()
        self.assertEqual(result["condition"], "cn1 || cn2")

    def test_to_dict_mixed_children_without_condition(self):
        node = DiagNode("parent")
        node.children["cn1"] = DiagNode("cn1|eng1")
        node.children["subtree"] = DiagNode("subtree")
        with self.assertRaises(PaintingRuleError):
            node.to_dict()


class TestDiagTree(unittest.TestCase):
    """
    Test of DiagTree with mock sheet
    """

    def make_tree(self, node_rows):
        sheet = FakeSheet(make_rows(node_rows))
        sheet.make_useless()
        return DiagTree(sheet)

    def test_get_tree_name(self):
        tree = self.make_tree([])
        self.assertEqual(tree.name, "Memory")

    def test_generate_tree_leaf(self):
        tree = self.make_tree([["Subtree1", ""], ["", "内存|memory"]])
        result = tree.to_dict()
        self.assertEqual(result["node name"], "Memory")
        subtree = result["children"][0]
        self.assertEqual(subtree["node name"], "Subtree1")
        self.assertEqual(subtree["condition"], "内存")
        leaf = subtree["children"][0]
        self.assertEqual(leaf["node name"], "内存")
        self.assertEqual(leaf["check item"], "memory")

    def test_generate_tree_multi_children(self):
        tree = self.make_tree(
            [
                ["Subtree1", ""],
                ["", "内存|memory"],
                ["", "cpu|cpu"],
            ]
        )
        subtree = tree.to_dict()["children"][0]
        self.assertEqual(subtree["condition"], "内存 && cpu")

    def test_generate_tree_condition_row(self):
        tree = self.make_tree(
            [
                ["Subtree1", ""],
                ["", "condition: 内存 || cpu"],
                ["", "内存|memory"],
                ["", "cpu|cpu"],
            ]
        )
        subtree = tree.to_dict()["children"][0]
        self.assertEqual(subtree["condition"], "内存 || cpu")

    def test_generate_tree_description_and_advice(self):
        tree = self.make_tree(
            [
                ["Subtree1", ""],
                ["", "description: some description"],
                ["", "advice: some advice"],
                ["", "内存|memory"],
            ]
        )
        subtree = tree.to_dict()["children"][0]
        self.assertEqual(subtree["description"], "some description")
        self.assertEqual(subtree["advice"], "some advice")

    def test_generate_tree_two_subtrees(self):
        tree = self.make_tree(
            [
                ["Subtree1", ""],
                ["", "内存|memory"],
                ["Subtree2", ""],
                ["", "磁盘|disk"],
            ]
        )
        result = tree.to_dict()
        self.assertEqual(len(result["children"]), 2)
        self.assertEqual(result["children"][1]["children"][0]["check item"], "disk")

    def test_check_one2one_success(self):
        tree = self.make_tree([])
        tree.eng2cn_dict = {"memory": "内存"}
        tree.cn2eng_dict = {"内存": "memory"}
        tree.check_one2one("memory", "内存")

    def test_check_one2one_conflict_eng(self):
        tree = self.make_tree([])
        tree.eng2cn_dict = {"memory": "内存"}
        with self.assertRaises(PaintingRuleError):
            tree.check_one2one("memory", "存储")

    def test_check_one2one_conflict_cn(self):
        tree = self.make_tree([])
        tree.cn2eng_dict = {"内存": "memory"}
        with self.assertRaises(PaintingRuleError):
            tree.check_one2one("mem", "内存")

    def test_create_node_leaf(self):
        tree = self.make_tree([])
        root = tree.root
        node = tree.create_node("内存|memory", root)
        self.assertEqual(root.children["内存"], node)
        self.assertEqual(node.name, "内存")
        self.assertEqual(node.check_item, "memory")
        self.assertEqual(tree.eng2cn_dict, {"memory": "内存"})

    def test_create_node_subtree(self):
        tree = self.make_tree([])
        root = tree.root
        node = tree.create_node("Subtree1", root)
        self.assertEqual(root.children["Subtree1"], node)
        self.assertFalse(node.is_leaf)

    def test_to_dict_with_node(self):
        tree = self.make_tree([["Subtree1", ""], ["", "内存|memory"]])
        subtree_node = tree.root.children["Subtree1"]
        result = tree.to_dict(subtree_node)
        self.assertEqual(result["node name"], "Subtree1")


class TestGenerateTreeDict(unittest.TestCase):
    """
    Test of generate_tree_dict entrance with mock workbook and sheet
    """

    def test_generate_tree_dict_success(self):
        rows = [["Memory", ""]] + [[""]] + [
            ["Subtree1", ""],
            ["", "内存|memory"],
        ]
        for row in rows:
            row.extend([""] * (USELESS_COL_NUM - len(row) + USELESS_COL_NUM))
        sheet = FakeSheet(rows)
        mock_workbook = MagicMock()
        mock_workbook.sheet_names.return_value = ["diag"]
        mock_workbook.sheet_by_name.return_value = sheet
        with patch("vulcanus.excel2dict.diag_tree_dict.xlrd.open_workbook", return_value=mock_workbook):
            result = generate_tree_dict("mock_path.xlsx")
        self.assertEqual(result["node name"], "Memory")
        self.assertEqual(result["children"][0]["children"][0]["check item"], "memory")


if __name__ == "__main__":
    unittest.main()
