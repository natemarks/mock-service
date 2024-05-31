#!/usr/bin/env python3
# pylint: disable=duplicate-code
"""EKS stack module.
"""
from dataclasses import dataclass
from constructs import Construct
from aws_cdk import (
    Stack,
    aws_eks as eks,
    aws_ecr as ecr,
)


@dataclass
class EKSStackConfig:
    """FargateStackConfig class"""

    prefix: str
    construct_id: str
    aws_account_number: str
    default_region: str
    image_tag: str


EKS_STACK_CONFIG = EKSStackConfig(
    prefix="EKSMockService",
    construct_id="mock-service-eks",
    aws_account_number="709310380790",
    default_region="us-east-1",
    image_tag="latest",
)


class MockServiceEKSStack(
    Stack
):  # pylint: disable=too-many-instance-attributes
    """MockServiceEKSStack"""

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        stack_cfg: EKSStackConfig,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        access_config = eks.CfnCluster.AccessConfigProperty(
            authentication_mode="API_AND_CONFIG_MAP",
            bootstrap_cluster_creator_admin_permissions=False,
        )
        eks_cluster = eks.Cluster(
            self,
            stack_cfg.prefix,
            version=eks.KubernetesVersion.V1_29,
        )
        ecr_repository = ecr.Repository.from_repository_name(
            self, f"{stack_cfg.prefix}Repo", "mock-service"
        )
        # apply a kubernetes manifest to the cluster
        eks_cluster.add_manifest(
            f"{stack_cfg.prefix}Pod",
            {
                "apiVersion": "apps/v1",
                "kind": "Deployment",
                "metadata": {"name": "mock-service"},
                "spec": {
                    "replicas": 2,
                    "selector": {"matchLabels": {"app": "mock-service"}},
                    "template": {
                        "metadata": {"labels": {"app": "mock-service"}},
                        "spec": {
                            "containers": [
                                {
                                    "name": "mock-service",
                                    "image": f"{ecr_repository.repository_uri}:latest",
                                    "ports": [{"containerPort": 8080}],
                                }
                            ]
                        },
                    },
                },
            },
        )
        eks.AlbController(
            self,
            f"{stack_cfg.prefix}ALBController",
            cluster=eks_cluster,
            version=eks.AlbControllerVersion.V2_6_2,
            # the properties below are optional
            # policy=policy,
            # repository="repository"
        )
