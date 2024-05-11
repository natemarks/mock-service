#!/usr/bin/env python3
""" project data module


"""

from dataclasses import dataclass

import boto3


@dataclass
class StackConfig:
    """StackConfig class"""

    construct_id: str
    aws_account_number: str
    default_region: str
    image_tag: str


def check_account_number(expected_account_number: str):
    """raise exception if the current account number doesn't match the expected"""
    sts_client = boto3.client("sts")
    response = sts_client.get_caller_identity()
    if response["Account"] != expected_account_number:
        raise ValueError(
            f"Unexpected AWS account number. Expected: {expected_account_number}, "
            f"Got: {response['Account']}"
        )
