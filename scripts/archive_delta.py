#!/usr/bin/env python3
"""
scripts/archive_delta.py

Mechanically merges a delta specification (from specs/changes/<id>/spec.delta.md)
into the persistent capability specification (specs/<capability>/spec.md or root SPEC.md)
and archives the change directory to specs/archive/<date>-<id>/.

Adheres to Agent Skills script hygiene:
- Human/Machine result payload to stdout.
- Diagnostic logs and error traces to stderr.
- Exit code 0 on success, 1 on failure.
"""

import argparse
import datetime
import json
import os
import re
import shutil
import sys
from typing import Any, Dict, List, Optional, Tuple

from validate_spec import validate_delta_spec, validate_full_spec


class DeltaArchiveError(Exception):
    """Raised when archiving a delta fails."""



def extract_metadata(content: str) -> Dict[str, str]:
    """Extracts frontmatter or top metadata lines from delta spec."""
    meta: Dict[str, str] = {}
    lines = content.splitlines()
    for line in lines[:25]:
        m = re.match(r"^\s*[-*]?\s*\*\*([A-Za-z_-]+)\*\*:\s*(.*)$", line)
        if m:
            meta[m.group(1).lower()] = m.group(2).strip()
    return meta


def resolve_target_spec(delta_path: str, meta: Dict[str, str], repo_root: str) -> str:
    """Determines the target persistent specification file."""
    # 1. Capability in metadata
    cap = meta.get("capability") or meta.get("domain") or meta.get("target")
    if cap:
        target = os.path.join(repo_root, "specs", cap, "spec.md")
        if os.path.exists(target):
            return target
        # Check if specs/<cap>.md
        alt_target = os.path.join(repo_root, "specs", f"{cap}.md")
        if os.path.exists(alt_target):
            return alt_target
            
    # 2. Check if a capability name matches parent folder
    change_dir = os.path.dirname(os.path.abspath(delta_path))
    parent_specs_dir = os.path.dirname(change_dir)
    if os.path.basename(parent_specs_dir) == "changes":
        specs_root = os.path.dirname(parent_specs_dir)
        # If there are subdirectories in specs_root other than changes & archive
        for entry in os.listdir(specs_root):
            candidate = os.path.join(specs_root, entry, "spec.md")
            if os.path.isfile(candidate) and entry in os.path.basename(change_dir):
                return candidate

    # 3. Default to root SPEC.md
    root_spec = os.path.join(repo_root, "SPEC.md")
    if os.path.exists(root_spec):
        return root_spec

    # 4. If specs/spec.md exists
    spec_in_specs = os.path.join(repo_root, "specs", "spec.md")
    if os.path.exists(spec_in_specs):
        return spec_in_specs
        
    return root_spec


def extract_requirement_blocks(section_content: str) -> List[Tuple[str, str, str]]:
    """
    Extracts individual requirement or rule blocks from a markdown section.
    Returns list of tuples: (full_header_line, normalized_name, full_block_text)
    """
    blocks: List[Tuple[str, str, str]] = []
    # Match headers at start of line
    pattern = r"(^###\s+(?:Requirement(?:\s+(?:R\d+|R<n>))?:\s*|R\d+:|R<n>:)\s*(.+)$)"
    matches = list(re.finditer(pattern, section_content, re.MULTILINE))
    
    for i, m in enumerate(matches):
        full_header = m.group(1).strip()
        name = m.group(2).strip()
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(section_content)
        block_text = section_content[start:end].strip()
        blocks.append((full_header, name, block_text))

    return blocks


def parse_header(header: str) -> Tuple[Optional[str], str]:
    """Splits a requirement/rule header into (rule_id, name).

    Accepts every supported header style so the archiver is format-agnostic:
    ``### R1: Name`` (SDD), ``### Requirement R1: Name`` (Hybrid), and
    ``### Requirement: Name`` (OpenSpec, no id). Returns ``(None, name)`` when
    the header carries no rule id.
    """
    m = re.match(r"^###\s+(?:Requirement\s+)?(R\d+|R<n>):\s*(.*)$", header)
    if m:
        return m.group(1), m.group(2).strip()
    m = re.match(r"^###\s+Requirement:\s*(.+)$", header)
    if m:
        return None, m.group(1).strip()
    m = re.match(r"^###\s+(.+)$", header)
    return None, (m.group(1).strip() if m else header.strip())


def target_block_pattern(rule_id: str) -> str:
    """Regex matching a rule block in the target for ``R1`` or ``Requirement R1`` headers."""
    return rf"^###\s+(?:Requirement\s+)?{rule_id}:[\s\S]*?(?=\n###|\n##|\Z)"


