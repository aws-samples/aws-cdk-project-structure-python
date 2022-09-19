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

import unittest

import aws_cdk as cdk
import aws_cdk.aws_dynamodb as dynamodb
from aws_cdk import assertions

from backend.api.infrastructure import API
from backend.database.infrastructure import Database


class APITestCase(unittest.TestCase):
    def test_lambda_function_bundling(self) -> None:
        stack = cdk.Stack()
        database = Database(
            stack,
            "Database",
            dynamodb_billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
        )
        API(
            stack,
            "API",
            dynamodb_table_name=database.dynamodb_table.table_name,
            lambda_reserved_concurrency=1,
        )
        template = assertions.Template.from_stack(stack).to_json()
        lambda_function_code_property = template["Resources"][
            "APILambdaFunction0BD6F5C6"
        ]["Properties"]["Code"]
        self.assertIn("S3Bucket", lambda_function_code_property)
        self.assertIn("S3Key", lambda_function_code_property)


if __name__ == "__main__":
    unittest.main()
