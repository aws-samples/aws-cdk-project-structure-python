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
import pathlib
import tempfile
import unittest

from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import core as cdk

from api.infrastructure import API
from database.infrastructure import Database


class APITestCase(unittest.TestCase):
    def test_endpoint_url_output_exists(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            app = cdk.App(outdir=temp_dir)
            stack = cdk.Stack(app, "Stack")
            database = Database(
                stack,
                "Database",
                dynamodb_billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            )
            API(
                stack,
                "API",
                dynamodb_table=database.table,
                lambda_reserved_concurrency=1,
            )
            cloud_assembly = app.synth()
            template = cloud_assembly.get_stack_by_name(stack.stack_name).template
        self.assertEqual(
            template["Outputs"]["EndpointURL"]["Value"]["Fn::Sub"],
            "https://${RestAPI}.execute-api.${AWS::Region}.${AWS::URLSuffix}/v1/",
        )
        self._cleanup_chalice_config_file(f"{stack.stack_name}/API")

    @staticmethod
    def _cleanup_chalice_config_file(stage_name: str) -> None:
        chalice_config_path = (
            pathlib.Path(__file__)
            .resolve()
            .parent.parent.joinpath("api/runtime/.chalice/config.json")
        )
        with pathlib.Path.open(chalice_config_path, "r+") as chalice_config_file:
            chalice_config = json.load(chalice_config_file)
            try:
                del chalice_config["stages"][stage_name]
            except KeyError:
                return
            else:
                chalice_config_file.seek(0)
                chalice_config_file.truncate()
                json.dump(chalice_config, chalice_config_file, indent=2)


if __name__ == "__main__":
    unittest.main()