def parse_precedence_hint(block_text: str) -> Optional[Tuple[str, Optional[str]]]:
    """Reads a ``- **Precedence**: ...`` line and returns a placement directive.

    Returns ``("before", "R2")`` / ``("after", "R2")`` / ``("first", None)`` /
    ``("last", None)``, or ``None`` when no precedence is declared.
    """
    m = re.search(r"\*\*Precedence\*\*:\s*(.+)", block_text, re.IGNORECASE)
    if not m:
        return None
    directive = m.group(1).strip()
    rel = re.search(r"\b(before|after)\b.*?\b(R\d+)\b", directive, re.IGNORECASE)
    if rel:
        return rel.group(1).lower(), rel.group(2)
    if re.search(r"\bfirst\b|\bhighest\b", directive, re.IGNORECASE):
        return "first", None
    if re.search(r"\blast\b|\blowest\b", directive, re.IGNORECASE):
        return "last", None
    return None


def apply_delta_to_spec(target_content: str, delta_content: str) -> Tuple[str, List[str]]:
    """Applies added, modified, renamed, and removed requirements/rules to target content.

    Returns the updated content and a list of human-readable warnings (e.g. added
    rules whose precedence position was not declared and so were appended).
    """
    updated = target_content
    warnings: List[str] = []

    # 1. Apply RENAMED Requirements (OpenSpec convention)
    renamed_match = re.search(r"##\s+RENAMED\s+(Requirements|Rules)\b([\s\S]*?)(?=\n##\s+[A-Z]|\Z)", delta_content, re.IGNORECASE)
    if renamed_match:
        ren_block = renamed_match.group(2)
        pairs = re.findall(r"FROM:\s*`?(?:###\s+Requirement:\s*)?([^`\n]+)`?\s*\n\s*-\s*TO:\s*`?(?:###\s+Requirement:\s*)?([^`\n]+)`?", ren_block, re.IGNORECASE)
        for old_name, new_name in pairs:
            old_name = old_name.strip()
            new_name = new_name.strip()
            # Replace old header in target
            old_pattern = rf"^###\s+Requirement:\s*{re.escape(old_name)}\b"
            updated = re.sub(old_pattern, f"### Requirement: {new_name}", updated, flags=re.MULTILINE | re.IGNORECASE)

    # 2. Apply MODIFIED Requirements / Rules
    mod_match = re.search(r"##\s+MODIFIED\s+(Requirements|Rules)\b([\s\S]*?)(?=\n##\s+[A-Z]|\Z)", delta_content, re.IGNORECASE)
    if mod_match:
        mod_block = mod_match.group(2)
        mod_blocks = extract_requirement_blocks(mod_block)
        for header, name, new_block_text in mod_blocks:
            # Prefer matching by stable rule id (works even when the title changed);
            # fall back to the requirement name for id-less OpenSpec requirements.
            r_id, _name = parse_header(header)
            if r_id:
                target_m = re.search(target_block_pattern(r_id), updated, re.MULTILINE)
            else:
                norm_name = re.escape(name)
                target_m = re.search(rf"^###\s+Requirement(?:\s+R\d+)?:\s*{norm_name}[\s\S]*?(?=\n###|\n##|\Z)", updated, re.MULTILINE | re.IGNORECASE)

            if target_m:
                updated = updated[:target_m.start()] + new_block_text + "\n\n" + updated[target_m.end():]
                # Re-sync human label in ## Precedence order if present and title changed
                if r_id and _name:
                    updated = re.sub(
                        rf"^(\s*\d+\.\s+{re.escape(r_id)}\b\s*[—–-]\s*).*$",
                        rf"\g<1>{_name}",
                        updated,
                        flags=re.MULTILINE
                    )
            else:
                raise DeltaArchiveError(f"Cannot modify '{name}': requirement does not exist in target specification")

    # 3. Apply ADDED Requirements / Rules
    add_match = re.search(r"##\s+ADDED\s+(Requirements|Rules)\b([\s\S]*?)(?=\n##\s+[A-Z]|\Z)", delta_content, re.IGNORECASE)
    if add_match:
        add_block = add_match.group(2)
        add_blocks = extract_requirement_blocks(add_block)
        added_text = "\n\n".join(b[2] for b in add_blocks) + "\n\n"
        
        # Check where to insert
        prec_match = re.search(r"##\s+Precedence\s+order", updated, re.IGNORECASE)
        if prec_match:
            updated = updated[:prec_match.start()] + added_text + updated[prec_match.start():]
            updated = _splice_precedence(updated, add_blocks, warnings)
        else:
            # OpenSpec: append to end of Requirements or document
            updated = updated.rstrip() + "\n\n" + added_text.strip() + "\n"

    # 4. Apply REMOVED Requirements / Rules
    rem_match = re.search(r"##\s+REMOVED\s+(Requirements|Rules)\b([\s\S]*?)(?=\n##\s+[A-Z]|\Z)", delta_content, re.IGNORECASE)
    if rem_match:
        rem_block = rem_match.group(2)
        rem_blocks = extract_requirement_blocks(rem_block)
        # Also check for list of requirement headers: - `### Requirement: ...`
        if not rem_blocks:
            rem_names = re.findall(r"-\s*`?(?:###\s+Requirement:\s*)?([^`\n]+)`?", rem_block)
            for name in rem_names:
                name = name.strip()
                norm_name = re.escape(name)
                updated = re.sub(rf"^###\s+Requirement(?:\s+R\d+)?:\s*{norm_name}[\s\S]*?(?=\n###|\n##|\Z)", "", updated, flags=re.MULTILINE | re.IGNORECASE)
        else:
            for header, name, _ in rem_blocks:
                r_id, _name = parse_header(header)
                if r_id:
                    target_m = re.search(target_block_pattern(r_id), updated, re.MULTILINE)
                    if target_m:
                        superseded_text = f"### {r_id}: [REMOVED/SUPERSEDED]\n\n- **Status**: Removed\n"
                        updated = updated[:target_m.start()] + superseded_text + updated[target_m.end():]
                        updated = _renumber_precedence(_drop_precedence_entry(updated, r_id))
                else:
                    norm_name = re.escape(name)
                    updated = re.sub(rf"^###\s+Requirement(?:\s+R\d+)?:\s*{norm_name}[\s\S]*?(?=\n###|\n##|\Z)", "", updated, flags=re.MULTILINE | re.IGNORECASE)

    return updated, warnings


