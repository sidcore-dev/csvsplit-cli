"""Core CSV-splitting logic — pure functions, no file I/O."""
from __future__ import annotations

from typing import Iterable, Iterator, List, Sequence


def split_rows(rows: Iterable[Sequence[str]], rows_per_file: int) -> Iterator[List[Sequence[str]]]:
    """Split `rows` (an iterable of CSV rows, header first) into chunks.

    Each yielded chunk is a list starting with the header row, followed by
    up to `rows_per_file` data rows — so every output chunk is a complete,
    independently-readable CSV. If `rows` contains only a header (or is
    empty), nothing is yielded.

    Raises ValueError if `rows_per_file` is not positive.
    """
    if rows_per_file <= 0:
        raise ValueError("rows_per_file must be positive")

    it = iter(rows)
    try:
        header = next(it)
    except StopIteration:
        return

    chunk: List[Sequence[str]] = []
    for row in it:
        chunk.append(row)
        if len(chunk) == rows_per_file:
            yield [header] + chunk
            chunk = []
    if chunk:
        yield [header] + chunk


def part_filename(original: str, part_number: int) -> str:
    """Build the output filename for a given 1-based part number.

    `access.csv`, part 1 -> `access_part001.csv`
    `data`, part 12 -> `data_part012.csv` (no extension: `.csv` is assumed)
    """
    if part_number < 1:
        raise ValueError("part_number must be >= 1")

    if "." in original:
        stem, _, ext = original.rpartition(".")
        return f"{stem}_part{part_number:03d}.{ext}"
    return f"{original}_part{part_number:03d}.csv"
