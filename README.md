# csvsplit-cli

A small, dependency-free command-line tool that splits a large CSV file
into multiple smaller files by row count, keeping the header row intact
in every piece.

## Why

Splitting a CSV with `split` or `head`/`tail` loses the header on every
part after the first, which breaks anything that expects a proper CSV
(pandas, Excel, another script). `csvsplit-cli` re-writes the header into
every output file, so each part is independently valid on its own.

## Install

```bash
pip install .
```

This installs a `csvsplit-cli` command on your PATH.

## Usage

```bash
$ csvsplit-cli orders.csv --rows 500
csvsplit-cli: wrote orders_part001.csv (500 data row(s))
csvsplit-cli: wrote orders_part002.csv (500 data row(s))
csvsplit-cli: wrote orders_part003.csv (241 data row(s))
```

Write parts to a different directory:

```bash
csvsplit-cli orders.csv --rows 500 --out-dir ./parts
```

### Options

| Flag         | Description                                                    |
|--------------|-------------------------------------------------------------------|
| `file`       | Path to the CSV file to split                                     |
| `--rows`     | Data rows per output file, header not counted (default: 1000)     |
| `--out-dir`  | Directory to write output files to (default: same dir as input)   |

Output files are named `<original>_partNNN.csv` — e.g. `orders.csv`
becomes `orders_part001.csv`, `orders_part002.csv`, and so on, zero-padded
to three digits.

### Behavior notes

- The first row of the input is always treated as the header and is
  repeated at the top of every output file.
- If the input has no data rows (header only, or completely empty),
  no output files are written.
- The last output file may have fewer than `--rows` data rows if the
  total doesn't divide evenly.

### Exit codes

- `0` — completed successfully (including the case of nothing to split)
- `2` — the input file couldn't be read, `--rows` wasn't positive, or an
  output file couldn't be written

## Development

```bash
pip install -e .
python -m unittest discover -s tests -v
```

## License

All rights reserved. This code is public for viewing and reference only —
no license is granted to use, copy, modify, or redistribute it. See
[LICENSE](LICENSE) for details.
