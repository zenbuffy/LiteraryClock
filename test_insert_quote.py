#!/usr/bin/env python3
import tempfile
import time
import unittest

import yaml

from insert_quote import yaml_insert

FIXTURE = [
    {"time": "08:00", "time_name": "eight o'clock", "source": "Book A", "author": "Author A", "quote": "Quote at eight."},
    {"time": "12:00", "time_name": "noon",           "source": "Book B", "author": "Author B", "quote": "Quote at noon."},
    {"time": "18:00", "time_name": "six o'clock",    "source": "Book C", "author": "Author C", "quote": "Quote at six."},
]


def make_temp_yaml(content):
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False)
    f.write(yaml.dump(content, allow_unicode=True, sort_keys=True))
    f.close()
    return f.name


def load_yaml(path):
    with open(path) as f:
        return yaml.safe_load(f)


def t(hhmm):
    return time.strptime(hhmm, "%H:%M")


class TestInsertionPosition(unittest.TestCase):

    def test_insert_in_middle(self):
        path = make_temp_yaml(FIXTURE)
        yaml_insert(t("10:00"), "ten o'clock", "Book D", "Author D", "Quote at ten.", filepath=path)
        result = load_yaml(path)
        times = [e["time"] for e in result]
        self.assertEqual(times, ["08:00", "10:00", "12:00", "18:00"])

    def test_insert_before_first(self):
        path = make_temp_yaml(FIXTURE)
        yaml_insert(t("06:00"), "six in the morning", "Book E", "Author E", "Early quote.", filepath=path)
        result = load_yaml(path)
        self.assertEqual(result[0]["time"], "06:00")
        self.assertEqual(len(result), 4)

    def test_insert_after_last(self):
        path = make_temp_yaml(FIXTURE)
        yaml_insert(t("23:00"), "eleven at night", "Book F", "Author F", "Late quote.", filepath=path)
        result = load_yaml(path)
        self.assertEqual(result[-1]["time"], "23:00")
        self.assertEqual(len(result), 4)

    def test_insert_at_same_time_as_existing(self):
        path = make_temp_yaml(FIXTURE)
        yaml_insert(t("12:00"), "noon", "Book G", "Author G", "Another noon quote.", filepath=path)
        result = load_yaml(path)
        noon_entries = [e for e in result if e["time"] == "12:00"]
        self.assertEqual(len(noon_entries), 2)


class TestDataIntegrity(unittest.TestCase):

    def test_all_fields_written(self):
        path = make_temp_yaml(FIXTURE)
        yaml_insert(t("10:00"), "ten o'clock", "My Book", "My Author", "My quote.", filepath=path)
        result = load_yaml(path)
        entry = next(e for e in result if e["source"] == "My Book")
        self.assertEqual(entry["time"], "10:00")
        self.assertEqual(entry["time_name"], "ten o'clock")
        self.assertEqual(entry["source"], "My Book")
        self.assertEqual(entry["author"], "My Author")
        self.assertEqual(entry["quote"], "My quote.")

    def test_existing_entries_preserved(self):
        path = make_temp_yaml(FIXTURE)
        yaml_insert(t("10:00"), "ten o'clock", "Book D", "Author D", "New quote.", filepath=path)
        result = load_yaml(path)
        sources = [e["source"] for e in result]
        self.assertIn("Book A", sources)
        self.assertIn("Book B", sources)
        self.assertIn("Book C", sources)

    def test_output_is_valid_yaml(self):
        path = make_temp_yaml(FIXTURE)
        yaml_insert(t("10:00"), "ten o'clock", "Book D", "Author D", "New quote.", filepath=path)
        result = load_yaml(path)
        self.assertIsInstance(result, list)
        self.assertTrue(all(isinstance(e, dict) for e in result))


class TestSpecialCharacters(unittest.TestCase):

    def test_double_quotes_in_quote(self):
        path = make_temp_yaml(FIXTURE)
        yaml_insert(t("10:00"), "ten o'clock", "Ulysses", "James Joyce",
                    '"But wait till I tell you," he said.', filepath=path)
        result = load_yaml(path)
        entry = next(e for e in result if e["source"] == "Ulysses")
        self.assertEqual(entry["quote"], '"But wait till I tell you," he said.')

    def test_single_quotes_in_quote(self):
        path = make_temp_yaml(FIXTURE)
        yaml_insert(t("10:00"), "ten o'clock", "Some Book", "Some Author",
                    "It's a fine day, isn't it?", filepath=path)
        result = load_yaml(path)
        entry = next(e for e in result if e["source"] == "Some Book")
        self.assertEqual(entry["quote"], "It's a fine day, isn't it?")

    def test_em_dash_and_unicode(self):
        path = make_temp_yaml(FIXTURE)
        yaml_insert(t("10:00"), "ten o'clock", "Some Book", "Some Author",
                    "Time\u2014the great healer.", filepath=path)
        result = load_yaml(path)
        entry = next(e for e in result if e["author"] == "Some Author")
        self.assertEqual(entry["quote"], "Time\u2014the great healer.")

    def test_mixed_quotes_round_trip(self):
        path = make_temp_yaml(FIXTURE)
        quote = "\"It's over,\" she said\u2014and meant it."
        yaml_insert(t("10:00"), "ten o'clock", "Novel", "Writer", quote, filepath=path)
        result = load_yaml(path)
        entry = next(e for e in result if e["source"] == "Novel")
        self.assertEqual(entry["quote"], quote)


if __name__ == "__main__":
    unittest.main()
