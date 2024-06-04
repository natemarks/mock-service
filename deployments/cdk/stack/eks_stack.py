#!/usr/bin/env python3
# pylint: disable=duplicate-code
"""EKS stack module.
"""
from dataclasses import dataclass
from constructs import Construct
from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_eks as eks,
    aws_ecr as ecr,
    aws_iam as iam,
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
        self.vpc = ec2.Vpc(
            self,
            f"{stack_cfg.prefix}VPC",
            max_azs=2,
            ip_addresses=ec2.IpAddresses.cidr("10.77.0.0/16"),
            vpc_name=f"{stack_cfg.prefix}VPC",
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="mock_service_eks_public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                ),
                ec2.SubnetConfiguration(
                    name="mock_service_eks_private",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                ),
                ec2.SubnetConfiguration(
                    name="mock_service_eks_isolated",
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                ),
            ],
        )
        # add VPC interface endpoints
        self.vpc.add_interface_endpoint(
            "EC2", service=ec2.InterfaceVpcEndpointAwsService.EC2
        )
        self.vpc.add_interface_endpoint(
            "EC2_MESSAGES",
            service=ec2.InterfaceVpcEndpointAwsService.EC2_MESSAGES,
        )
        self.vpc.add_interface_endpoint(
            "SSM", service=ec2.InterfaceVpcEndpointAwsService.SSM
        )
        self.vpc.add_interface_endpoint(
            "SSM_MESSAGES",
            service=ec2.InterfaceVpcEndpointAwsService.SSM_MESSAGES,
        )
        self.vpc.add_interface_endpoint(
            "SECRETS_MANAGER",
            service=ec2.InterfaceVpcEndpointAwsService.SECRETS_MANAGER,
        )
        access_config = eks.CfnCluster.AccessConfigProperty(
            authentication_mode="API_AND_CONFIG_MAP",
            bootstrap_cluster_creator_admin_permissions=True,
        )
        private_subnets = self.vpc.select_subnets(
            subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
        )
        private_subnet_ids = [
            subnet.subnet_id for subnet in private_subnets.subnets
        ]
        resources_vpc_config = eks.CfnCluster.ResourcesVpcConfigProperty(
            subnet_ids=private_subnet_ids,
            # the properties below are optional
            endpoint_private_access=True,
            endpoint_public_access=True,
            public_access_cidrs=["0.0.0.0/0"],
        )
        eks_role = iam.Role(
            self,
            f"{stack_cfg.prefix}EksRole",
            assumed_by=iam.ServicePrincipal("eks.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonEKSClusterPolicy"
                ),
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonEKSVPCResourceController"
                ),
            ],
        )
        eks_cluster = eks.CfnCluster(
            self,
            stack_cfg.prefix,
            name="mock-service",
            version="1.30",
            access_config=access_config,
            resources_vpc_config=resources_vpc_config,
            role_arn=eks_role.role_arn,
        )
        repo = ecr.Repository.from_repository_name(
            self, f"{stack_cfg.prefix}Repo", "mock-service"
        )
        # apply a kubernetes manifest to the cluster
        # eks_cluster.add_manifest(
        #     f"{stack_cfg.prefix}Pod",
        #     {
        #         "apiVersion": "apps/v1",
        #         "kind": "Deployment",
        #         "metadata": {"name": "mock-service"},
        #         "spec": {
        #             "replicas": 2,
        #             "selector": {"matchLabels": {"app": "mock-service"}},
        #             "template": {
        #                 "metadata": {"labels": {"app": "mock-service"}},
        #                 "spec": {
        #                     "containers": [
        #                         {
        #                             "name": "mock-service",
        #                             "image": f"{ecr_repository.repository_uri}:latest",
        #                             "ports": [{"containerPort": 8080}],
        #                         }
        #                     ]
        #                 },
        #             },
        #         },
        #     },
        # )
        # Add a Kubernetes manifest to the cluster

        # Define the kubectl role
        # pylint: disable=unused-variable
        kubectl_role = iam.Role(
            self,
            f"{stack_cfg.prefix}KctlRole",
            assumed_by=iam.AccountRootPrincipal(),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonEKSClusterPolicy"
                ),
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonEKSWorkerNodePolicy"
                ),
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonEC2ContainerRegistryReadOnly"
                ),
            ],
        )
        eks.KubernetesManifest(
            self,
            f"{stack_cfg.prefix}Pod",
            cluster=eks_cluster,
            manifest=[
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
                                        "image": f"{repo.repository_uri}:latest",
                                        "ports": [{"containerPort": 8080}],
                                    }
                                ]
                            },
                        },
                    },
                },
            ],
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
