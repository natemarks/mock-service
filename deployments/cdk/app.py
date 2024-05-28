#!/usr/bin/env python3
""" CDK entry point """

import aws_cdk as cdk

from stack.apprunner_stack import MockServiceAppRunnerStack, AR_STACK_CONFIG
from stack.fargate_stack import MockServiceFargateStack, FG_STACK_CONFIG
from stack.helper import (
    check_account_number,
)

app = cdk.App()

check_account_number(AR_STACK_CONFIG.aws_account_number)

cdk.Tags.of(app).add("iac", "gh:natemarks/mock-service")

MockServiceAppRunnerStack(
    app,
    construct_id=AR_STACK_CONFIG.construct_id,
    env=cdk.Environment(
        account=AR_STACK_CONFIG.aws_account_number,
        region=AR_STACK_CONFIG.default_region,
    ),
    stack_cfg=AR_STACK_CONFIG,
)

MockServiceFargateStack(
    app,
    construct_id=FG_STACK_CONFIG.construct_id,
    env=cdk.Environment(
        account=FG_STACK_CONFIG.aws_account_number,
        region=FG_STACK_CONFIG.default_region,
    ),
    stack_cfg=FG_STACK_CONFIG,
)
app.synth()