def _precedence_bounds(lines: List[str]) -> Tuple[int, int]:
    """Returns (start, end) line indices of the precedence list body, or (-1, -1)."""
    header_idx = next(
        (i for i, l in enumerate(lines) if re.match(r"^##\s+Precedence\s+order", l, re.IGNORECASE)),
        -1,
    )
    if header_idx == -1:
        return -1, -1
    end = header_idx + 1
    while end < len(lines) and not lines[end].startswith("## "):
        end += 1
    return header_idx + 1, end


def _renumber_precedence(content: str) -> str:
    """Rewrites the numbered precedence list so entries read 1., 2., 3., ... contiguously."""
    lines = content.splitlines()
    start, end = _precedence_bounds(lines)
    if start == -1:
        return content
    counter = 0
    for i in range(start, end):
        if re.match(r"^\s*\d+\.\s+", lines[i]):
            counter += 1
            lines[i] = re.sub(r"^\s*\d+\.\s+", f"{counter}. ", lines[i])
    return "\n".join(lines)


def _drop_precedence_entry(content: str, rule_id: str) -> str:
    """Removes the numbered precedence entry for a rule id (both header styles)."""
    return re.sub(rf"^\s*\d+\.\s+{rule_id}\b.*$\n?", "", content, flags=re.MULTILINE)


def _splice_precedence(content: str, add_blocks: List[Tuple[str, str, str]], warnings: List[str]) -> str:
    """Inserts each added rule into the numbered precedence list at its declared position.

    Honors a ``- **Precedence**: before/after Rn`` (or first/last) directive in the
    rule block; when none is declared the rule is appended and a warning is recorded.
    """
    lines = content.splitlines()
    start, end = _precedence_bounds(lines)
    if start == -1:
        return content

    entries = lines[start:end]

    def entry_index(rule_id: str) -> int:
        for i, line in enumerate(entries):
            if re.match(rf"^\s*\d+\.\s+{rule_id}\b", line):
                return i
        return -1

    for header, name, block_text in add_blocks:
        r_id, r_name = parse_header(header)
        if not r_id:
            continue
        new_line = f"0. {r_id} — {r_name or name}"
        hint = parse_precedence_hint(block_text)
        pos = len(entries)  # default: append
        if hint:
            kind, ref = hint
            if kind == "first":
                pos = 0
            elif kind == "last":
                pos = len(entries)
            elif ref:
                ref_idx = entry_index(ref)
                if ref_idx == -1:
                    warnings.append(f"{r_id}: precedence references unknown {ref}; appended to the end.")
                else:
                    pos = ref_idx if kind == "before" else ref_idx + 1
        else:
            warnings.append(f"{r_id}: no precedence position declared; appended to the end — review the order.")
        entries.insert(pos, new_line)

    lines = lines[:start] + entries + lines[end:]
    return _renumber_precedence("\n".join(lines))


