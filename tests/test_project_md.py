"""
Tests for PROJECT.md — V1.5 (Institutional Reality Audit)

These tests validate the structural and content changes introduced in the V1.5
revision of PROJECT.md. They are intentionally scoped to only the changes
present in this PR (V1.4 → V1.5).
"""

import re
import unittest
from pathlib import Path

PROJECT_MD = Path(__file__).parent.parent / "PROJECT.md"


def _read_md() -> str:
    return PROJECT_MD.read_text(encoding="utf-8")


class TestVersionBump(unittest.TestCase):
    """Version references must consistently reflect V1.5, not V1.4 or V1.3."""

    def setUp(self):
        self.content = _read_md()

    def test_title_contains_v1_5(self):
        self.assertIn("V1.5", self.content.splitlines()[0])

    def test_operational_mode_is_v1_5(self):
        self.assertIn("Phoenix V1.5 (Institutional Reality Audit)", self.content)

    def test_no_stale_v1_4_operational_mode(self):
        """V1.4 operational mode line must not appear."""
        self.assertNotIn("Phoenix V1.4 (Institutional Hardening)", self.content)

    def test_no_stale_v1_3_operational_mode(self):
        """V1.3 operational mode line must not appear."""
        self.assertNotIn("Phoenix V1.3 (Cognitive Logic Integration)", self.content)

    def test_conspiracy_of_complexity_references_v1_5(self):
        """The 'Conspiracy of Complexity' enforcement line must cite V1.5."""
        self.assertIn(
            'combat the **"Conspiracy of Complexity"** and false certainty, V1.5 enforces',
            self.content,
        )

    def test_kill_switch_section_references_v1_5(self):
        """Kill Switch Hierarchy heading must reference V1.5."""
        self.assertIn("Kill Switch Hierarchy (Simplified V1.5)", self.content)

    def test_critical_note_references_v1_5(self):
        """Critical note in the status section must reference V1.5."""
        self.assertIn(
            "CRITICAL NOTE:** V1.5 (based on the V7.1.0 Rebuilt Sovereign)", self.content
        )

    def test_system_overview_section_references_v1_5(self):
        """New System Overview subsection must reference V1.5."""
        self.assertIn("System Overview (V1.5 Refinement)", self.content)


class TestInstitutionalRealityAuditSection(unittest.TestCase):
    """
    New section 'Institutional Reality Audit (Integration V1.5)' must be present
    and contain exactly 5 numbered admissions introduced in this PR.
    """

    def setUp(self):
        self.content = _read_md()

    def test_section_heading_exists(self):
        self.assertIn("Institutional Reality Audit (Integration V1.5)", self.content)

    def test_mt5_retail_trap_item(self):
        self.assertIn("MT5 is a Retail Trap", self.content)

    def test_sqlite_not_for_audit_item(self):
        self.assertIn("SQLite is not for Audit", self.content)

    def test_custom_event_buses_deadlock_item(self):
        self.assertIn("Custom Event Buses Deadlock", self.content)

    def test_ml_frankenstein_dead_item(self):
        self.assertIn("The ML Frankenstein is Dead", self.content)

    def test_compliance_not_addon_item(self):
        self.assertIn("Compliance is not an Add-on", self.content)

    def test_exactly_five_audit_items(self):
        """All five numbered items must be present in the section."""
        section_match = re.search(
            r"### 🧐 Institutional Reality Audit.*?(?=\n### |\n## |\Z)",
            self.content,
            re.DOTALL,
        )
        self.assertIsNotNone(section_match, "Institutional Reality Audit section missing")
        section_text = section_match.group(0)
        numbered_items = re.findall(r"^\d+\.\s+", section_text, re.MULTILINE)
        self.assertEqual(len(numbered_items), 5)

    def test_bus_py_deprecated(self):
        self.assertIn("bus.py` is deprecated", self.content)

    def test_postgresql_mandatory_governance_store(self):
        self.assertIn("PostgreSQL** is now the mandatory governance store", self.content)

    def test_finbert_faiss_rl_removed(self):
        self.assertIn("Removed FinBERT/FAISS/RL bloat", self.content)

    def test_mifid_iii_in_audit_section(self):
        self.assertIn("MiFID III", self.content)

    def test_fix_gateway_mentioned_for_phase_2(self):
        self.assertIn("FIX Gateway** for true institutional liquidity", self.content)


