import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from databricks_labs import (
    PACKS,
    ROOT,
    import_path,
    iter_pack_files,
    should_skip_file,
    workspace_path,
)


class DatabricksLabsScriptTest(unittest.TestCase):
    def test_should_list_four_existing_lab_packs(self):
        self.assertEqual(len(PACKS), 4)
        for name in PACKS:
            self.assertTrue((ROOT / name).is_dir(), name)

    def test_should_build_workspace_path_under_user_folder(self):
        path = workspace_path("dev@example.com", "notebook-data-001-churn/README.md")
        self.assertEqual(
            path,
            "/Users/dev@example.com/ai-master-challenge/notebook-data-001-churn/README.md",
        )

    def test_should_strip_ipynb_suffix_from_import_path(self):
        local = Path("lab01_carga_csv.ipynb")
        dest = "/Users/dev@example.com/ai-master-challenge/lab01_carga_csv.ipynb"
        self.assertEqual(
            import_path(local, dest),
            "/Users/dev@example.com/ai-master-challenge/lab01_carga_csv",
        )

    def test_should_keep_non_notebook_import_path(self):
        local = Path("README.md")
        dest = "/Users/dev@example.com/ai-master-challenge/README.md"
        self.assertEqual(import_path(local, dest), dest)

    def test_should_skip_file_when_larger_than_limit(self):
        csv_path = ROOT / "notebook-marketing-004-social" / "dados" / "social_media_dataset.csv"
        self.assertTrue(csv_path.is_file())
        self.assertTrue(should_skip_file(csv_path, limit=9_000_000))
        self.assertFalse(should_skip_file(csv_path, limit=csv_path.stat().st_size + 1))

    def test_should_find_lab01_notebook_in_each_pack(self):
        for name in PACKS:
            files = [path.name for path in iter_pack_files(ROOT / name)]
            self.assertIn("lab01_carga_csv.ipynb", files, name)


if __name__ == "__main__":
    unittest.main()
