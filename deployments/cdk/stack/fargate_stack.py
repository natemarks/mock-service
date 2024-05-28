#!/usr/bin/env python3
# pylint: disable=duplicate-code
"""Test ecs with cloudwatch logs
"""
from dataclasses import dataclass
from constructs import Construct
from aws_cdk import (
    Aws,
    RemovalPolicy,
    Stack,
    aws_ecr as ecr,
    aws_ecs as ecs,
    aws_logs as logs,
    aws_ecs_patterns as ecs_patterns,
)


@dataclass
class FargateStackConfig:
    """FargateStackConfig class"""

    prefix: str
    construct_id: str
    aws_account_number: str
    default_region: str
    image_tag: str


FG_STACK_CONFIG = FargateStackConfig(
    prefix="MockService",
    construct_id="mock-service-fargate",
    aws_account_number="709310380790",
    default_region="us-east-1",
    image_tag="latest",
)


class MockServiceFargateStack(
    Stack
):  # pylint: disable=too-many-instance-attributes
    """MockServiceFargateStack"""

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        stack_cfg: FargateStackConfig,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        my_log_group = logs.LogGroup(
            self,
            f"{stack_cfg.prefix}LogGroup",
            log_group_name=f"/ecs/{Aws.STACK_NAME}",
            removal_policy=RemovalPolicy.DESTROY,
            retention=logs.RetentionDays.TWO_WEEKS,
        )

        # Create CloudWatch log driver
        my_log_driver = ecs.LogDriver.aws_logs(
            log_group=my_log_group, stream_prefix=f"{stack_cfg.prefix}Fargate"
        )

        my_ecr = ecr.Repository.from_repository_name(
            self,
            f"{stack_cfg.prefix}ECRRepository",
            repository_name="mock-service",
        )

        # Create an ECS cluster
        ecs_cluster = ecs.Cluster(
            self,
            f"{stack_cfg.prefix}Cluster",
        )

        ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            "MyFargateService",
            cluster=ecs_cluster,  # Required
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_ecr_repository(
                    repository=my_ecr, tag=stack_cfg.image_tag
                ),
                log_driver=my_log_driver,
                container_port=8080,
                enable_logging=True,
            ),
            public_load_balancer=True,
        )  # Default is True
