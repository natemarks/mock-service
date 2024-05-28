#!/usr/bin/env python3
# pylint: disable=duplicate-code
"""EKS stack module.
"""
from dataclasses import dataclass
from constructs import Construct
from aws_cdk import (
    Stack,
    aws_eks as eks,
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
        eks_cluster = eks.Cluster(
            self,
            stack_cfg.prefix,
            version=eks.KubernetesVersion.V1_29,
        )
        # apply a kubernetes manifest to the cluster
        eks_cluster.add_manifest(
            f"{stack_cfg.prefix}Pod",
            {
                "api_version": "v1",
                "kind": "Pod",
                "metadata": {"name": "mypod"},
                "spec": {
                    "containers": [
                        {
                            "name": "hello",
                            "image": "paulbouwer/hello-kubernetes:1.5",
                            "ports": [{"container_port": 8080}],
                        }
                    ]
                },
            },
        )