class TestPerformanceMandatesTable(unittest.TestCase):
    """
    Performance Mandates table was restructured in V1.5.
    Columns changed to: Metric | Phase 1 (MVP) | Phase 2 (Stretch) | Priority
    A new 'Execution Cost' row was also added.
    """

    def setUp(self):
        self.content = _read_md()
        # Extract the Performance Mandates table block
        # Use \n\n--- to only match the horizontal rule divider, not | :--- | table rows
        match = re.search(
            r"### 📊 Performance Mandates.*?(?=\n### |\n\n---|\Z)",
            self.content,
            re.DOTALL,
        )
        self.table_block = match.group(0) if match else ""

    def test_performance_mandates_section_exists(self):
        self.assertIn("Performance Mandates (Realistic & Phased)", self.content)

    def test_column_phase1_mvp(self):
        self.assertIn("Phase 1 (MVP)", self.table_block)

    def test_column_phase2_stretch(self):
        self.assertIn("Phase 2 (Stretch)", self.table_block)

    def test_column_priority(self):
        self.assertIn("Priority", self.table_block)

    def test_old_column_target_absent(self):
        """Old 'Target' column header should not appear in the table."""
        # Match only inside the table header row to avoid false positives
        header_line = next(
            (ln for ln in self.table_block.splitlines() if "Metric" in ln), ""
        )
        self.assertNotIn("| Target |", header_line)

    def test_old_column_reality_check_absent(self):
        header_line = next(
            (ln for ln in self.table_block.splitlines() if "Metric" in ln), ""
        )
        self.assertNotIn("Reality Check", header_line)

    def test_execution_cost_row_present(self):
        self.assertIn("Execution Cost", self.table_block)

    def test_six_data_rows_in_table(self):
        """Table should have 6 data rows: Sharpe, Sortino, MAR, Max DD, Risk of Ruin, Execution Cost."""
        # Data rows start with | **...
        data_rows = [
            ln for ln in self.table_block.splitlines()
            if re.match(r"\|\s+\*\*", ln)
        ]
        self.assertEqual(len(data_rows), 6)

    def test_sharpe_phase1_target(self):
        self.assertIn("> 1.0", self.table_block)

    def test_max_drawdown_absolute_priority(self):
        dd_line = next(
            (ln for ln in self.table_block.splitlines() if "Max Drawdown" in ln), ""
        )
        self.assertIn("ABSOLUTE", dd_line)

    def test_risk_of_ruin_absolute_priority(self):
        rr_line = next(
            (ln for ln in self.table_block.splitlines() if "Risk of Ruin" in ln), ""
        )
        self.assertIn("ABSOLUTE", rr_line)

    def test_execution_cost_critical_priority(self):
        ec_line = next(
            (ln for ln in self.table_block.splitlines() if "Execution Cost" in ln), ""
        )
        self.assertIn("CRITICAL", ec_line)


class TestKillSwitchHierarchy(unittest.TestCase):
    """
    Kill Switch section was restructured in V1.5 from DD/broker-health triggers
    to a numbered 4-level hierarchy with new scope names.
    """

    def setUp(self):
        self.content = _read_md()
        match = re.search(
            r"### 🛑 Kill Switch Hierarchy.*?(?=\n### |\n\n---|\Z)",
            self.content,
            re.DOTALL,
        )
        self.ks_block = match.group(0) if match else ""

    def test_kill_switch_section_exists(self):
        self.assertIn("Kill Switch Hierarchy (Simplified V1.5)", self.content)

    def test_level_1_strategy_scope(self):
        self.assertIn("Level 1 (Strategy)", self.ks_block)

    def test_level_2_symbol_scope(self):
        self.assertIn("Level 2 (Symbol)", self.ks_block)

    def test_level_3_global_scope(self):
        self.assertIn("Level 3 (Global)", self.ks_block)

    def test_level_4_infrastructure_scope(self):
        self.assertIn("Level 4 (Infrastructure)", self.ks_block)

    def test_exactly_four_numbered_levels(self):
        numbered = re.findall(r"^\d+\.\s+\*\*Level", self.ks_block, re.MULTILINE)
        self.assertEqual(len(numbered), 4)

    def test_level_1_trigger_description(self):
        self.assertIn("volatility or drawdown breach", self.ks_block)

    def test_level_2_trigger_description(self):
        self.assertIn("extreme spread or data gaps", self.ks_block)

    def test_level_3_trigger_description(self):
        self.assertIn("Flatten all positions and disable entry", self.ks_block)

    def test_level_4_trigger_description(self):
        self.assertIn("heartbeat failure or audit corruption", self.ks_block)

    def test_old_soft_halt_label_absent(self):
        self.assertNotIn("Soft Halt", self.ks_block)

    def test_old_hard_halt_label_absent(self):
        self.assertNotIn("Hard Halt", self.ks_block)

    def test_old_emergency_liquidation_label_absent(self):
        self.assertNotIn("Emergency Liquidation", self.ks_block)


