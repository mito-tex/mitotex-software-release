import tempfile
import unittest
from pathlib import Path

from explorer_support.feature_explanations import (
    load_feature_explanations,
    update_feature_explanation,
)


SAMPLE = '''feature_one:
  filter: "LoG ($\\\\sigma=2$)"
  stats: IQR
  title: Original title
  technical: >
    Original technical text.
  image: >
    Original image text.
  biology: >
    Original biology text.
'''


class FeatureExplanationsTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.path = Path(self.directory.name) / "features.yaml"
        self.path.write_text(SAMPLE, encoding="utf-8")

    def tearDown(self):
        self.directory.cleanup()

    def test_updates_only_requested_values_and_preserves_scalar_styles(self):
        update_feature_explanation(
            self.path,
            "feature_one",
            {"title": "New title", "biology": "New biology."},
        )

        saved = self.path.read_text(encoding="utf-8")
        data = load_feature_explanations(self.path)
        self.assertEqual(data["feature_one"]["title"], "New title")
        self.assertEqual(data["feature_one"]["biology"], "New biology.\n")
        self.assertEqual(data["feature_one"]["technical"], "Original technical text.\n")
        self.assertIn('filter: "LoG ($\\\\sigma=2$)"', saved)
        self.assertIn("biology: >", saved)
        self.assertNotIn("biology: >-", saved)

    def test_rejects_empty_and_unknown_fields_without_writing(self):
        original = self.path.read_bytes()
        with self.assertRaises(ValueError):
            update_feature_explanation(self.path, "feature_one", {"title": "  "})
        with self.assertRaises(ValueError):
            update_feature_explanation(self.path, "feature_one", {"feature_id": "new"})
        self.assertEqual(self.path.read_bytes(), original)

if __name__ == "__main__":
    unittest.main()
