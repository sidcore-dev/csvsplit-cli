import csv
import io
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory

from csvsplit_cli.cli import main


def write_csv(path: Path, header, rows) -> None:
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(header)
        writer.writerows(rows)


class TestCli(unittest.TestCase):
    def test_splits_and_preserves_header(self) -> None:
        with TemporaryDirectory() as tmp:
            src = Path(tmp) / "data.csv"
            write_csv(src, ["id", "name"], [[str(i), f"row{i}"] for i in range(5)])

            out = io.StringIO()
            with redirect_stdout(out):
                code = main([str(src), "--rows", "2"])
            self.assertEqual(code, 0)

            part1 = Path(tmp) / "data_part001.csv"
            part3 = Path(tmp) / "data_part003.csv"
            self.assertTrue(part1.exists())
            self.assertTrue(part3.exists())

            with open(part1, newline="") as fh:
                rows = list(csv.reader(fh))
            self.assertEqual(rows[0], ["id", "name"])
            self.assertEqual(len(rows), 3)  # header + 2 data rows

            with open(part3, newline="") as fh:
                rows = list(csv.reader(fh))
            self.assertEqual(rows[0], ["id", "name"])
            self.assertEqual(len(rows), 2)  # header + 1 leftover data row

    def test_out_dir_option(self) -> None:
        with TemporaryDirectory() as tmp:
            src = Path(tmp) / "data.csv"
            write_csv(src, ["id"], [[str(i)] for i in range(3)])
            out_dir = Path(tmp) / "parts"

            out = io.StringIO()
            with redirect_stdout(out):
                code = main([str(src), "--rows", "1", "--out-dir", str(out_dir)])
            self.assertEqual(code, 0)
            self.assertTrue((out_dir / "data_part001.csv").exists())
            self.assertTrue((out_dir / "data_part003.csv").exists())

    def test_header_only_writes_nothing(self) -> None:
        with TemporaryDirectory() as tmp:
            src = Path(tmp) / "empty.csv"
            write_csv(src, ["id", "name"], [])

            out = io.StringIO()
            with redirect_stdout(out):
                code = main([str(src)])
            self.assertEqual(code, 0)
            self.assertIn("nothing written", out.getvalue())
            self.assertFalse((Path(tmp) / "empty_part001.csv").exists())

    def test_missing_file_errors(self) -> None:
        err = io.StringIO()
        with redirect_stderr(err):
            code = main(["/no/such/file.csv"])
        self.assertEqual(code, 2)
        self.assertIn("error", err.getvalue())

    def test_zero_rows_errors(self) -> None:
        with TemporaryDirectory() as tmp:
            src = Path(tmp) / "data.csv"
            write_csv(src, ["id"], [["1"]])
            err = io.StringIO()
            with redirect_stderr(err):
                code = main([str(src), "--rows", "0"])
            self.assertEqual(code, 2)
            self.assertIn("must be positive", err.getvalue())

    def test_default_rows_is_1000(self) -> None:
        with TemporaryDirectory() as tmp:
            src = Path(tmp) / "small.csv"
            write_csv(src, ["id"], [[str(i)] for i in range(10)])
            out = io.StringIO()
            with redirect_stdout(out):
                code = main([str(src)])
            self.assertEqual(code, 0)
            self.assertTrue((Path(tmp) / "small_part001.csv").exists())
            self.assertFalse((Path(tmp) / "small_part002.csv").exists())


if __name__ == "__main__":
    unittest.main()
