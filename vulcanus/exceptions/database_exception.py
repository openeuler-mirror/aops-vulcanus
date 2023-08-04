#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2023. All rights reserved.
# licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# ******************************************************************************/


class DatabaseError(Exception):
    """
    Exception base class for database operation errors
    """

    def __init__(self, error) -> None:
        self.error = error

    def __str__(self) -> str:
        return f'Database error:{self.error}'


class DatabaseConnectionFailed(DatabaseError):
    """
    Database connection error
    """

    def __str__(self) -> str:
        return f'Database connection failed to be established: {self.error}'
