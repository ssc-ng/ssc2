"""Checks on site/build_data.py's reading of the mirror's ERRATA.md.

Standard library only, matching the rest of this repository's Python.
"""

import datetime as dt
import importlib.util
import unittest
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "build_data", Path(__file__).resolve().parent.parent / "site" / "build_data.py")
build_data = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(build_data)

ERRATA = """# Known bugs and errors

## Absent dates

| Start date | End date   | Reason |
|------------|------------|--------|
| 2021-12-22 | 2021-12-22 | Mirror workflow not automated |
| 2026-03-08 | 2026-03-10 | The mirror workflow failed. |
| 2026-10-21 | 2026-10-21 | BC website down for maintenance |

## Early dates

| 2017-08-10 | 2017-08-11 | not an absent range |
"""


class ParseAbsentDates(unittest.TestCase):
    def test_expands_ranges_and_single_days(self):
        d = dt.date.fromisoformat
        self.assertEqual(build_data.parse_absent_dates(ERRATA), {
            d("2021-12-22"), d("2026-03-08"), d("2026-03-09"),
            d("2026-03-10"), d("2026-10-21")})

    def test_ignores_rows_outside_absent_dates_section(self):
        self.assertEqual(build_data.parse_absent_dates(
            "## Early dates\n| 2017-08-10 | 2017-08-10 | x |\n"), set())


if __name__ == "__main__":
    unittest.main()
