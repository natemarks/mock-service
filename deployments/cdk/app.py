#!/usr/bin/env python3
""" CDK entry point """

import aws_cdk as cdk

from stack.apprunner_stack import MockServiceAppRunnerStack
from stack.helper import (
    StackConfig,
    check_account_number,
)

app = cdk.App()


sc = StackConfig(
    construct_id="test-mock-service",
    aws_account_number="709310380790",
    default_region="us-east-1",
    image_tag="latest",
)
check_account_number(sc.aws_account_number)

# set the cdk_environment
cdk_env = cdk.Environment(
    account=sc.aws_account_number,
    region=sc.default_region,
)
cdk.Tags.of(app).add("iac", "gh:natemarks/mock-service")

MockServiceAppRunnerStack(
    app,
    construct_id=sc.construct_id,
    env=cdk_env,
    stack_cfg=sc,
)

app.synth()
