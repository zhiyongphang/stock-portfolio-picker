#!/usr/bin/env python3
import argparse
import json
import sys

from src.brief import build_brief
from src.report import render_text


def main():
    parser = argparse.ArgumentParser(description="Personal stock portfolio tracker & fund manager")
    parser.add_argument("command", choices=["brief", "json"], help="brief: text summary, json: raw data dump")
    args = parser.parse_args()

    brief = build_brief()

    if args.command == "json":
        print(json.dumps(brief, indent=2, default=str))
    else:
        print(render_text(brief))


if __name__ == "__main__":
    sys.exit(main())
