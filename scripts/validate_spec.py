#!/usr/bin/env python3
"""
scripts/validate_spec.py

Mechanically audits full specifications (SPEC.md, specs/<cap>/spec.md)
and delta specifications (specs/changes/<id>/spec.delta.md) for structural
integrity, sequential rule numbering, and domain model totality.

Adheres to Agent Skills script hygiene:
- Human/Machine result payload to stdout.
- Diagnostic logs and error traces to stderr.
- Exit code 0 on valid, 1 on validation error.
"""

import argparse
import json
import os
import re
import sys
from typing import List, Dict, Any, Tuple


class SpecValidationError(Exception):
    """Raised when a specification violates syntax or structural invariants."""



def normalize_header(header: str) -> str:
    """Normalizes a requirement or scenario header for equality comparison."""
    # Strip markdown formatting, trailing hashes, and excess whitespace
    clean = re.sub(r"[#*_`]", "", header).strip()
    return re.sub(r"\s+", " ", clean).lower()


def validate_full_spec(content: str, filepath: str, is_template: bool = False) -> Dict[str, Any]:
    """Validates a complete living specification in OpenSpec, SDD, or Hybrid format."""
    findings: List[str] = []
    
    # 1. Top level header
    if not re.search(r"^#\s+(.+)", content, re.MULTILINE):
        findings.append("Missing top-level H1 header '# <Title>'")
        
    # Detect specification style: OpenSpec vs SDD Rule Engine
    has_requirements_section = bool(re.search(r"##\s+Requirements\b", content, re.IGNORECASE))
    has_rules_section = bool(re.search(r"##\s+Rules\b", content, re.IGNORECASE))
    
    if not (has_requirements_section or has_rules_section):
        findings.append("Spec must contain either a '## Requirements' section (OpenSpec) or '## Rules' section (SDD)")
        return {
            "filepath": filepath,
            "type": "unknown",
            "valid": False,
            "findings": findings
        }
        
    spec_style = "openspec" if has_requirements_section else "sdd_rules"
    
    # Check Purpose / Domain model
    if spec_style == "openspec":
        if not re.search(r"##\s+(Purpose|Overview|Context)\b", content, re.IGNORECASE):
            findings.append("OpenSpec format requires a '## Purpose' or '## Overview' section")
            
        # Parse OpenSpec requirements: ### Requirement: <Name> or ### Requirement R<n>: <Name>
        req_pattern = r"^###\s+Requirement(?:\s+(R\d+|R<n>))?:\s*(.+)$"
        raw_matches = re.findall(req_pattern, content, re.MULTILINE | re.IGNORECASE)
        
        # Also check for ### R<n>: <Name> inside Requirements section if any
        if not raw_matches:
            raw_matches = list(re.findall(r"^###\s+(R\d+|R<n>):\s*(.+)$", content, re.MULTILINE))
            if raw_matches:
                spec_style = "hybrid"
        else:
            if any(r[0] for r in raw_matches):
                spec_style = "hybrid"
                
        if not raw_matches:
            findings.append("No requirements found under '## Requirements' (expected headers like '### Requirement: <Name>')")
        else:
            names = [normalize_header(m[1]) for m in raw_matches]
            # Check duplicate names
            if len(names) != len(set(names)):
                duplicates = [name for name in names if names.count(name) > 1]
                findings.append(f"Duplicate requirement names detected: {sorted(set(duplicates))}")
                
            # Check that each requirement has at least one scenario or SHALL statement
            for r_id, title in raw_matches:
                header_regex = rf"###\s+Requirement(?:\s+{re.escape(r_id)})?:\s*{re.escape(title)}" if r_id else rf"###\s+Requirement:\s*{re.escape(title)}"
                block_m = re.search(rf"{header_regex}[\s\S]*?(?=\n###|\n##|\Z)", content, re.IGNORECASE)
                if block_m:
                    block = block_m.group(0)
                    has_scenario = bool(re.search(r"####\s+Scenario:", block, re.IGNORECASE))
                    has_shall = bool(re.search(r"\b(SHALL|MUST|SHOULD)\b", block))
                    has_behavior = bool(re.search(r"\*\*Behavior\*\*:", block, re.IGNORECASE))
                    if not (has_scenario or has_shall or has_behavior):
                        findings.append(f"Requirement '{title}' is missing both a '#### Scenario:' and an RFC 2119 SHALL/MUST statement")
                        
            # If sequential IDs used, verify sequential numbering
            r_nums = [int(m[0][1:]) for m in raw_matches if m[0] and m[0] != "R<n>"]
            if r_nums and not is_template:
                expected = list(range(1, len(r_nums) + 1))
                if sorted(r_nums) != expected:
                    findings.append(f"Non-sequential rule IDs: found {[f'R{n}' for n in sorted(r_nums)]}, expected {[f'R{n}' for n in expected]}")
                    
    else:  # SDD Rule Engine format
        # Required sections for SDD pure decision engine
        required_sections = [
            ("Domain model", r"##\s+(Domain\s+model|Data\s+model|Model)"),
            ("Global constraints", r"##\s+(Global\s+constraints|Invariants)"),
            ("Rules", r"##\s+Rules"),
            ("Precedence order", r"##\s+Precedence\s+order"),
        ]
        for name, pattern in required_sections:
            if not re.search(pattern, content, re.IGNORECASE):
                findings.append(f"Missing required section in SDD rule format: '## {name}'")
                
        rule_matches = re.findall(r"###\s+(R\d+|R<n>):", content)
        if not rule_matches:
            findings.append("No rules found under '## Rules' (expected headers like '### R1: Name')")
        elif not is_template:
            concrete = [r for r in rule_matches if r != "R<n>"]
            rule_numbers = [int(r[1:]) for r in concrete]
            if len(rule_numbers) != len(set(rule_numbers)):
                duplicates = [f"R{n}" for n in rule_numbers if rule_numbers.count(n) > 1]
                findings.append(f"Duplicate rule IDs detected: {sorted(set(duplicates))}")
            expected = list(range(1, len(rule_numbers) + 1))
            if sorted(rule_numbers) != expected:
                findings.append(f"Non-sequential rule IDs: found {[f'R{n}' for n in sorted(rule_numbers)]}, expected {[f'R{n}' for n in expected]}")
            precedence_match = re.search(r"##\s+Precedence\s+order\s+([\s\S]*?)(?=\n##|\Z)", content, re.IGNORECASE)
            if precedence_match:
                prec_text = precedence_match.group(1)
                for r_id in concrete:
                    if not re.search(rf"\b{r_id}\b", prec_text):
                        findings.append(f"Rule {r_id} declared in '## Rules' is missing from '## Precedence order'")
                        
    return {
        "filepath": filepath,
        "format": spec_style,
        "type": "template" if is_template else "full_spec",
        "valid": len(findings) == 0,
        "rule_count": len(raw_matches) if spec_style in ("openspec", "hybrid") else len(rule_matches),
        "rule_ids": [m[0] if m[0] else m[1] for m in raw_matches] if spec_style in ("openspec", "hybrid") else rule_matches,
        "findings": findings
    }


