# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import json
import unittest
from unittest import mock

from backend.api.runtime import lambda_function  # type: ignore


class AppTestCase(unittest.TestCase):
    @mock.patch.dict("helpers.os.environ", {"DYNAMODB_TABLE_NAME": "AppTestCase"})
    @mock.patch("users.DynamoDBDatabase.get_user")
    def test_get_user_exists(self, mock_get_user: mock.Mock) -> None:
        username = "john"
        user = {"username": username, "email": f"{username}@example.com"}
        mock_get_user.return_value = user
        apigatewayv2_proxy_event = {
            "rawPath": f"/users/{username}",
            "requestContext": {
                "http": {
                    "method": "GET",
                    "path": f"/users/{username}",
                },
                "stage": "$default",
            },
        }
        response = lambda_function.lambda_handler(apigatewayv2_proxy_event, None)
        self.assertEqual(json.loads(response["body"]), user)


if __name__ == "__main__":
    unittest.main()
