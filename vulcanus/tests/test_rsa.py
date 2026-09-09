# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2024. All rights reserved.
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
Description: unit tests for rsa.py
"""
import unittest

from vulcanus.rsa import (
    generate_rsa_key_pair,
    recursive_sort,
    sign_data,
    verify_signature,
    get_public_key_pem_str,
    load_public_key,
    get_private_key_pem_str,
    load_private_key,
)

TEST_DATA = {"key": "value", "num": 42}
TEST_SECRET = "hello world"


class TestRecursiveSort(unittest.TestCase):
    """Tests for recursive_sort function."""

    def test_sort_dict(self):
        """Test recursive_sort sorts dict keys."""
        data = {"b": 1, "a": 2}
        result = recursive_sort(data)
        self.assertEqual(list(result.keys()), ["a", "b"])

    def test_sort_list(self):
        """Test recursive_sort sorts list items."""
        data = [3, 1, 2]
        result = recursive_sort(data)
        self.assertEqual(result, [3, 1, 2])

    def test_sort_nested(self):
        """Test recursive_sort handles nested structures."""
        data = {"b": {"d": 1, "c": 2}, "a": 3}
        result = recursive_sort(data)
        self.assertEqual(list(result.keys()), ["a", "b"])
        self.assertEqual(list(result["b"].keys()), ["c", "d"])

    def test_sort_string(self):
        """Test recursive_sort returns string as-is."""
        result = recursive_sort("test")
        self.assertEqual(result, "test")


class TestRsaKeyPair(unittest.TestCase):
    """Tests for RSA key generation and conversion."""

    def test_generate_key_pair(self):
        """Test generate_rsa_key_pair returns private and public keys."""
        private_key, public_key = generate_rsa_key_pair()
        self.assertIsNotNone(private_key)
        self.assertIsNotNone(public_key)

    def test_get_public_key_pem_str(self):
        """Test get_public_key_pem_str returns PEM string."""
        _, public_key = generate_rsa_key_pair()
        pem_str = get_public_key_pem_str(public_key)
        self.assertIn("BEGIN PUBLIC KEY", pem_str)
        self.assertIn("END PUBLIC KEY", pem_str)

    def test_get_private_key_pem_str(self):
        """Test get_private_key_pem_str returns PEM string."""
        private_key, _ = generate_rsa_key_pair()
        pem_str = get_private_key_pem_str(private_key)
        self.assertIn("BEGIN PRIVATE KEY", pem_str)
        self.assertIn("END PRIVATE KEY", pem_str)

    def test_load_public_key(self):
        """Test load_public_key restores key from PEM string."""
        _, public_key = generate_rsa_key_pair()
        pem_str = get_public_key_pem_str(public_key)
        loaded = load_public_key(pem_str)
        self.assertIsNotNone(loaded)

    def test_load_private_key(self):
        """Test load_private_key restores key from PEM string."""
        private_key, _ = generate_rsa_key_pair()
        pem_str = get_private_key_pem_str(private_key)
        loaded = load_private_key(pem_str)
        self.assertIsNotNone(loaded)


class TestSignAndVerify(unittest.TestCase):
    """Tests for sign_data and verify_signature."""

    def test_sign_and_verify_success(self):
        """Test sign_data and verify_signature work together."""
        private_key, public_key = generate_rsa_key_pair()
        signature = sign_data(TEST_DATA, private_key)
        result = verify_signature(TEST_DATA, signature, public_key)
        self.assertTrue(result)

    def test_verify_wrong_data(self):
        """Test verify_signature returns False for wrong data."""
        private_key, public_key = generate_rsa_key_pair()
        signature = sign_data(TEST_DATA, private_key)
        result = verify_signature({"wrong": "data"}, signature, public_key)
        self.assertFalse(result)

    def test_verify_wrong_signature(self):
        """Test verify_signature returns False for wrong signature."""
        private_key, public_key = generate_rsa_key_pair()
        signature = sign_data(TEST_DATA, private_key)
        wrong_sig = "a" * len(signature)
        result = verify_signature(TEST_DATA, wrong_sig, public_key)
        self.assertFalse(result)

    def test_sign_data_hex_string(self):
        """Test sign_data returns hex string."""
        private_key, _ = generate_rsa_key_pair()
        signature = sign_data(TEST_DATA, private_key)
        self.assertIsInstance(signature, str)
        int(signature, 16)


if __name__ == "__main__":
    unittest.main()
