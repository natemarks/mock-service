#!/usr/bin/env python3
""" project data module


"""


import boto3


def check_account_number(expected_account_number: str):
    """raise exception if the current account number doesn't match the expected"""
    sts_client = boto3.client("sts")
    response = sts_client.get_caller_identity()
    if response["Account"] != expected_account_number:
        raise ValueError(
            f"Unexpected AWS account number. Expected: {expected_account_number}, "
            f"Got: {response['Account']}"
        )


def ecr_image(aws_account_number: str, region: str, image_tag: str):
    """return the ECR image"""
    return f"{aws_account_number}.dkr.ecr.{region}.amazonaws.com/mock-service:{image_tag}"