def validate_delta_spec(content: str, filepath: str, is_template: bool = False) -> Dict[str, Any]:
    """Validates a delta specification (spec.delta.md or openspec delta spec)."""
    findings: List[str] = []
    
    # Delta sections can be either Requirements (OpenSpec) or Rules (SDD)
    has_added = bool(re.search(r"##\s+ADDED\s+(Requirements|Rules)", content, re.IGNORECASE))
    has_modified = bool(re.search(r"##\s+MODIFIED\s+(Requirements|Rules)", content, re.IGNORECASE))
    has_removed = bool(re.search(r"##\s+REMOVED\s+(Requirements|Rules)", content, re.IGNORECASE))
    has_renamed = bool(re.search(r"##\s+RENAMED\s+(Requirements|Rules)", content, re.IGNORECASE))
    
    if not (has_added or has_modified or has_removed or has_renamed):
        findings.append("Delta spec must contain at least one of: '## ADDED Requirements/Rules', '## MODIFIED Requirements/Rules', '## REMOVED Requirements/Rules', or '## RENAMED Requirements/Rules'")
        return {
            "filepath": filepath,
            "valid": False,
            "findings": findings
        }
        
    added_names: List[str] = []
    added_match = re.search(r"##\s+ADDED\s+(Requirements|Rules)\b([\s\S]*?)(?=\n##\s+[A-Z]|\Z)", content, re.IGNORECASE)
    if added_match:
        added_block = added_match.group(2)
        # Find headers strictly at start of line: ^### Requirement: <Name> or ^### R<n>: <Name>
        headers = re.findall(r"^###\s+(?:Requirement(?:\s+(?:R\d+|R<n>))?:\s*|R\d+:|R<n>:)\s*(.+)$", added_block, re.MULTILINE)
        added_names = [h.strip() for h in headers]
        if not added_names:
            findings.append("ADDED section is empty (must contain at least one requirement or rule)")
            
    modified_names: List[str] = []
    modified_match = re.search(r"##\s+MODIFIED\s+(Requirements|Rules)\b([\s\S]*?)(?=\n##\s+[A-Z]|\Z)", content, re.IGNORECASE)
    if modified_match:
        mod_block = modified_match.group(2)
        headers = re.findall(r"^###\s+(?:Requirement(?:\s+(?:R\d+|R<n>))?:\s*|R\d+:|R<n>:)\s*(.+)$", mod_block, re.MULTILINE)
        modified_names = [h.strip() for h in headers]
        
    removed_names: List[str] = []
    removed_match = re.search(r"##\s+REMOVED\s+(Requirements|Rules)\b([\s\S]*?)(?=\n##\s+[A-Z]|\Z)", content, re.IGNORECASE)
    if removed_match:
        rem_block = removed_match.group(2)
        headers = re.findall(r"^###\s+(?:Requirement(?:\s+(?:R\d+|R<n>))?:\s*|R\d+:|R<n>:)\s*(.+)$", rem_block, re.MULTILINE)
        removed_names = [h.strip() for h in headers]
        
    def extract_r_ids(names: List[str], raw_block: str) -> List[str]:
        r_ids = re.findall(r"^###\s+(?:Requirement\s+)?(R\d+|R<n>):", raw_block, re.MULTILINE)
        return r_ids if r_ids else names

    added_r_ids = extract_r_ids(added_names, added_match.group(2) if added_match else "")
    modified_r_ids = extract_r_ids(modified_names, modified_match.group(2) if modified_match else "")
    removed_r_ids = extract_r_ids(removed_names, removed_match.group(2) if removed_match else "")
        
    return {
        "filepath": filepath,
        "type": "delta_template" if is_template else "delta_spec",
        "valid": len(findings) == 0,
        "added": added_names,
        "modified": modified_names,
        "removed": removed_names,
        "added_rules": added_r_ids,
        "modified_rules": modified_r_ids,
        "removed_rules": removed_r_ids,
        "findings": findings
    }


