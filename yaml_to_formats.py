#!/usr/bin/env python3
import json
import yaml

FIELDS = ["time", "time_name", "quote", "source", "author"]


def convert(yaml_path="litclock.yaml", json_path="litclock.json", csv_path="litclock_annotated_improved.csv"):
    with open(yaml_path, encoding="utf-8") as f:
        entries = yaml.safe_load(f)

    if json_path is not None:
        ordered = [{field: entry[field] for field in FIELDS} for entry in entries]
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(ordered, f, indent=4, ensure_ascii=False)
            f.write("\n")

    if csv_path is not None:
        with open(csv_path, "w", encoding="utf-8") as f:
            for entry in entries:
                row = "|".join(entry[field] for field in FIELDS)
                f.write(row + "\n")


if __name__ == "__main__":
    convert()