class TestStrategicRoadmap(unittest.TestCase):
    """
    Phase roadmap was updated in V1.5: phases renamed and items use checkbox format.
    """

    def setUp(self):
        self.content = _read_md()
        # Use \n## to avoid matching ### subheadings as a ## boundary
        match = re.search(
            r"## 🗺️ 11\. Strategic Roadmap.*?(?=\n## |\Z)",
            self.content,
            re.DOTALL,
        )
        self.roadmap_block = match.group(0) if match else ""

    def test_roadmap_section_exists(self):
        self.assertIn("Strategic Roadmap & Phase Progression", self.content)

    def test_phase_1_name(self):
        self.assertIn("Phase 1: MVP & Logic Proof", self.roadmap_block)

    def test_phase_2_name(self):
        self.assertIn("Phase 2: FIX & Sovereignty", self.roadmap_block)

    def test_phase_3_name(self):
        self.assertIn("Phase 3: Terminal & Compliance", self.roadmap_block)

    def test_phase_4_name(self):
        self.assertIn("Phase 4: Scaling & Capital", self.roadmap_block)

    def test_phase_1_uses_checkboxes(self):
        checkboxes = re.findall(r"- \[ \]", self.roadmap_block)
        self.assertGreaterEqual(len(checkboxes), 1)

    def test_phase_1_modular_monolith_task(self):
        self.assertIn("Modular Monolith Core", self.roadmap_block)

    def test_phase_1_xgboost_lstm_task(self):
        self.assertIn("XGBoost + LSTM", self.roadmap_block)

    def test_phase_1_kill_criterion(self):
        self.assertIn("Sharpe < 0.5", self.roadmap_block)

    def test_phase_2_fix_gateway_task(self):
        self.assertIn("FIX Gateway", self.roadmap_block)

    def test_phase_3_fincon_terminal_task(self):
        self.assertIn("FinCon Terminal", self.roadmap_block)

    def test_phase_3_mifid_compliance_task(self):
        self.assertIn("MiFID III", self.roadmap_block)

    def test_phase_4_prime_broker_task(self):
        self.assertIn("Prime Broker", self.roadmap_block)

    def test_old_phase_1_name_absent(self):
        self.assertNotIn("Phase 1: MVP — Single Strategy", self.roadmap_block)

    def test_old_phase_4_name_absent(self):
        self.assertNotIn("Phase 4: The Sovereign Platform", self.roadmap_block)


class TestRiskAssessmentTable(unittest.TestCase):
    """
    Risk table in section 12 was updated: 'Team Burnout' replaced
    'Regulatory Non-Compliance'.
    """

    def setUp(self):
        self.content = _read_md()
        match = re.search(
            r"## ⚠️ 12\. Risk Assessment.*?(?=\n## |\Z)",
            self.content,
            re.DOTALL,
        )
        self.risk_block = match.group(0) if match else ""

    def test_risk_section_exists(self):
        self.assertIn("Risk Assessment & Failure Modes", self.content)

    def test_mql5_dependency_risk_present(self):
        self.assertIn("MQL5 Dependency", self.risk_block)

    def test_adversarial_broker_risk_present(self):
        self.assertIn("Adversarial Broker", self.risk_block)

    def test_team_burnout_risk_present(self):
        self.assertIn("Team Burnout", self.risk_block)

    def test_regulatory_non_compliance_removed(self):
        self.assertNotIn("Regulatory Non-Compliance", self.risk_block)

    def test_three_data_rows_in_table(self):
        data_rows = [
            ln for ln in self.risk_block.splitlines()
            if re.match(r"\|\s+\*\*", ln)
        ]
        self.assertEqual(len(data_rows), 3)

    def test_team_burnout_mitigation(self):
        burnout_line = next(
            (ln for ln in self.risk_block.splitlines() if "Team Burnout" in ln), ""
        )
        self.assertIn("8-person redundancy", burnout_line)


