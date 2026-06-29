import unittest
from pathlib import Path

class TestInstitutionalDocs(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).parent.parent
        self.readme = self.root / "README.md"
        self.project = self.root / "PROJECT.md"
        self.roadmap = self.root / "ROADMAP.md"
        self.architecture = self.root / "FINAL_ARCHITECTURE.md"

    def test_version_consistency(self):
        version = "V3.3.0"
        for doc in [self.readme, self.project, self.roadmap, self.architecture]:
            content = doc.read_text(encoding="utf-8")
            self.assertIn(version, content, f"Version {version} missing in {doc.name}")

    def test_zero_tolerance_mention(self):
        term = "Zero-Tolerance"
        for doc in [self.readme, self.project, self.architecture]:
            content = doc.read_text(encoding="utf-8")
            self.assertIn(term, content, f"{term} missing in {doc.name}")

    def test_rust_kernel_mentions(self):
        kernels = ["aat_heavy", "aat_rust_core", "aat_rust"]
        content = self.readme.read_text(encoding="utf-8")
        for kernel in kernels:
            self.assertIn(kernel, content, f"Kernel {kernel} missing in README.md")

    def test_triple_dashboard_mentions(self):
        dashboards = ["Native Desktop", "Web Interface", "MT5 Terminal"]
        content = self.readme.read_text(encoding="utf-8")
        for dash in dashboards:
            self.assertIn(dash, content, f"Dashboard {dash} missing in README.md")

if __name__ == "__main__":
    unittest.main()
