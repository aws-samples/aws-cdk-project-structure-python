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

import pathlib
from typing import Any, Dict

import cdk_chalice
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_iam as iam
from aws_cdk import core as cdk


class API(cdk.Construct):
    def __init__(
        self,
        scope: cdk.Construct,
        id_: str,
        *,
        dynamodb_table: dynamodb.Table,
        lambda_reserved_concurrency: int,
    ):
        super().__init__(scope, id_)

        service_principal = iam.ServicePrincipal("lambda.amazonaws.com")
        # This policy is used for writing to Amazon CloudWatch Logs
        policy = iam.ManagedPolicy.from_aws_managed_policy_name(
            "service-role/AWSLambdaBasicExecutionRole"
        )
        handler_role = iam.Role(
            self,
            "HandlerRole",
            assumed_by=service_principal,
            managed_policies=[policy],
        )

        dynamodb_table.grant_read_write_data(handler_role)

        stage_config = API._create_chalice_stage_config(
            handler_role, dynamodb_table, lambda_reserved_concurrency
        )
        source_dir = pathlib.Path(__file__).resolve().parent.joinpath("runtime")
        self.chalice = cdk_chalice.Chalice(
            self,
            "Chalice",
            source_dir=str(source_dir),
            stage_config=stage_config,
        )

        self.endpoint_url: cdk.CfnOutput = self.chalice.sam_template.get_output(
            "EndpointURL"
        )

    @staticmethod
    def _create_chalice_stage_config(
        handler_role: iam.Role,
        dynamodb_table: dynamodb.Table,
        lambda_reserved_concurrency: int,
    ) -> Dict[str, Any]:
        chalice_stage_config = {
            "api_gateway_stage": "v1",
            "lambda_functions": {
                "api_handler": {
                    "manage_iam_role": False,
                    "iam_role_arn": handler_role.role_arn,
                    "environment_variables": {"TABLE_NAME": dynamodb_table.table_name},
                    "reserved_concurrency": lambda_reserved_concurrency,
                }
            },
        }
        return chalice_stage_config
