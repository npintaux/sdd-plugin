---
name: archive-spec
description: Specification Synchronization and Archival persona. Validates completed delta specifications (specs/changes/id/spec.delta.md), merges added and modified rules into persistent capability specifications (specs/capability/spec.md or root SPEC.md), and archives the change directory to specs/archive/. Use when an implemented change has passed tests and review, and its rules must be permanently synchronized into the living specification ("/archive-spec", "archive spec", "merge delta spec", "archive change", "sync specification").
---

# Specification Synchronization & Archival

## Overview
This skill embodies the **Specification Synchronization & Archival** persona. It provides the native Python automation to merge staged delta specifications (`specs/changes/<id>/spec.delta.md`) into persistent capability specifications (`specs/<capability>/spec.md` or root `SPEC.md`). It ensures that sequential rule numbering (`R1..Rn`) and precedence order remain mathematically unbroken, then archives the applied change folder into `specs/archive/<timestamp>-<id>/`.

## When to use
- When an acceptance criterion or feature branch implementation is fully green and reviewed.
- When merging staged rules from `specs/changes/<id>/spec.delta.md` into the authoritative capability spec.
- When retiring or archiving an applied change proposal.
- Use slash command `/archive-spec` or trigger phrases like "archive spec", "merge delta spec", or "archive change".

## When NOT to use
- Do not use for drafting or proposing new acceptance criteria (use `/specify`).
- Do not use for writing code or unit tests (use `/implement`).
- Do not use for macro-architecture or pattern selection (use `/architect`).
- Do not use for committing code to git (use `/commit`).
- Do not use during active development before tests pass.

## Preconditions / Inputs
1. A valid change directory under `specs/changes/<change-id>/` containing `spec.delta.md` (or `openspec/changes/<id>/specs/<cap>/spec.md`).
2. All unit tests for the change must be passing (`pytest` green).
3. The delta specification must adhere to either OpenSpec delta conventions (`## ADDED/MODIFIED/REMOVED/RENAMED Requirements`) or SDD conventions (`## ADDED/MODIFIED/REMOVED Rules`).
4. Working Python runtime with `scripts/archive_delta.py` and `scripts/validate_spec.py`.

## Procedure

### Step 1: Verify Change Readiness & Pre-Validation
1. Confirm that unit tests for the change are passing:
   ```bash
   pytest
   ```
2. Validate the delta specification structure before merging:
   ```bash
   python3 scripts/validate_spec.py specs/changes/<change-id>/spec.delta.md --delta
   ```
3. If validation fails, report the syntax errors and halt before touching persistent specifications.

### Step 2: Execute Delta Merging and Archiving
1. Run the native archive script targeting the change identifier:
   ```bash
   python3 scripts/archive_delta.py --change <change-id>
   ```
2. The script will:
   - Resolve the target capability specification from metadata or path.
   - Splice `## ADDED Rules` into the persistent spec and update `## Precedence order`.
   - Update `## MODIFIED Rules` in place.
   - Mark `## REMOVED Rules` as deprecated to preserve ID history.
   - Run full structural and sequential validation on the updated specification.
   - Move `specs/changes/<change-id>/` to `specs/archive/<timestamp>-<change-id>/`.

### Step 3: Verify Updated Specification
1. Inspect the resulting capability specification or root `SPEC.md`:
   ```bash
   python3 scripts/validate_spec.py specs/<capability>/spec.md
   ```
2. Confirm that all new rules are listed in sequential order without gaps or duplicates.
3. Confirm that the change directory was successfully relocated to `specs/archive/`.

## Common Rationalizations
- *"We can manually copy-paste the rules into SPEC.md instead of running the archive script."*
  - Rejection: Manual copy-pasting risks breaking sequential numbering, precedence ordering, or omitting historical timestamps. Always use `scripts/archive_delta.py`.
- *"We should delete the change directory instead of archiving it."*
  - Rejection: Archiving preserves the complete historical trajectory and proposal context in `specs/archive/` for audits.
- *"We can archive the delta before the unit tests are green."*
  - Rejection: Only verified, implemented behaviors may be promoted into the living source of truth.

## Verification
Before completing this skill, verify the following evidence:
- [ ] `scripts/archive_delta.py` exited with status code 0.
- [ ] The target specification file exists and validates cleanly via `scripts/validate_spec.py`.
- [ ] Added rules appear under `## Rules` and within `## Precedence order`.
- [ ] The original change folder in `specs/changes/<change-id>/` no longer exists.
- [ ] The archived folder exists under `specs/archive/<timestamp>-<change-id>/`.
