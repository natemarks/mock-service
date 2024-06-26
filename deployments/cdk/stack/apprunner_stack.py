#!/usr/bin/env python3
# pylint: disable=duplicate-code,line-too-long
""" stack module"""
from dataclasses import dataclass
from constructs import Construct
from aws_cdk import (
    Stack,
    aws_iam as iam,
    aws_apprunner as apprunner,
)
from .helper import ecr_image


@dataclass
class AppRunnerStackConfig:
    """AppRunnerStackConfig class"""

    prefix: str
    construct_id: str
    aws_account_number: str
    default_region: str
    image_tag: str


AR_STACK_CONFIG = AppRunnerStackConfig(
    prefix="MockService",
    construct_id="mock-service-app-runner",
    aws_account_number="709310380790",
    default_region="us-east-1",
    image_tag="latest",
)


class MockServiceAppRunnerStack(Stack):
    """stack class"""

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        stack_cfg: AppRunnerStackConfig,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.stack_cfg = stack_cfg
        app_runner_role = iam.Role(
            self,
            f"{stack_cfg.prefix}AppRunnerRole",
            assumed_by=iam.ServicePrincipal("build.apprunner.amazonaws.com"),
        )
        app_runner_role.add_to_policy(
            iam.PolicyStatement(
                resources=["*"],
                actions=[
                    "ecr:GetDownloadUrlForLayer",
                    "ecr:BatchCheckLayerAvailability",
                    "ecr:BatchGetImage",
                    "ecr:DescribeImages",
                    "ecr:GetAuthorizationToken",
                ],
            )
        )
        apprunner.CfnService(
            self,
            stack_cfg.prefix,
            service_name="mock-service",
            source_configuration=apprunner.CfnService.SourceConfigurationProperty(
                authentication_configuration=apprunner.CfnService.AuthenticationConfigurationProperty(
                    access_role_arn=app_runner_role.role_arn
                ),
                auto_deployments_enabled=True,
                image_repository=apprunner.CfnService.ImageRepositoryProperty(
                    image_identifier=ecr_image(
                        stack_cfg.aws_account_number,
                        stack_cfg.default_region,
                        stack_cfg.image_tag,
                    ),
                    image_repository_type="ECR",
                    # the properties below are optional
                    image_configuration=apprunner.CfnService.ImageConfigurationProperty(
                        # port="port",
                        # runtime_environment_secrets=[apprunner.CfnService.KeyValuePairProperty(
                        #     name="name",
                        #     value="value"
                        # )],
                        runtime_environment_variables=[
                            apprunner.CfnService.KeyValuePairProperty(
                                name="SERVICE_GRACEFUL_SHUTDOWN_TIMEOUT",
                                value="20000ms",
                            )
                        ],
                        # start_command="startCommand"
                    ),
                ),
            ),
            # the properties below are optional
            # auto_scaling_configuration_arn="autoScalingConfigurationArn",
            # encryption_configuration=apprunner.CfnService.EncryptionConfigurationProperty(
            #     kms_key="kmsKey"
            # ),
            health_check_configuration=apprunner.CfnService.HealthCheckConfigurationProperty(
                healthy_threshold=1,  # default: 1
                interval=5,  # default: 5
                path="/ping",  # default: /
                protocol="HTTP",  # default: TCP
                timeout=2,  # default: 2
                unhealthy_threshold=5,  # default: 5
            ),
            # instance_configuration=apprunner.CfnService.InstanceConfigurationProperty(
            #     cpu="cpu",
            #     instance_role_arn="instanceRoleArn",
            #     memory="memory"
            # ),
            # network_configuration=apprunner.CfnService.NetworkConfigurationProperty(
            #     egress_configuration=apprunner.CfnService.EgressConfigurationProperty(
            #         egress_type="egressType",
            #
            #         # the properties below are optional
            #         vpc_connector_arn="vpcConnectorArn"
            #     ),
            #     ingress_configuration=apprunner.CfnService.IngressConfigurationProperty(
            #         is_publicly_accessible=False
            #     ),
            #     ip_address_type="ipAddressType"
            # ),
            # observability_configuration=apprunner.CfnService.ServiceObservabilityConfigurationProperty(
            #     observability_enabled=False,
            #
            #     # the properties below are optional
            #     observability_configuration_arn="observabilityConfigurationArn"
            # )
        )
