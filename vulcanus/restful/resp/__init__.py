#!/usr/bin/python3
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
from vulcanus.restful.resp.xmlmap import Response
from vulcanus.restful.resp import state


__all__ = ("Response", "state", "make_response")


def make_response(label: str, message: str = None, data=None):
    """
    Make response body

    Args:
        label: Status code of the service
        message: Custom message
        data: Data for the response body, typing list/dict/str

    Returns:
        {
            "label": "Scuueed",
            "code": 200,
            "message": "operation succeed"
            "data":
        }
    """
    response = Response(label=state.SUCCEED)
    return response.body(label=label, zh=False, message=message, data=data)
