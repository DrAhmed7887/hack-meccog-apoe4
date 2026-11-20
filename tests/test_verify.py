"""Tests for scripts/verify.py strictness. Standard library only. NOT RUN when written (21 Nov 2026)."""
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import verify  # noqa: E402


class VerifyBase(unittest.TestCase):
    def setUp(self):
        verify.FAILS.clear()
        verify.WARNS.clear()
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def run_quiet(self, fn, *args, **kw):
        with redirect_stdout(io.StringIO()):
            return fn(*args, **kw)

    def write_json(self, rel, obj):
        p = self.dir / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(obj), encoding="utf-8")


class EmptyJson(VerifyBase):
    def test_empty_freeze_object_fails(self):
        self.write_json("FREEZE.json", {})
        self.run_quiet(verify.check_freeze, self.dir, True)
        self.assertTrue(verify.FAILS)

    def test_empty_files_map_fails(self):
        self.write_json("FREEZE.json", {"files": {}})
        self.run_quiet(verify.check_freeze, self.dir, True)
        self.assertTrue(verify.FAILS)

    def test_empty_report_fails(self):
        self.write_json("dd/report.json", {})
        self.run_quiet(verify.check_report, self.dir)
        self.assertTrue(verify.FAILS)

    def test_empty_extracted_fails(self):
        self.write_json("extracted.json", {})
        self.run_quiet(verify.check_extracted, self.dir)
        self.assertTrue(verify.FAILS)


class Workbook(VerifyBase):
    def test_missing_xlsx_fails_when_strict_warns_when_not(self):
        self.run_quiet(verify.check_workbook, self.dir, (1, 1), True)
        self.assertEqual(len(verify.FAILS), 1)
        verify.FAILS.clear()
        self.run_quiet(verify.check_workbook, self.dir, (1, 1), False)
        self.assertFalse(verify.FAILS)
        self.assertEqual(len(verify.WARNS), 1)

    def test_count_excludes_papers_without_findings(self):
        # to_template.build_rows skips papers with no findings, so verify must count the same way
        finding = {"directness_class": 1, "description": "d", "quote": "q", "direction": "supports"}
        self.write_json("extracted.json", {"papers": [
            {"pmid": "1", "findings": [finding]}, {"pmid": "2", "findings": []}]})
        counts = self.run_quiet(verify.check_extracted, self.dir)
        self.assertEqual(counts, (1, 1))


class Claims(VerifyBase):
    def test_out_path_does_not_fall_back_to_local_out(self):
        fake_root = self.dir / "root"
        (fake_root / "out" / "dd").mkdir(parents=True)
        (fake_root / "out" / "dd" / "report.json").write_text("{}", encoding="utf-8")
        data = self.dir / "data"  # exists but lacks dd/report.json
        data.mkdir()
        claims = self.dir / "CLAIMS.md"
        claims.write_text("| claim | src | `out/dd/report.json` | x |\n", encoding="utf-8")
        with mock.patch.object(verify, "ROOT", fake_root):
            self.run_quiet(verify.check_claims, data, claims)
        self.assertTrue(any("out/dd/report.json" in f for f in verify.FAILS))

    def test_out_path_resolves_in_data_dir(self):
        data = self.dir / "data"
        (data / "dd").mkdir(parents=True)
        (data / "dd" / "report.json").write_text("{}", encoding="utf-8")
        claims = self.dir / "CLAIMS.md"
        claims.write_text("| claim | src | `out/dd/report.json` | x |\n", encoding="utf-8")
        with mock.patch.object(verify, "ROOT", self.dir / "root"):
            self.run_quiet(verify.check_claims, data, claims)
        self.assertFalse(verify.FAILS)


if __name__ == "__main__":
    unittest.main()
