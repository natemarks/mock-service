#!/usr/bin/env python3
"""Custom pytest options

"""
import pytest


def pytest_addoption(parser):
    """enable boolean switch to update golden files"""
    parser.addoption(
        "--update_golden", action="store_true", help="update the golden files"
    )


@pytest.fixture
def update_golden(request):
    """return True if the update_golden flag was set"""
    return request.config.getoption("--update_golden")
