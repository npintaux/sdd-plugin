"""
tests/test_core_scripts.py

Unit and integration tests for:
- scripts/validate_spec.py
- scripts/pattern_selector.py
- scripts/archive_delta.py
"""

import os
import shutil
import tempfile
import unittest
import sys

# Add scripts directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts")))

from validate_spec import validate_full_spec, validate_delta_spec
from pattern_selector import recommend
from archive_delta import apply_delta_to_spec, archive_change


class TestValidateSpec(unittest.TestCase):
    def test_valid_full_spec(self):
        content = """# Specification: Decision Engine

## Domain model
- Request: amount (int), category (str)
- Decision: outcome (str), rule_ids (list)

## Global constraints
- All requests must have positive amounts.

## Rules
### R1: Small office expense
- **Behavior**: Auto-approve under $100.
- **Example**: `evaluate(amount=50)` -> `APPROVE, ["R1"]`

### R2: Large expense review
- **Behavior**: Review over $100.
- **Example**: `evaluate(amount=500)` -> `REVIEW, ["R2"]`

## Precedence order
1. R2 — Large expense review
2. R1 — Small office expense
"""
        report = validate_full_spec(content, "test.md")
        self.assertTrue(report["valid"], f"Expected valid spec, got: {report['findings']}")
        self.assertEqual(report["rule_count"], 2)

    def test_non_sequential_rules_fail(self):
        content = """# Spec
## Domain model
...
## Global constraints
...
## Rules
### R1: First
- **Behavior**: ...
### R3: Third (gap!)
- **Behavior**: ...
## Precedence order
1. R1
2. R3
"""
        report = validate_full_spec(content, "test.md")
        self.assertFalse(report["valid"])
        self.assertTrue(any("Non-sequential" in f for f in report["findings"]))

    def test_valid_delta_spec(self):
        content = """# Delta: issue-42-vip-rule

## ADDED Rules
### R3: VIP auto approval
- **Behavior**: VIP members get auto-approval.
- **Example**: `evaluate(vip=True)` -> `APPROVE, ["R3"]`
- **Precedence**: Evaluated before R1
"""
        report = validate_delta_spec(content, "delta.md")
        self.assertTrue(report["valid"], f"Expected valid delta, got: {report['findings']}")
        self.assertEqual(report["added_rules"], ["R3"])


class TestPatternSelector(unittest.TestCase):
    def test_pattern_recommendation(self):
        rec = recommend("We need an event-driven order lifecycle transition table with human approval gates")
        self.assertEqual(rec["domain_pattern"]["key"], "state-machine")
        agentic_names = [p["name"] for p in rec["agentic_patterns"]]
        self.assertIn("Human-in-the-Loop", agentic_names)

    def test_word_boundary_isolation(self):
        # 'input' contains 'put' and 'budget' contains 'get', which should NOT trigger repository-service CRUD
        rec = recommend("Evaluate input compliance and budget ceilings against strict rules")
        self.assertEqual(rec["domain_pattern"]["key"], "decision-list")

    def test_zero_match_fallback_transparency(self):
        # An opaque or generic prompt with 0 keyword hits must be flagged as fallback
        rec = recommend("xyz unrelated gibberish without architectural keywords")
        self.assertTrue(rec["domain_pattern"]["is_fallback"])
        self.assertEqual(rec["domain_pattern"]["confidence"], "none")
        self.assertEqual(rec["domain_pattern"]["relevance_score"], 0)
        self.assertTrue(rec["agentic_is_fallback"])



