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
import smtplib
from typing import List

from vulcanus.log.log import LOGGER


class Email:
    """
        provide email method
    """

    def __init__(self, server: str, port: int, sender: str, authorization_code: str):
        """
        Args:
            server(str): The mail server. e.g smtp.163.com
            port(int): the port number used by the SMTP service
            sender(str): sender email address
            authorization_code(str)
        """
        self.sender = sender
        self.server = server
        self.port = port
        self.authorization_code = authorization_code

    def send(self, receivers: List[str], message, smtp_ssl=False, timeout=3):
        """
        connect email server and send email

        Args:
            receivers(list): receiver email address list
            message:email body, it contains text, photos, file
            smtp_ssl(bool): use smtp server or smtp_ssl server
            timeout: the maximum timeout for connection
        Returns:
            tuple(result, log)
        """
        try:
            if smtp_ssl:
                server = smtplib.SMTP_SSL(host=self.server, timeout=timeout)
            else:
                server = smtplib.SMTP(host=self.server, timeout=timeout)
            server.connect(self.server, self.port)
            server.login(self.sender, self.authorization_code)
            server.sendmail(self.sender, receivers, message.as_string())
            server.quit()
        except smtplib.SMTPException as error:
            LOGGER.error("send mail failed!")
            LOGGER.error(error)
            return False, error
        except Exception as error:
            LOGGER.error(error)
            return False, error
        return True, ""

    @staticmethod
    def turn_data_to_table_html(thead: List[str], tbody: List[List[str]]) -> str:
        """
        generate html table code

        Args:
            thead(list): table head data. e.g
                [column1,column2,column3 ... ]
            tbody(list): table body data. e.g
                [
                    [value1,value2,value3 ...], [value1,value2,value3 ...]
                ]

        Returns:
            <table style="xxxx">
                <tr>
                    <th>...</th>
                    ...
                </tr>
                <tr>
                    <td>...</td>
                    ...
                </tr>
            </table>
        """
        table_html = '<table border="1" border="1" cellpadding="5" cellspacing="0" ' \
                     'style="text-align: center;border-collapse:collapse"  width="100%"><tr>'
        for column in thead:
            table_html += f'<th>{column}</th>'
        table_html += '</tr>'

        for row in tbody:
            table_html += '<tr>'
            for item in row:
                table_html += f'<td>{item}</td>'
            table_html += "</tr>"
        table_html += "</table>"
        return table_html
