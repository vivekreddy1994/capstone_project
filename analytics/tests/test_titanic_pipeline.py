import json
import unittest

import pandas as pd

from analytics.src.titanic_pipeline import ROOT, clean, load_once, profile


class TestTitanicPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = load_once()
        cls.missing = profile(cls.raw)
        cls.cleaned = clean(cls.raw, cls.missing)

    def test_offline_fallback_and_cleaning(self):
        self.assertTrue((ROOT / "titanic.csv").exists())
        self.assertGreaterEqual(len(self.cleaned), 800)
        self.assertFalse(self.cleaned[["age", "embarked"]].isna().any().any())

    def test_eda_outputs(self):
        outputs = json.loads((ROOT / "artifacts" / "run_summary.json").read_text(encoding="utf-8"))["eda"]
        self.assertIn("age_outliers", outputs)
        self.assertIn("fare_outliers", outputs)
        self.assertEqual(set(["survived", "pclass", "age", "sibsp", "parch", "fare"]), set(self.cleaned[["survived", "pclass", "age", "sibsp", "parch", "fare"]].columns))
        self.assertTrue((ROOT / "artifacts" / "correlation_heatmap.png").exists())


if __name__ == "__main__":
    unittest.main()
