"""
Tests for PROJECT.md — V1.9.0 (Pragmatic Realignment)

These tests validate the structural and content changes introduced in the V1.9.0
revision of PROJECT.md.
"""

import re
import unittest
from pathlib import Path

PROJECT_MD = Path(__file__).parent.parent / "PROJECT.md"


def _read_md() -> str:
    return PROJECT_MD.read_text(encoding="utf-8")


class TestVersionBump(unittest.TestCase):
    """PROJECT.md must be at Version 1.9.0."""

    def setUp(self):
        self.content = _read_md()

    def test_title_contains_v1_9_0(self):
        self.assertIn("Version**: 1.9.0", self.content)

    def test_operational_mode_is_v1_9_0(self):
        self.assertIn("Version**: 1.9.0", self.content)


class TestInstitutionalRealityAuditSection(unittest.TestCase):
    """Validates the 'Institutional Reality Audit' appendice."""

    def setUp(self):
        self.content = _read_md()
        match = re.search(
            r"## 📜 13\. Appendices.*",
            self.content,
            re.DOTALL,
        )
        self.audit_block = match.group(0) if match else ""

    def test_section_heading_exists(self):
        self.assertIn("13. Appendices", self.content)

    def test_postgresql_mandatory_governance_store(self):
        self.assertIn("PostgreSQL mandatory for governance", self.audit_block)

    def test_sqlite_not_for_audit(self):
        self.assertIn("SQLite is not for Audit", self.audit_block)


class TestRiskAssessmentTable(unittest.TestCase):
    """Validates the risk assessment table exists and is populated."""

    def setUp(self):
        self.content = _read_md()
        match = re.search(
            r"## ⚠️ 12\. Risk Assessment.*?(?=\n## |\Z)",
            self.content,
            re.DOTALL,
        )
        self.risk_block = match.group(0) if match else ""

    def test_risk_section_exists(self):
        self.assertIn("12. Risk Assessment", self.content)

    def test_three_data_rows_in_table(self):
        data_rows = [
            ln for ln in self.risk_block.splitlines()
            if re.match(r"\|\s+\*\*", ln)
        ]
        self.assertEqual(len(data_rows), 3)

    def test_team_burnout_mitigation(self):
        self.assertIn("Team Burnout", self.risk_block)
        self.assertIn("8-person redundancy", self.risk_block)


class TestSectionStructure(unittest.TestCase):
    """Verify top-level sections."""

    def setUp(self):
        self.content = _read_md()
        self.section_headings = re.findall(r"^## .+$", self.content, re.MULTILINE)

    def test_sections_present(self):
        # We check for at least the major ones
        self.assertTrue(any("1." in h and "Project Identity" in h for h in self.section_headings))
        self.assertTrue(any("2." in h and "System Overview" in h for h in self.section_headings))
        self.assertTrue(any("6." in h and "Risk Management" in h for h in self.section_headings))
        self.assertTrue(any("11." in h and "Strategic Roadmap" in h for h in self.section_headings))
        self.assertTrue(any("12." in h and "Risk Assessment" in h for h in self.section_headings))
        self.assertTrue(any("13." in h and "Appendices" in h for h in self.section_headings))


class TestNoDuplicateSections(unittest.TestCase):
    """Ensure no duplicate headings."""

    def setUp(self):
        self.content = _read_md()

    def test_no_duplicate_section_4(self):
        matches = re.findall(r"## 🏗️ 4\. System Architecture", self.content)
        self.assertEqual(len(matches), 1)

    def test_no_duplicate_section_6(self):
        matches = re.findall(r"## 🛡️ 6\. Risk Management", self.content)
        self.assertEqual(len(matches), 1)


class TestSystemOverviewSection(unittest.TestCase):
    """Validates System Overview content."""

    def setUp(self):
        self.content = _read_md()
        match = re.search(
            r"## 🛠️ 2\. System Overview.*?(?=\n## |\Z)",
            self.content,
            re.DOTALL,
        )
        self.overview_block = match.group(0) if match else ""

    def test_sovereign_ingress_aes(self):
        self.assertIn("AES-256-GCM Secure Gateway", self.overview_block)

    def test_mt5_phase1_fix_phase2_migration(self):
        self.assertIn("MT5 Phase 1", self.overview_block)
        self.assertIn("FIX Protocol Priority Phase 2", self.overview_block)

    def test_persistence_layer_components(self):
        self.assertIn("PostgreSQL", self.overview_block)
        self.assertIn("QuestDB", self.overview_block)
        self.assertIn("Redis Cluster", self.overview_block)

    def test_event_bus_protobuf(self):
        self.assertIn("Protocol Buffers (Protobuf)", self.overview_block)


class TestRiskStackSection(unittest.TestCase):
    """Validates the Risk Stack."""

    def setUp(self):
        self.content = _read_md()
        match = re.search(
            r"### 🛡️ The 7-Layer Risk Stack.*?(?=\n## |\Z)",
            self.content,
            re.DOTALL,
        )
        self.stack_block = match.group(0) if match else ""

    def test_monte_carlo_validation_present(self):
        self.assertIn("Monte Carlo simulation", self.stack_block)

    def test_conflict_resolution_present(self):
        self.assertIn("Higher precedence always wins", self.stack_block)


class TestTeamSection(unittest.TestCase):
    """Validates the Team section."""

    def setUp(self):
        self.content = _read_md()
        match = re.search(
            r"## 👥 10\. Minimum Viable Team.*?(?=\n## |\Z)",
            self.content,
            re.DOTALL,
        )
        self.team_block = match.group(0) if match else ""

    def test_team_section_exists(self):
        self.assertIn("Minimum Viable Team (8 People)", self.content)

    def test_backend_kernel_engineers_title(self):
        self.assertIn("Backend/Kernel Engineers", self.team_block)

    def test_devops_sre_title(self):
        self.assertIn("DevOps/SRE", self.team_block)

    def test_qa_sdet_title(self):
        self.assertIn("QA/SDET", self.team_block)


class TestCoreValuesSection(unittest.TestCase):
    """Validates Core Values."""

    def setUp(self):
        self.content = _read_md()
        match = re.search(
            r"### 💎 Core Values.*?(?=\n## |\Z)",
            self.content,
            re.DOTALL,
        )
        self.values_block = match.group(0) if match else ""

    def test_core_values_section_exists(self):
        self.assertIn("Core Values (V7.1.0)", self.content)

    def test_sovereignty_value_present(self):
        self.assertIn("Sovereignty", self.values_block)

    def test_transparency_value_present(self):
        self.assertIn("Transparency", self.values_block)

    def test_performance_value_python_mt5(self):
        self.assertIn("Python + MT5", self.values_block)


if __name__ == "__main__":
    unittest.main()
