#!/usr/bin/env python3
import argparse
import time
import yaml


def main(time_arg, time_human, source, author, quote, sfw):
    time_obj = time.strptime(time_arg, "%H:%M")
    yaml_insert(time_obj, time_human, source, author, quote, sfw=sfw)


def yaml_insert(time_obj, time_human, source, author, quote, sfw="yes", filepath="litclock.yaml"):
    """Insert a quote into a litclock YAML file at the correct chronological position."""
    with open(filepath, encoding='utf-8') as f:
        content = yaml.safe_load(f)

    entry = {
        "time": time.strftime("%H:%M", time_obj),
        "time_name": time_human,
        "source": source,
        "author": author,
        "quote": quote,
        "sfw": sfw,
    }

    for i, line in enumerate(content):
        if time.strptime(line["time"], "%H:%M") > time_obj:
            print(f"Inserting before {line}")
            content.insert(i, entry)
            break
    else:
        print("Inserting at end")
        content.append(entry)

    with open(filepath, "w", encoding='utf-8') as f:
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
    parser.add_argument(
        "--nsfw",
        action="store_true",
        help="Mark this quote as not safe for work (default: SFW)",
    )
    args = parser.parse_args()
    main(
        time_arg=args.time,
        time_human=args.time_human,
        source=args.source,
        author=args.author,
        quote=args.quote,
        sfw="no" if args.nsfw else "yes",
    )
