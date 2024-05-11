#!/usr/bin/env python3
"""Helper functions for pytest


"""
import json
import os
import pathlib
import pytest


class Case:
    """A test case

    This class is used by pytests to access the input and expected data
    files for a particular test case. The tests/data direcotry tree mirrors the tests/
    modules directory tree

    For parametrize (table) tests, a test module: tests/unit/policy/test_inline.py
    containing a test function: test_red_policy
    having a test case id: 111

    would have its input file:
    tests/data/tests/unit/policy/test_inline/test_red_policy/111/input.json
    and expected file:
    tests/data/tests/unit/policy/test_inline/test_red_policy/111/expected.json

    For tests that have a single test case (not table tests)
    would have its input file:
    tests/data/tests/unit/policy/test_inline/test_red_policy/input.json
    and expected file:
    tests/data/tests/unit/policy/test_inline/test_red_policy/expected.json

    """

    def __init__(self, request: pytest.FixtureRequest):
        self.request = request  # type: pytest.FixtureRequest
        self.test_dir = pathlib.Path(__file__).parent
        self.data_dir = str(self.test_dir / "data")
        self.module_dir = self.request.node.location[0].removesuffix(".py")
        self.function_name = request.node.originalname
        try:
            self.case_name = request.node.callspec.id
        except AttributeError:
            self.case_name = ""

    def case_dir(self):
        """return the file path to the current case input file"""
        return os.path.join(
            self.data_dir, self.module_dir, self.function_name, self.case_name
        )

    def update_expected(self, data, file_name="expected.json"):
        """save expected/golden file"""
        os.makedirs(self.case_dir(), mode=0o755, exist_ok=True)
        file_path = os.path.join(self.case_dir(), file_name)
        with open(file_path, "w", encoding="utf-8") as outfile:
            outfile.write(json.dumps(data, indent=4))

    def input(self):
        """assuming the input file is JSON, return the data"""
        file_path = os.path.join(self.case_dir(), "input.json")
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        return data

    def input_contents(self):
        """return the contents of the input file"""
        file_path = os.path.join(self.case_dir(), "input.json")
        with open(file_path, "r", encoding="utf-8") as file:
            data = file.read()
        return data

    def expected(self):
        """assuming the expected file is JSON, return the data"""
        file_path = os.path.join(self.case_dir(), "expected.json")
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        return data

    def read_json(self, file_name: str):
        """assuming the expected file is JSON, return the data"""
        file_path = os.path.join(self.case_dir(), file_name)
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        return data
