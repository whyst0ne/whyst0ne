import json
import tempfile
import unittest
from pathlib import Path

from csv_to_json import convert_csv, main


class CsvToJsonTests(unittest.TestCase):
    def test_missing_fields_become_null_and_amount_is_numeric(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "in.csv"
            source.write_text("id,name,amount\n1,Ada,12.50\n2,,\n", encoding="utf-8")
            rows = convert_csv(source)
        self.assertEqual(rows[0]["amount"], 12.5)
        self.assertIsNone(rows[1]["name"])
        self.assertIsNone(rows[1]["amount"])

    def test_delimiter_is_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "in.csv"
            source.write_text("id;amount\n1;3.25\n", encoding="utf-8")
            self.assertEqual(convert_csv(source)[0]["amount"], 3.25)

    def test_output_file_is_valid_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "in.csv"
            output = Path(tmp) / "out.json"
            source.write_text("id,amount\n1,4\n", encoding="utf-8")
            self.assertEqual(main([str(source), "-o", str(output)]), 0)
            self.assertEqual(json.loads(output.read_text()), [{"id": "1", "amount": 4.0}])


if __name__ == "__main__":
    unittest.main()
