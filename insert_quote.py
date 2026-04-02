#!/usr/bin/env python3
import argparse
import time
import yaml


def main(time_arg, time_human, source, author, quote):
    time_obj = time.strptime(time_arg, "%H:%M")
    yaml_insert(time_obj, time_human, source, author, quote)


def yaml_insert(time_obj, time_human, source, author, quote, filepath="litclock.yaml"):
    """Insert a quote into a litclock YAML file at the correct chronological position."""
    with open(filepath) as f:
        content = yaml.safe_load(f)

    entry = {
        "time": time.strftime("%H:%M", time_obj),
        "time_name": time_human,
        "source": source,
        "author": author,
        "quote": quote,
    }

    for i, line in enumerate(content):
        if time.strptime(line["time"], "%H:%M") > time_obj:
            print(f"Inserting before {line}")
            content.insert(i, entry)
            break
    else:
        print("Inserting at end")
        content.append(entry)

    with open(filepath, "w") as f:
        f.write(yaml.dump(content, allow_unicode=True, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="InsertQuote",
        description="Add a quote to the correct position in litclock.yaml",
    )
    parser.add_argument("--time", required=True, help="Time in 24h format, e.g. 14:35")
    parser.add_argument(
        "--time_human",
        required=True,
        help="Human-readable time, e.g. 'twenty-five to three'",
    )
    parser.add_argument("--source", required=True, help="Title of the literary work")
    parser.add_argument("--author", required=True, help="Author of the literary work")
    parser.add_argument("quote", help="The quote text")
    args = parser.parse_args()
    main(
        time_arg=args.time,
        time_human=args.time_human,
        source=args.source,
        author=args.author,
        quote=args.quote,
    )