def validate_file(filepath: str, is_delta: bool = False, is_template: bool = False) -> Tuple[bool, Dict[str, Any]]:
    """Reads and validates the given spec file."""
    if not os.path.exists(filepath):
        sys.stderr.write(f"Error: Spec file '{filepath}' does not exist.\n")
        return False, {"filepath": filepath, "valid": False, "findings": ["File does not exist"]}
        
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Auto-detect template if in template path
    if "template" in os.path.basename(filepath).lower():
        is_template = True
        
    # Auto-detect if not explicitly provided
    if is_delta or "delta" in os.path.basename(filepath).lower() or re.search(r"##\s+(ADDED|MODIFIED|REMOVED)\s+Rules", content, re.IGNORECASE):
        report = validate_delta_spec(content, filepath, is_template=is_template)
    else:
        report = validate_full_spec(content, filepath, is_template=is_template)
        
    return report["valid"], report


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate SDD specification or delta specification.")
    parser.add_argument("spec_file", type=str, help="Path to SPEC.md or spec.delta.md")
    parser.add_argument("--delta", action="store_true", help="Force validation as delta specification")
    parser.add_argument("--template", action="store_true", help="Validate as template (allows R<n> placeholders)")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON format")
    
    args = parser.parse_args()

    try:
        is_valid, report = validate_file(args.spec_file, is_delta=args.delta, is_template=args.template)
    except Exception as exc:  # noqa: BLE001 - the validator must never masquerade a bug as an invalid spec
        # Exit code 2 signals "the validator could not run" (a bug or environment
        # problem) as distinct from exit 1 ("the spec is genuinely invalid"), so
        # callers such as the commit gate can fail OPEN on infrastructure errors.
        sys.stderr.write(f"VALIDATOR ERROR: {exc}\n")
        sys.exit(2)

    if args.json:
        sys.stdout.write(json.dumps(report, indent=2) + "\n")
    else:
        if is_valid:
            sys.stdout.write(f"VALID: {args.spec_file} conforms to SDD specification format.\n")
            if report.get("type") in ("full_spec", "template"):
                sys.stdout.write(f"Rules declared: {len(report.get('rule_ids', []))} ({', '.join(report.get('rule_ids', []))})\n")
            else:
                sys.stdout.write(f"Added: {report.get('added_rules', [])}, Modified: {report.get('modified_rules', [])}, Removed: {report.get('removed_rules', [])}\n")
        else:
            sys.stderr.write(f"INVALID: {args.spec_file} failed specification audit:\n")
            for finding in report.get("findings", []):
                sys.stderr.write(f"  - {finding}\n")
                
    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()
