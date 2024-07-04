#!/usr/bin/python3
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
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa


def generate_rsa_key_pair():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
    public_key = private_key.public_key()

    return private_key, public_key


def recursive_sort(data):
    if isinstance(data, dict):
        return {key: recursive_sort(data[key]) for key in sorted(data.keys())}
    elif isinstance(data, list):
        return [recursive_sort(item) for item in data]
    else:
        return data


def sign_data(data, private_key):
    data = str(recursive_sort(data)).encode()
    signature = private_key.sign(
        data, padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256()
    )

    return signature.hex()


def verify_signature(data, signature, public_key):
    data = str(recursive_sort(data)).encode()
    signature = bytes.fromhex(signature)
    try:
        public_key.verify(
            signature,
            data,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256(),
        )
        return True
    except InvalidSignature as e:
        return False


def get_public_key_pem_str(public_key):
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    public_pem_str = public_pem.decode('utf-8')
    return public_pem_str


def load_public_key(public_pem_str):
    public_pem = bytes(public_pem_str, 'utf-8')
    public_key = serialization.load_pem_public_key(public_pem, backend=default_backend())
    return public_key


def get_private_key_pem_str(private_key):
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    private_pem_str = private_pem.decode('utf-8')
    return private_pem_str


def load_private_key(private_pem_str):
    private_pem = bytes(private_pem_str, 'utf-8')
    private_key = serialization.load_pem_private_key(private_pem, password=None, backend=default_backend())
    return private_key
