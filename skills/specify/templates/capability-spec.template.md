# Specification: <Capability Name>
> **Status**: Living Behavior Contract  
> **Capability**: specs/<capability>/spec.md  
> **Selected Domain Pattern**: `<decision-list | repository-service | state-machine | pipeline-reducer | algorithmic-core>`  
> **Selected Agentic Patterns**: `<None | Tool Use | Reflection | Routing | Guardrails>`  

## Purpose
<High-level narrative describing what this capability does, who it serves, and its boundary in the macro-architecture.>

## Domain model

### Request
```python
@dataclass(frozen=True)
class <Capability>Request:
    <field_1>: <type>
    <field_2>: <type>
```

### Decision / Outcome
```python
@dataclass(frozen=True)
class <Capability>Decision:
    outcome: <OutcomeEnum>
    rule_ids: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)
```

## Global constraints
- Invariants that hold across all requirements and operations (e.g. non-null constraints, budget ceilings).

## Requirements

### Requirement R<n>: <Requirement Title>
The system SHALL <precise normative statement conforming to RFC 2119>.

#### Scenario: <Primary Success Scenario>
- **GIVEN** <initial state or precondition>
- **WHEN** <event triggered or evaluate(Request) called>
- **THEN** <expected observable result with rule_ids=["R<n>"]>
- **AND** <additional assertions or side-effects>

#### Scenario: <Edge Case / Failure Scenario>
- **WHEN** <exceptional input condition>
- **THEN** <expected error outcome or fallback behavior>

## Precedence order
1. R<n> — <Requirement Title>

## Glossary
- **<term>**: <definition>

