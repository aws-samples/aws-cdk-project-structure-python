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

from typing import Any

import aws_cdk as cdk
import aws_cdk.aws_dynamodb as dynamodb
from constructs import Construct

from backend.api.infrastructure import API
from backend.database.infrastructure import Database
from backend.monitoring.infrastructure import Monitoring


class Backend(cdk.Stack):
    def __init__(
        self,
        scope: Construct,
        id_: str,
        *,
        database_dynamodb_billing_mode: dynamodb.BillingMode,
        api_lambda_reserved_concurrency: int,
        **kwargs: Any,
    ):
        super().__init__(scope, id_, **kwargs)

        database = Database(
            self,
            "Database",
            dynamodb_billing_mode=database_dynamodb_billing_mode,
        )
        api = API(
            self,
            "API",
            dynamodb_table_name=database.dynamodb_table.table_name,
            lambda_reserved_concurrency=api_lambda_reserved_concurrency,
        )
        Monitoring(self, "Monitoring", database=database, api=api)

        database.dynamodb_table.grant_read_write_data(api.lambda_function)

        self.api_endpoint = cdk.CfnOutput(
            self,
            "APIEndpoint",
            # API doesn't disable create_default_stage, hence URL will be defined
            value=api.api_gateway_http_api.url,  # type: ignore
        )
