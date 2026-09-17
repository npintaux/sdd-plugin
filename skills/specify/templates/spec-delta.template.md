# Delta: <change-id>
- **Capability**: <target-capability-or-root>
- **Source**: <issue-number-or-proposal>
- **Status**: draft | applied

## Context & Intent
<1-2 paragraphs summarizing the behavioral requirement or business rule changes, why they are needed, and business impact.>

## RENAMED Requirements
<!-- Optional: use when existing requirements are renamed to preserve history -->
- FROM: `### Requirement: <Old Name>`
- TO: `### Requirement: <New Name>`

## ADDED Requirements
### Requirement R<n>: <Requirement Title>
The system SHALL <precise normative statement conforming to RFC 2119>.

#### Scenario: <Scenario Name>
- **GIVEN** <initial state or precondition>
- **WHEN** <event triggered or evaluate(Request) called>
- **THEN** <expected observable result with rule_ids=["R<n>"]>
- **AND** <additional assertions or side-effects>

## MODIFIED Requirements
### Requirement R<existing-id>: <Existing Requirement Title Updated>
The system SHALL <updated normative statement>.

#### Scenario: <Updated Scenario Name>
- **WHEN** <updated condition>
- **THEN** <updated expected outcome>
- **Rationale**: <Why this requirement was modified>

## REMOVED Requirements
### Requirement R<existing-id>: <Deprecated Requirement Title>
- **Reason**: <Why this requirement is being superseded or deprecated>
- **Migration**: <Migration path for callers or dependents>

## Impact & Test Strategy
- **Affected Endpoints**: <list endpoints or interfaces>
- **New Unit Tests**: <list required unit test scenarios>

