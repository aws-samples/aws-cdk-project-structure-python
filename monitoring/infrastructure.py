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

from aws_cdk import aws_cloudwatch as cloudwatch
from aws_cdk import aws_sam as sam
from aws_cdk import core as cdk

from api.infrastructure import API
from database.infrastructure import Database


class Monitoring(cdk.Construct):
    def __init__(self, scope: cdk.Construct, id_: str, *, database: Database, api: API):
        super().__init__(scope, id_)

        apigateway: sam.CfnApi = api.chalice.sam_template.get_resource("RestAPI")
        apigateway_metric_dimensions = {"ApiName": cdk.Fn.ref(apigateway.logical_id)}
        apigateway_metric_count = cloudwatch.Metric(
            namespace="AWS/APIGateway",
            metric_name="Count",
            dimensions=apigateway_metric_dimensions,
        )
        widgets = [
            cloudwatch.SingleValueWidget(metrics=[apigateway_metric_count]),
            cloudwatch.SingleValueWidget(
                metrics=[database.table.metric_consumed_read_capacity_units()]
            ),
        ]
        cloudwatch.Dashboard(self, "Dashboard", widgets=[widgets])