def archive_change(change_id: str, repo_root: str) -> Dict[str, Any]:
    """Performs the complete archive operation for a single change."""
    change_dir = os.path.join(repo_root, "specs", "changes", change_id)
    if not os.path.exists(change_dir):
        # Check if change_id is a full path
        if os.path.exists(change_id) and os.path.isdir(change_id):
            change_dir = os.path.abspath(change_id)
            change_id = os.path.basename(change_dir)
        else:
            raise DeltaArchiveError(f"Change directory not found: '{change_dir}'")

    delta_file = os.path.join(change_dir, "spec.delta.md")
    if not os.path.exists(delta_file):
        raise DeltaArchiveError(f"Delta file 'spec.delta.md' missing in {change_dir}")

    with open(delta_file, "r", encoding="utf-8") as f:
        delta_content = f.read()

    # Step 1: Validate Delta Spec
    sys.stderr.write(f"Validating delta specification: {delta_file}\n")
    delta_report = validate_delta_spec(delta_content, delta_file)
    if not delta_report["valid"]:
        raise DeltaArchiveError(f"Invalid delta spec: {'; '.join(delta_report['findings'])}")

    # Step 2: Resolve and Read Target Spec
    meta = extract_metadata(delta_content)
    target_spec_path = resolve_target_spec(delta_file, meta, repo_root)
    sys.stderr.write(f"Resolved target specification: {target_spec_path}\n")

    if not os.path.exists(target_spec_path):
        raise DeltaArchiveError(f"Target specification file '{target_spec_path}' does not exist")

    with open(target_spec_path, "r", encoding="utf-8") as f:
        target_content = f.read()

    # Step 3: Apply Deltas
    updated_content, warnings = apply_delta_to_spec(target_content, delta_content)
    for warning in warnings:
        sys.stderr.write(f"WARNING: {warning}\n")

    # Step 4: Validate resulting Target Spec
    sys.stderr.write(f"Validating updated specification integrity...\n")
    spec_report = validate_full_spec(updated_content, target_spec_path)
    if not spec_report["valid"]:
        raise DeltaArchiveError(
            f"Merging delta results in invalid specification: {'; '.join(spec_report['findings'])}"
        )

    # Step 5: Write Target Spec
    with open(target_spec_path, "w", encoding="utf-8") as f:
        f.write(updated_content)
    sys.stderr.write(f"Successfully updated {target_spec_path}\n")

    # Step 6: Move Change Directory to Archive
    archive_root = os.path.join(repo_root, "specs", "archive")
    os.makedirs(archive_root, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    archived_dir_name = f"{timestamp}-{change_id}"
    archived_dest = os.path.join(archive_root, archived_dir_name)

    shutil.move(change_dir, archived_dest)
    sys.stderr.write(f"Archived change to {archived_dest}\n")

    return {
        "change_id": change_id,
        "target_spec": target_spec_path,
        "archived_to": archived_dest,
        "added_rules": delta_report.get("added_rules", []),
        "modified_rules": delta_report.get("modified_rules", []),
        "removed_rules": delta_report.get("removed_rules", []),
        "warnings": warnings,
        "status": "success"
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge and archive an SDD delta specification.")
    parser.add_argument("--change", type=str, required=True, help="Change identifier or directory path (e.g. issue-42-filter)")
    parser.add_argument("--repo-root", type=str, default=os.getcwd(), help="Root directory of the repository")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON format")

    args = parser.parse_args()

    try:
        report = archive_change(args.change, args.repo_root)
        if args.json:
            sys.stdout.write(json.dumps(report, indent=2) + "\n")
        else:
            sys.stdout.write(f"SUCCESS: Archived change '{report['change_id']}'\n")
            sys.stdout.write(f"  Target Spec:   {report['target_spec']}\n")
            sys.stdout.write(f"  Archive Path:  {report['archived_to']}\n")
            sys.stdout.write(f"  Rules Added:   {report['added_rules']}\n")
            sys.stdout.write(f"  Rules Modified:{report['modified_rules']}\n")
            sys.stdout.write(f"  Rules Removed: {report['removed_rules']}\n")
        sys.exit(0)
    except Exception as e:
        sys.stderr.write(f"ERROR: {str(e)}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
