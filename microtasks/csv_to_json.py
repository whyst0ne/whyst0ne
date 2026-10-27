#!/usr/bin/env python3
"""Convert a CSV file to a JSON array with safe missing-field handling."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Iterable


def _reader(path: Path, delimiter: str | None) -> csv.DictReader:
    handle = path.open("r", encoding="utf-8", newline="")
    sample = handle.read(4096)
    handle.seek(0)
    chosen = delimiter
    if chosen is None:
        try:
            chosen = csv.Sniffer().sniff(sample, delimiters=",;\t|").delimiter
        except csv.Error:
            chosen = ","
    return csv.DictReader(handle, delimiter=chosen)


def _amount(value: str | None) -> float | None:
    if value is None or not value.strip():
        return None
    try:
        return float(Decimal(value.strip()))
    except (InvalidOperation, ValueError):
        return None


def convert_csv(
    input_path: Path,
    amount_field: str = "amount",
    delimiter: str | None = None,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    reader = _reader(input_path, delimiter)
    for raw in reader:
        row: dict[str, Any] = {
            key: (value if value not in (None, "") else None)
            for key, value in raw.items()
            if key is not None
        }
        if amount_field in row:
            row[amount_field] = _amount(raw.get(amount_field))
        rows.append(row)
    return rows


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="CSV input path")
    parser.add_argument("-o", "--output", type=Path, help="JSON output path")
    parser.add_argument("--amount-field", default="amount")
    parser.add_argument("--delimiter", help="CSV delimiter; auto-detected by default")
    args = parser.parse_args(argv)

    try:
        rows = convert_csv(args.input, args.amount_field, args.delimiter)
    except (OSError, csv.Error) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    payload = json.dumps(rows, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)
    print(f"rows: {len(rows)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
