#!/usr/bin/env python3
# pylint: disable=duplicate-code
"""data classes for stack/biometric_aware.py


"""
import pytest
from aws_cdk import App, assertions
from tests.helper import Case
from deployments.cdk.stack.apprunner_stack import MockServiceAppRunnerStack
from deployments.cdk.stack.helper import StackConfig

SC = StackConfig(
    construct_id="test-mock-service",
    aws_account_number="709310380790",
    default_region="us-east-1",
    image_tag="latest",
)


@pytest.mark.unit
@pytest.mark.parametrize(
    "",
    [pytest.param(id="sandbox")],
)
def test_avd_apprunner_stack(request, update_golden):
    """Compare the EU Stacks to known good golden files"""

    case = Case(request)

    app = App()
    stk = MockServiceAppRunnerStack(
        app,
        construct_id=SC.construct_id,
        stack_cfg=SC,
    )

    template = assertions.Template.from_stack(stk)
    if update_golden:
        case.update_expected(template.to_json())

    template.template_matches(case.expected())
