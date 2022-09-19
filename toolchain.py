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
from typing import Any

import aws_cdk as cdk
import aws_cdk.aws_codebuild as codebuild
import aws_cdk.aws_dynamodb as dynamodb
from aws_cdk import pipelines
from constructs import Construct

import constants
from backend.component import Backend

GITHUB_CONNECTION_ARN = "CONNECTION_ARN"
GITHUB_OWNER = "OWNER"
GITHUB_REPO = "REPO"
GITHUB_TRUNK_BRANCH = "TRUNK_BRANCH"
PRODUCTION_ENV_NAME = "Production"
PRODUCTION_ENV_ACCOUNT = "222222222222"
PRODUCTION_ENV_REGION = "eu-west-1"


class Toolchain(cdk.Stack):
    def __init__(self, scope: Construct, id_: str, **kwargs: Any):
        super().__init__(scope, id_, **kwargs)

        source = pipelines.CodePipelineSource.connection(
            GITHUB_OWNER + "/" + GITHUB_REPO,
            GITHUB_TRUNK_BRANCH,
            connection_arn=GITHUB_CONNECTION_ARN,
        )
        build_spec = {"phases": {"install": {"runtime-versions": {"python": "3.7"}}}}
        synth = pipelines.CodeBuildStep(
            "Synth",
            input=source,
            partial_build_spec=codebuild.BuildSpec.from_object(build_spec),
            install_commands=["./scripts/install-deps.sh"],
            commands=["./scripts/run-tests.sh", "npx cdk synth"],
            primary_output_directory="cdk.out",
        )
        pipeline = pipelines.CodePipeline(
            self,
            "Pipeline",
            cli_version=Toolchain._get_cdk_cli_version(),
            cross_account_keys=True,
            docker_enabled_for_synth=True,
            publish_assets_in_parallel=False,
            synth=synth,
        )
        Toolchain._add_production_stage(pipeline)

    @staticmethod
    def _get_cdk_cli_version() -> str:
        package_json_path = (
            pathlib.Path(__file__).parent.joinpath("package.json").resolve()
        )
        with open(package_json_path, encoding="utf_8") as package_json_file:
            package_json = json.load(package_json_file)
        cdk_cli_version = str(package_json["devDependencies"]["aws-cdk"])
        return cdk_cli_version

    @staticmethod
    def _add_production_stage(pipeline: pipelines.CodePipeline) -> None:
        production = cdk.Stage(
            pipeline,
            PRODUCTION_ENV_NAME,
            env=cdk.Environment(
                account=PRODUCTION_ENV_ACCOUNT, region=PRODUCTION_ENV_REGION
            ),
        )
        backend = Backend(
            production,
            constants.APP_NAME + PRODUCTION_ENV_NAME,
            stack_name=constants.APP_NAME + PRODUCTION_ENV_NAME,
            api_lambda_reserved_concurrency=10,
            database_dynamodb_billing_mode=dynamodb.BillingMode.PROVISIONED,
        )
        api_endpoint_env_var_name = constants.APP_NAME.upper() + "_API_ENDPOINT"
        smoke_test_commands = [f"curl ${api_endpoint_env_var_name}"]
        smoke_test = pipelines.ShellStep(
            "SmokeTest",
            env_from_cfn_outputs={api_endpoint_env_var_name: backend.api_endpoint},
            commands=smoke_test_commands,
        )
        pipeline.add_stage(production, post=[smoke_test])