class TestArchiveDelta(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.specs_dir = os.path.join(self.test_dir, "specs")
        self.changes_dir = os.path.join(self.specs_dir, "changes")
        self.archive_dir = os.path.join(self.specs_dir, "archive")
        os.makedirs(self.changes_dir, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_archive_delta_lifecycle(self):
        # 1. Create target capability spec
        cap_dir = os.path.join(self.specs_dir, "finance")
        os.makedirs(cap_dir, exist_ok=True)
        spec_path = os.path.join(cap_dir, "spec.md")
        
        initial_spec = """# Specification: Finance Engine

## Domain model
- Request: amount (int)
- Decision: outcome (str), rule_ids (list)

## Global constraints
- Positive amounts only.

## Rules
### R1: Auto approve under 50
- **Behavior**: Approve under 50.
- **Example**: `evaluate(amount=30)` -> `APPROVE, ["R1"]`

### R2: Review over 50
- **Behavior**: Review over 50.
- **Example**: `evaluate(amount=100)` -> `REVIEW, ["R2"]`

## Precedence order
1. R2 — Review over 50
2. R1 — Auto approve under 50
"""
        with open(spec_path, "w", encoding="utf-8") as f:
            f.write(initial_spec)

        # 2. Create delta change
        change_dir = os.path.join(self.changes_dir, "issue-55-super-vip")
        os.makedirs(change_dir, exist_ok=True)
        delta_path = os.path.join(change_dir, "spec.delta.md")

        delta_content = """# Delta: issue-55-super-vip
- **Capability**: finance

## ADDED Rules
### R3: Super VIP instant approval
- **Behavior**: Super VIP requests are always approved.
- **Example**: `evaluate(tier="super_vip")` -> `APPROVE, ["R3"]`

## MODIFIED Rules
### R2: Review threshold elevated
- **Behavior**: Review over 150 rather than 50.
- **Example**: `evaluate(amount=200)` -> `REVIEW, ["R2"]`
"""
        with open(delta_path, "w", encoding="utf-8") as f:
            f.write(delta_content)

        # 3. Run archive_change
        report = archive_change("issue-55-super-vip", repo_root=self.test_dir)
        self.assertEqual(report["status"], "success")

        # 4. Verify spec was updated
        with open(spec_path, "r", encoding="utf-8") as f:
            updated = f.read()

        self.assertIn("R3: Super VIP instant approval", updated)
        self.assertIn("R2: Review threshold elevated", updated)
        self.assertIn("3. R3 — Super VIP instant approval", updated)

        # 5. Verify change folder was moved to archive
        self.assertFalse(os.path.exists(change_dir))
        self.assertTrue(os.path.exists(report["archived_to"]))

    def test_archive_hybrid_delta_with_precedence(self):
        # Hybrid format: `### Requirement R<n>:` headers, MODIFIED with a changed
        # title, ADDED with a declared precedence position.
        cap_dir = os.path.join(self.specs_dir, "pricing")
        os.makedirs(cap_dir, exist_ok=True)
        spec_path = os.path.join(cap_dir, "spec.md")
        initial_spec = """# Specification: Pricing Engine

## Purpose
Decide whether a purchase is approved or reviewed.

## Domain model
- Request: amount (int)
- Decision: outcome (str), rule_ids (list)

## Global constraints
- Positive amounts only.

## Requirements

### Requirement R1: Small purchase auto-approve
The system SHALL approve purchases under 100.

### Requirement R2: Large purchase review
The system SHALL review purchases over 100.

## Precedence order
1. R2 — Large purchase review
2. R1 — Small purchase auto-approve
"""
        with open(spec_path, "w", encoding="utf-8") as f:
            f.write(initial_spec)

        change_dir = os.path.join(self.changes_dir, "issue-70-vip")
        os.makedirs(change_dir, exist_ok=True)
        delta_path = os.path.join(change_dir, "spec.delta.md")
        delta_content = """# Delta: issue-70-vip
- **Capability**: pricing

## ADDED Requirements
### Requirement R3: VIP instant approval
The system SHALL always approve VIP requests.
- **Precedence**: Evaluated before R2

## MODIFIED Requirements
### Requirement R2: Large purchase manual review (renamed)
The system SHALL review purchases over 250.
"""
        with open(delta_path, "w", encoding="utf-8") as f:
            f.write(delta_content)

        report = archive_change("issue-70-vip", repo_root=self.test_dir)
        self.assertEqual(report["status"], "success")

        with open(spec_path, "r", encoding="utf-8") as f:
            updated = f.read()

        requirements = updated.split("## Precedence order")[0]
        # MODIFIED matched by id despite the changed title.
        self.assertIn("Large purchase manual review", requirements)
        self.assertIn("over 250", requirements)
        self.assertNotIn("### Requirement R2: Large purchase review", requirements)
        # ADDED rule inserted before R2 in the precedence order and renumbered.
        prec = updated.split("## Precedence order")[1]
        r3_pos = prec.index("R3")
        r2_pos = prec.index("R2")
        self.assertLess(r3_pos, r2_pos, "R3 should precede R2 per the declared precedence")
        self.assertIn("1. R3", prec)
        self.assertIn("2. R2 — Large purchase manual review (renamed)", prec)

    def test_apply_delta_reports_missing_precedence_warning(self):
        target = """# Spec
## Domain model
x
## Global constraints
x
## Rules
### R1: First
- **Behavior**: ...
## Precedence order
1. R1 — First
"""
        delta = """# Delta
## ADDED Rules
### R2: Second
- **Behavior**: ...
"""
        _updated, warnings = apply_delta_to_spec(target, delta)
        self.assertTrue(any("no precedence position declared" in w for w in warnings))

    def test_archive_openspec_delta(self):
        # Test OpenSpec format: Requirements, Scenarios, ADDED, MODIFIED, RENAMED
        spec_path = os.path.join(self.test_dir, "specs", "auth", "spec.md")
        os.makedirs(os.path.dirname(spec_path), exist_ok=True)
        initial_spec = """# Authentication Specification

## Purpose
Provides user identity verification and token generation.

## Requirements

### Requirement: Token Expiry Check
The service SHALL invalidate tokens older than 1 hour.

#### Scenario: Expired token
- **GIVEN** a token generated 2 hours ago
- **WHEN** user requests a protected resource
- **THEN** return 401 Unauthorized
"""
        with open(spec_path, "w", encoding="utf-8") as f:
            f.write(initial_spec)

        change_dir = os.path.join(self.changes_dir, "auth-refresh-tokens")
        os.makedirs(change_dir, exist_ok=True)
        delta_path = os.path.join(change_dir, "spec.delta.md")

        delta_content = """# Delta: auth-refresh-tokens
- **Capability**: auth

## RENAMED Requirements
- FROM: `### Requirement: Token Expiry Check`
- TO: `### Requirement: Token Lifespan Check`

## MODIFIED Requirements
### Requirement: Token Lifespan Check
The service SHALL invalidate tokens older than 30 minutes.

#### Scenario: Expired token after 30m
- **WHEN** token age exceeds 30 minutes
- **THEN** return 401 Unauthorized

## ADDED Requirements
### Requirement: Refresh Token Rotation
The service SHALL issue a new refresh token upon each refresh.

#### Scenario: Rotation on refresh
- **WHEN** user submits valid refresh token
- **THEN** invalidate old refresh token and issue new token pair
"""
        with open(delta_path, "w", encoding="utf-8") as f:
            f.write(delta_content)

        report = archive_change("auth-refresh-tokens", repo_root=self.test_dir)
        self.assertEqual(report["status"], "success")

        with open(spec_path, "r", encoding="utf-8") as f:
            updated = f.read()

        self.assertIn("Requirement: Token Lifespan Check", updated)
        self.assertIn("older than 30 minutes", updated)
        self.assertIn("Requirement: Refresh Token Rotation", updated)
        self.assertNotIn("Token Expiry Check", updated)


if __name__ == "__main__":
    unittest.main()
