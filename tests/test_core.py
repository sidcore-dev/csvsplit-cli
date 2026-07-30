import unittest

from csvsplit_cli.core import part_filename, split_rows


class TestSplitRows(unittest.TestCase):
    def test_splits_into_expected_chunks(self) -> None:
        rows = [["id", "name"], ["1", "a"], ["2", "b"], ["3", "c"], ["4", "d"], ["5", "e"]]
        chunks = list(split_rows(rows, 2))
        self.assertEqual(len(chunks), 3)
        self.assertEqual(chunks[0], [["id", "name"], ["1", "a"], ["2", "b"]])
        self.assertEqual(chunks[1], [["id", "name"], ["3", "c"], ["4", "d"]])
        self.assertEqual(chunks[2], [["id", "name"], ["5", "e"]])

    def test_exact_multiple_has_no_short_last_chunk(self) -> None:
        rows = [["h"], ["1"], ["2"], ["3"], ["4"]]
        chunks = list(split_rows(rows, 2))
        self.assertEqual(len(chunks), 2)
        self.assertEqual([len(c) - 1 for c in chunks], [2, 2])

    def test_header_only_yields_nothing(self) -> None:
        rows = [["id", "name"]]
        self.assertEqual(list(split_rows(rows, 10)), [])

    def test_empty_input_yields_nothing(self) -> None:
        self.assertEqual(list(split_rows([], 10)), [])

    def test_rows_per_file_larger_than_data_yields_one_chunk(self) -> None:
        rows = [["h"], ["1"], ["2"]]
        chunks = list(split_rows(rows, 100))
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0], [["h"], ["1"], ["2"]])

    def test_zero_rows_per_file_raises(self) -> None:
        with self.assertRaises(ValueError):
            list(split_rows([["h"], ["1"]], 0))

    def test_negative_rows_per_file_raises(self) -> None:
        with self.assertRaises(ValueError):
            list(split_rows([["h"], ["1"]], -5))


class TestPartFilename(unittest.TestCase):
    def test_basic_extension(self) -> None:
        self.assertEqual(part_filename("orders.csv", 1), "orders_part001.csv")

    def test_zero_padded_to_three_digits(self) -> None:
        self.assertEqual(part_filename("orders.csv", 12), "orders_part012.csv")
        self.assertEqual(part_filename("orders.csv", 123), "orders_part123.csv")

    def test_no_extension_assumes_csv(self) -> None:
        self.assertEqual(part_filename("data", 1), "data_part001.csv")

    def test_part_number_below_one_raises(self) -> None:
        with self.assertRaises(ValueError):
            part_filename("orders.csv", 0)


if __name__ == "__main__":
    unittest.main()
