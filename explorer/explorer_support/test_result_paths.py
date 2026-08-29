import tempfile
import unittest
import warnings
from pathlib import Path

from explorer_support.result_paths import resolve_result_files


class ResultPathsTest(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.app = self.root / "explorer"
        self.paper = self.app / "paper_results"
        self.pipeline = self.root / "pipeline" / "results"
        self.paper.mkdir(parents=True)
        for name in ("features.csv", "scenarios_features.yaml", "feature_explanations.yaml"):
            (self.paper / name).write_text("paper\n", encoding="utf-8")

    def tearDown(self):
        self.temporary_directory.cleanup()

    def write_pipeline_results(self):
        (self.pipeline / "features").mkdir(parents=True)
        (self.pipeline / "features" / "features.csv").write_text("pipeline\n", encoding="utf-8")
        (self.pipeline / "scenarios_features.yaml").write_text("pipeline\n", encoding="utf-8")
        (self.pipeline / "feature_explanations.yaml").write_text("pipeline\n", encoding="utf-8")

    def test_uses_paper_results_when_pipeline_results_do_not_exist(self):
        files = resolve_result_files(self.app, self.pipeline)
        self.assertEqual(files.source, "paper")
        self.assertEqual(files.features, self.paper.resolve() / "features.csv")

    def test_uses_pipeline_only_when_the_complete_set_exists(self):
        self.write_pipeline_results()
        files = resolve_result_files(self.app, self.pipeline)
        self.assertEqual(files.source, "pipeline")
        self.assertEqual(
            files.features,
            self.pipeline.resolve() / "features" / "features.csv",
        )

    def test_incomplete_pipeline_warns_and_uses_complete_paper_set(self):
        self.pipeline.mkdir(parents=True)
        (self.pipeline / "scenarios_features.yaml").write_text("pipeline\n", encoding="utf-8")
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            files = resolve_result_files(self.app, self.pipeline)
        self.assertEqual(files.source, "paper")
        self.assertIn("Pipeline results are incomplete", str(caught[0].message))

    def test_incomplete_paper_set_is_an_error(self):
        (self.paper / "features.csv").unlink()
        with self.assertRaises(FileNotFoundError):
            resolve_result_files(self.app, self.pipeline)


if __name__ == "__main__":
    unittest.main()
