#!/usr/bin/env python3
import argparse
import csv
import json
import time
import yaml


def main(time_arg, time_human, source, author, quote, csv_fmt, yaml_fmt, json_fmt):
    """Redirect based on format.

    The main function accepts all the parsed arguments and redirects based on
    the format. This can be trimmed when there's only one format in the future.

    Args:
        time_arg: Time in 24h format as a string
        time_human: Human-readable time format as string. Eg: Midnight.
        source: The name of the literary work for the quote.
        author: The author of the literary work.
        quote: The text of the quote.
        csv_fmt: True if the output format is CSV.
        yaml_fmt: True if the output format is YAML.
        json_fmt: True if the output format is JSON.

    Returns:
        None
    """
    time_obj = time.strptime(time_arg, "%H:%M")
    if csv_fmt:
        csv_append(time_obj, time_human, source, author, quote)
    if yaml_fmt:
        yaml_append(time_obj, time_human, source, author, quote)
    if json_fmt:
        json_append(time_obj, time_human, source, author, quote)


def yaml_append(time_obj, time_human, source, author, quote):
    """Append to YAML.

    Appends to the YAML source file in the correct position based on time.

    Args:
        time_obj: Time in a time object
        time_human: Human-readable time format as string. Eg: Midnight.
        source: The name of the literary work for the quote.
        author: The author of the literary work.
        quote: The text of the quote.
        csv_fmt: True if the output format is CSV.
        yaml_fmt: True if the output format is YAML.
        json_fmt: True if the output format is JSON.

    Returns:
        None

    Raises:
        InvalidTimeException: The time was format could not be parsed.
    """
    content = []
    with open("litclock.yaml") as f:
        content = yaml.safe_load(f)
        for i, line in enumerate(content):
            if time.strptime(line["time"], "%H:%M") > time_obj:
                print(f"Inserting before {line}")
                content[i - 1 : i - 1] = [
                    {
                        "time": time.strftime("%H:%M", time_obj),
                        "time_name": time_human,
                        "source": source,
                        "author": author,
                        "quote": quote,
                    }
                ]
                break
    with open("litclock.yaml", "w") as f:
        f.write(yaml.dump(content))


class CustomDialect(csv.excel):
    delimiter = "|"


def csv_append(time_obj, time_human, source, author, quote):
    """Append to CSV.

    Appends to the CSV source file in the correct position based on time.

    Args:
        time_obj: Time in a time object.
        time_human: Human-readable time format as string. Eg: Midnight.
        source: The name of the literary work for the quote.
        author: The author of the literary work.
        quote: The text of the quote.
        csv_fmt: True if the output format is CSV.
        yaml_fmt: True if the output format is YAML.
        json_fmt: True if the output format is JSON.

    Returns:
        None

    Raises:
        InvalidTimeException: The time was format could not be parsed.
    """
    content = []
    with open("litclock_annotated_improved.csv") as f:
        r = csv.reader(f, dialect=CustomDialect)
        inserted = False
        for i, line in enumerate(r):
            if time.strptime(line[0], "%H:%M") > time_obj and not inserted:
                print(f"Inserting before {line}")
                content.append(
                    [
                        time.strftime("%H:%M", time_obj),
                        time_human,
                        quote,
                        source,
                        author,
                    ]
                )
                inserted = True
            else:
                content.append(line)
    with open("litclock_annotated_improved.csv.bak", "w") as f:
        w = csv.writer(f, dialect=CustomDialect)
        w.writerows(content)


def json_append(time_obj, time_human, source, author, quote):
    """Append to JSON.

    Appends to the JSON source file in the correct position based on time.

    Args:
        time_obj: Time in a time object.
        time_human: Human-readable time format as string. Eg: Midnight.
        source: The name of the literary work for the quote.
        author: The author of the literary work.
        quote: The text of the quote.
        csv_fmt: True if the output format is CSV.
        yaml_fmt: True if the output format is YAML.
        json_fmt: True if the output format is JSON.

    Returns:
        None

    Raises:
        InvalidTimeException: The time was format could not be parsed.
    """
    content = []
    with open("litclock.json") as f:
        content = json.load(f)
        for i, line in enumerate(content):
            if time.strptime(line["time"], "%H:%M") > time_obj:
                print(f"Inserting before {line}")
                content[i - 1 : i - 1] = [
                    {
                        "time": time.strftime("%H:%M", time_obj),
                        "time_name": time_human,
                        "source": source,
                        "author": author,
                        "quote": quote,
                    }
                ]
                break
    with open("litclock.json", "w") as f:
        json.dump(content, f, indent=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="InsertQuote",
        description="Add a quote to the correct position in the data",
    )
    parser.add_argument("--time", required=True, help="Time in 24h format as a string")
    parser.add_argument(
        "--time_human",
        required=True,
        help="Human-readable time format as string. Eg: Midnight.",
    )
    parser.add_argument(
        "--source",
        required=True,
        help="The name of the literary work for the quote.",
    )
    parser.add_argument("--author", required=True, help="The text of the quote.")

    # This is a special group to pick formats and the mutual exclusion makes
    # sure that one and only one is selected.
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--csv", action="store_true", help="True if the output format is CSV."
    )
    group.add_argument(
        "--yaml", action="store_true", help="True if the output format is YAML."
    )
    group.add_argument(
        "--json", action="store_true", help="True if the output format is JSON."
    )

    parser.add_argument("quote")
    args = parser.parse_args()
    main(
        time_arg=args.time,
        time_human=args.time_human,
        source=args.source,
        author=args.author,
        quote=args.quote,
        csv_fmt=args.csv,
        yaml_fmt=args.yaml,
        json_fmt=args.json,
    )
