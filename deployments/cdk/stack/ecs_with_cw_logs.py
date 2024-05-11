#!/usr/bin/env python3
"""Test ecs with cloudwatch logs
"""

from aws_cdk import (
    Aws,
    RemovalPolicy,
    Stack,
    aws_ecr as ecr,
    aws_ecs as ecs,
    aws_iam as iam,
    aws_logs as logs,
)
from constructs import Construct

ID_PREFIX = "TestECSWithCWLogs"


class TestECSWithCWLogstack(
    Stack
):  # pylint: disable=too-many-instance-attributes
    """RDS stack subclass"""

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        my_log_group = logs.LogGroup(
            self,
            f"{ID_PREFIX}LogGroup",
            log_group_name=f"/ecs/{Aws.STACK_NAME}",
            removal_policy=RemovalPolicy.DESTROY,
            retention=logs.RetentionDays.TWO_WEEKS,
        )
        my_ecr = ecr.Repository.from_repository_name(
            self,
            f"{ID_PREFIX}ECRRepository",
            repository_name="ecs_with_cw_logs",
        )

        # Create an ECS cluster
        ecs_cluster = ecs.Cluster(
            self,
            f"{ID_PREFIX}Cluster",
        )

        # Create a task definition
        task_definition = ecs.FargateTaskDefinition(
            self,
            f"{ID_PREFIX}TaskDefinition",
        )

        # Create CloudWatch log driver
        my_log_driver = ecs.LogDriver.aws_logs(
            log_group=my_log_group, stream_prefix=ID_PREFIX
        )

        # Add container to the task definition
        task_definition.add_container(
            f"{ID_PREFIX}Container",
            image=ecs.ContainerImage.from_ecr_repository(my_ecr),
            memory_limit_mib=512,  # Adjust as needed
            cpu=256,  # Adjust as needed
            logging=my_log_driver,
        )

        # Optionally, add IAM role for task execution
        iam.Role(
            self,
            f"{ID_PREFIX}TaskExecutionRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AmazonECSTaskExecutionRolePolicy"
                )
            ],
        )

        # Create ECS service
        ecs.FargateService(
            self,
            f"{ID_PREFIX}Service",
            cluster=ecs_cluster,
            task_definition=task_definition,
            desired_count=1,  # Adjust as needed
        )