class TestSectionStructure(unittest.TestCase):
    """All 13 top-level sections must be present and numbered correctly."""

    def setUp(self):
        self.content = _read_md()
        self.section_headings = re.findall(r"^## .+$", self.content, re.MULTILINE)

    def test_13_sections_present(self):
        self.assertEqual(len(self.section_headings), 13)

    def test_section_1_identity(self):
        self.assertTrue(
            any("1." in h and "Project Identity" in h for h in self.section_headings)
        )

    def test_section_6_risk_management(self):
        self.assertTrue(
            any("6." in h and "Risk Management" in h for h in self.section_headings)
        )

    def test_section_11_roadmap(self):
        self.assertTrue(
            any("11." in h and "Strategic Roadmap" in h for h in self.section_headings)
        )

    def test_section_12_risk_assessment(self):
        self.assertTrue(
            any("12." in h and "Risk Assessment" in h for h in self.section_headings)
        )

    def test_section_13_appendices(self):
        self.assertTrue(
            any("13." in h and "Appendices" in h for h in self.section_headings)
        )


class TestNoDuplicateSections(unittest.TestCase):
    """
    V1.4 had duplicate sections (sections 4-9 appeared twice). V1.5 must not
    repeat any top-level section heading.
    """

    def setUp(self):
        self.content = _read_md()

    def test_no_duplicate_section_4(self):
        matches = re.findall(
            r"## 🏗️ 4\. System Architecture", self.content
        )
        self.assertEqual(len(matches), 1)

    def test_no_duplicate_section_5(self):
        matches = re.findall(
            r"## 🔬 5\. Quantitative Strategy", self.content
        )
        self.assertEqual(len(matches), 1)

    def test_no_duplicate_section_6(self):
        matches = re.findall(
            r"## 🛡️ 6\. Risk Management", self.content
        )
        self.assertEqual(len(matches), 1)

    def test_no_duplicate_section_7(self):
        matches = re.findall(
            r"## .+ 7\. Market Connectivity", self.content
        )
        self.assertEqual(len(matches), 1)

    def test_no_duplicate_technical_specifications(self):
        matches = re.findall(
            r"### 🧱 Technical Specifications", self.content
        )
        self.assertEqual(len(matches), 1)

    def test_no_duplicate_ml_architecture(self):
        matches = re.findall(
            r"### 🧠 ML Architecture", self.content
        )
        self.assertEqual(len(matches), 1)

    def test_no_duplicate_phoenix_gauntlet(self):
        matches = re.findall(
            r"### 🔬 The Phoenix Gauntlet", self.content
        )
        self.assertEqual(len(matches), 1)

    def test_no_duplicate_risk_stack(self):
        matches = re.findall(
            r"### 🛡️ The 7-Layer Risk Stack", self.content
        )
        self.assertEqual(len(matches), 1)


class TestRemovedContent(unittest.TestCase):
    """Content explicitly removed in V1.5 must not appear."""

    def setUp(self):
        self.content = _read_md()

    def test_l99_certification_gap_analysis_removed(self):
        self.assertNotIn("L99 Certification Gap Analysis", self.content)

    def test_l99_a_code_requirement_removed(self):
        self.assertNotIn("L99-A (Code)", self.content)

    def test_l99_b_infra_requirement_removed(self):
        self.assertNotIn("L99-B (Infra)", self.content)

    def test_stability_paradox_section_removed(self):
        self.assertNotIn("The Stability Paradox Resolution", self.content)

    def test_microkernel_critique_removed(self):
        self.assertNotIn("Microkernel Critique", self.content)

    def test_human_capital_economics_removed(self):
        """Monthly cost breakdown was removed in V1.5."""
        self.assertNotIn("Total Monthly Costs", self.content)
        self.assertNotIn("$42,700", self.content)

    def test_appendix_regulatory_matrix_removed(self):
        self.assertNotIn("Appendix A: Regulatory Compliance Matrix", self.content)

    def test_appendix_tech_stack_removed(self):
        self.assertNotIn("Appendix B: Technology Stack", self.content)

    def test_appendix_glossary_removed(self):
        self.assertNotIn("Appendix C: Glossary", self.content)

    def test_sqlite_direct_reference_removed(self):
        """SQLite should only appear in the Institutional Reality Audit section as deprecated."""
        occurrences = [ln for ln in self.content.splitlines() if "SQLite" in ln]
        # Only one mention allowed: the "SQLite is not for Audit" audit item
        self.assertEqual(len(occurrences), 1)
        self.assertIn("SQLite is not for Audit", occurrences[0])


