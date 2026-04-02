#!/usr/bin/env python3
import json
import os
import tempfile
import unittest

import yaml

from yaml_to_formats import convert

FIXTURE = [
    {"time": "00:00", "time_name": "midnight", "quote": "Hello.", "source": "Book A", "author": "Author A"},
    {"time": "12:00", "time_name": "noon", "quote": "Goodbye.", "source": "Book B", "author": "Author B"},
]


class TestConvertJson(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.tmpdir_path = self.tmpdir.name

    def tearDown(self):
        self.tmpdir.cleanup()

    def _make_temp_yaml(self, content):
        path = os.path.join(self.tmpdir_path, "test.yaml")
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(content, f, allow_unicode=True)
        return path

    def test_json_contains_all_entries(self):
        yaml_path = self._make_temp_yaml(FIXTURE)
        json_path = yaml_path.replace(".yaml", ".json")
        convert(yaml_path=yaml_path, json_path=json_path, csv_path=None)
        with open(json_path, encoding="utf-8") as f:
            result = json.load(f)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["time"], "00:00")
        self.assertEqual(result[1]["source"], "Book B")

    def test_json_field_order(self):
        yaml_path = self._make_temp_yaml(FIXTURE)
        json_path = yaml_path.replace(".yaml", ".json")
        convert(yaml_path=yaml_path, json_path=json_path, csv_path=None)
        with open(json_path, encoding="utf-8") as f:
            result = json.load(f)
        self.assertEqual(list(result[0].keys()), ["time", "time_name", "quote", "source", "author"])

    def test_json_unicode_preserved(self):
        fixture = [{"time": "01:00", "time_name": "one", "quote": "Time\u2014heals.", "source": "X", "author": "Y"}]
        yaml_path = self._make_temp_yaml(fixture)
        json_path = yaml_path.replace(".yaml", ".json")
        convert(yaml_path=yaml_path, json_path=json_path, csv_path=None)
        with open(json_path, encoding="utf-8") as f:
            result = json.load(f)
        self.assertEqual(result[0]["quote"], "Time\u2014heals.")


class TestConvertCsv(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.tmpdir_path = self.tmpdir.name

    def tearDown(self):
        self.tmpdir.cleanup()

    def _make_temp_yaml(self, content):
        path = os.path.join(self.tmpdir_path, "test.yaml")
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(content, f, allow_unicode=True)
        return path

    def test_csv_row_count(self):
        yaml_path = self._make_temp_yaml(FIXTURE)
        csv_path = yaml_path.replace(".yaml", ".csv")
        convert(yaml_path=yaml_path, json_path=None, csv_path=csv_path)
        with open(csv_path, encoding="utf-8") as f:
            lines = [line for line in f.readlines() if line.strip()]
        self.assertEqual(len(lines), 2)

    def test_csv_pipe_delimited_format(self):
        yaml_path = self._make_temp_yaml(FIXTURE)
        csv_path = yaml_path.replace(".yaml", ".csv")
        convert(yaml_path=yaml_path, json_path=None, csv_path=csv_path)
        with open(csv_path, encoding="utf-8") as f:
            first_line = f.readline().rstrip("\n")
        self.assertEqual(first_line, "00:00|midnight|Hello.|Book A|Author A")


if __name__ == "__main__":
    unittest.main()
