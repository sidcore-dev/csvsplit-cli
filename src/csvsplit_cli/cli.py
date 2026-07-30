"""Command-line entry point for csvsplit-cli."""
from __future__ import annotations

import argparse
import csv
import os
import sys
from typing import List, Optional

from .core import part_filename, split_rows


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="csvsplit-cli",
        description="Split a large CSV file into smaller files by row count, "
        "preserving the header row in every output file.",
    )
    parser.add_argument("file", help="Path to the CSV file to split")
    parser.add_argument(
        "--rows", type=int, default=1000, help="Data rows per output file (default: 1000)"
    )
    parser.add_argument(
        "--out-dir",
        default=None,
        help="Directory to write output files to (default: same directory as input)",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.rows <= 0:
        print("csvsplit-cli: error: --rows must be positive", file=sys.stderr)
        return 2

    try:
        with open(args.file, "r", encoding="utf-8", newline="") as fh:
            rows = list(csv.reader(fh))
    except OSError as exc:
        print(f"csvsplit-cli: error: {exc}", file=sys.stderr)
        return 2

    out_dir = args.out_dir or os.path.dirname(os.path.abspath(args.file))
    if args.out_dir:
        try:
            os.makedirs(out_dir, exist_ok=True)
        except OSError as exc:
            print(f"csvsplit-cli: error: {exc}", file=sys.stderr)
            return 2

    base_name = os.path.basename(args.file)
    written = 0
    for part_number, chunk in enumerate(split_rows(rows, args.rows), start=1):
        out_name = part_filename(base_name, part_number)
        out_path = os.path.join(out_dir, out_name)
        try:
            with open(out_path, "w", encoding="utf-8", newline="") as out_fh:
                csv.writer(out_fh).writerows(chunk)
        except OSError as exc:
            print(f"csvsplit-cli: error: {exc}", file=sys.stderr)
            return 2
        print(f"csvsplit-cli: wrote {out_path} ({len(chunk) - 1} data row(s))")
        written += 1

    if written == 0:
        print("csvsplit-cli: no data rows found — nothing written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
