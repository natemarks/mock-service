#!/usr/bin/env python3
# pylint: disable=duplicate-code
"""data classes for stack/biometric_aware.py


"""
import pytest
from aws_cdk import App, assertions
from tests.helper import Case
from deployments.cdk.stack.fargate_stack import (
    FG_STACK_CONFIG,
    MockServiceFargateStack,
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
    stk = MockServiceFargateStack(
        app,
        construct_id=FG_STACK_CONFIG.construct_id,
        stack_cfg=FG_STACK_CONFIG,
    )

    template = assertions.Template.from_stack(stk)
    if update_golden:
        case.update_expected(template.to_json())

    template.template_matches(case.expected())