class TestSystemOverviewSection(unittest.TestCase):
    """New 'System Overview (V1.5 Refinement)' subsection added in V1.5."""

    def setUp(self):
        self.content = _read_md()
        match = re.search(
            r"### 🧩 System Overview.*?(?=\n### |\n\n---|\Z)",
            self.content,
            re.DOTALL,
        )
        self.overview_block = match.group(0) if match else ""

    def test_system_overview_section_exists(self):
        self.assertIn("System Overview (V1.5 Refinement)", self.content)

    def test_sovereign_ingress_aes(self):
        self.assertIn("AES-256-GCM Secure Gateway", self.overview_block)

    def test_mt5_phase1_fix_phase2_migration(self):
        self.assertIn("MT5 (Phase 1)", self.overview_block)
        self.assertIn("FIX Protocol Priority (Phase 2)", self.overview_block)

    def test_persistence_layer_components(self):
        self.assertIn("PostgreSQL", self.overview_block)
        self.assertIn("QuestDB", self.overview_block)
        self.assertIn("Redis Cluster", self.overview_block)

    def test_event_bus_protobuf(self):
        self.assertIn("Protocol Buffers (Protobuf)", self.overview_block)

    def test_decision_engine_split(self):
        self.assertIn("Context Loop", self.overview_block)
        self.assertIn("Execution Loop", self.overview_block)

    def test_buf_registry_mentioned(self):
        self.assertIn("Buf Registry", self.overview_block)


class TestRiskStackSection(unittest.TestCase):
    """7-Layer Risk Stack updated: Monte Carlo validation added, latency budget removed."""

    def setUp(self):
        self.content = _read_md()
        match = re.search(
            r"### 🛡️ The 7-Layer Risk Stack.*?(?=\n### |\n\n---|\Z)",
            self.content,
            re.DOTALL,
        )
        self.stack_block = match.group(0) if match else ""

    def test_monte_carlo_validation_present(self):
        self.assertIn("Monte Carlo simulation", self.stack_block)

    def test_conflict_resolution_present(self):
        self.assertIn("Higher precedence always wins", self.stack_block)

    def test_latency_budget_removed(self):
        self.assertNotIn("Latency Budget", self.stack_block)

    def test_seven_layers_listed(self):
        numbered = re.findall(r"^\d+\.", self.stack_block, re.MULTILINE)
        self.assertEqual(len(numbered), 7)


class TestTeamSection(unittest.TestCase):
    """Team section updated with more specific role titles in V1.5."""

    def setUp(self):
        self.content = _read_md()
        match = re.search(
            r"### 👥 Minimum Viable Team.*?(?=\n### |\n\n---|\Z)",
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

    def test_operations_terminal_manager_title(self):
        self.assertIn("Operations/Terminal Manager", self.team_block)

    def test_eight_roles_mentioned(self):
        # Count roles by splitting on common delimiters
        roles = re.split(r",\s*", self.team_block.replace("\n", " "))
        # Filter to lines that look like role descriptions (contain 'x ')
        role_items = [r for r in roles if re.search(r"\dx\s", r)]
        self.assertGreaterEqual(len(role_items), 7)


class TestCoreValuesSection(unittest.TestCase):
    """Core Values section simplified in V1.5 (redundant elaborations removed)."""

    def setUp(self):
        self.content = _read_md()
        match = re.search(
            r"### 💎 Core Values.*?(?=\n### |\n\n---|\Z)",
            self.content,
            re.DOTALL,
        )
        self.values_block = match.group(0) if match else ""

    def test_core_values_section_exists(self):
        self.assertIn("Core Values (V7.1.0)", self.content)

    def test_no_duplicate_core_values_heading(self):
        matches = re.findall(r"### 💎 Core Values", self.content)
        self.assertEqual(len(matches), 1)

    def test_sovereignty_value_present(self):
        self.assertIn("Sovereignty", self.values_block)

    def test_transparency_value_present(self):
        self.assertIn("Transparency", self.values_block)

    def test_performance_value_python_mt5(self):
        self.assertIn("Python + MT5", self.values_block)

    def test_six_core_values_listed(self):
        bullet_items = [
            ln for ln in self.values_block.splitlines()
            if ln.strip().startswith("- **")
        ]
        self.assertEqual(len(bullet_items), 6)


if __name__ == "__main__":
    unittest.main()
