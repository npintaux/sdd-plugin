# System Architecture Specification

## Executive Summary
<Brief description of the system purpose, high-level capabilities, and operational context.>

## Domain Boundaries & Subsystems
| Subsystem | Directory | Primary Pattern | Agentic Patterns | Responsibility |
|---|---|---|---|---|
| `<subsystem-1>` | `src/modules/<subsystem-1>/` | `decision-list` | `Guardrails, Tool Use` | <Core responsibility> |
| `<subsystem-2>` | `src/modules/<subsystem-2>/` | `state-machine` | `HITL, Memory` | <Lifecycle workflow> |

## Pattern Catalog Mapping (Antonio Gulli 21 Patterns)
- **Execution Layer**:
  - `Tool Use`: Standardized tools conforming to MCP / typed schema.
  - `Reflection`: Self-critique and validation loops.
- **Control & Routing Layer**:
  - `Routing`: Intent classification and dispatch.
  - `Planning`: Goal decomposition and dynamic replanning.
- **Safety & Quality Layer**:
  - `Guardrails`: Input sanitization and prompt injection defense.
  - `Human-in-the-Loop`: Explicit approval checkpoints before state mutations.
- **Operational Layer**:
  - `Memory Management`: Session and episodic persistence.
  - `Exception Handling & Recovery`: Graceful degradation and fallback routes.

## Framework Selection & Rationale
- **Primary Runtime**: Google GenAI SDK / Google ADK / LangGraph / Native Python
- **Rationale**: <Explain why selected runtime satisfies latency, typing, and dependency constraints.>

## Cloud Architecture & Well-Architected Framework (WAF)
- **Compute**: Cloud Run / GKE / Functions
- **Data Persistence**: Firestore / Cloud SQL / Cloud Storage
- **Perimeter & Security**: Cloud Armor, Secret Manager, IAM Least Privilege

## Architecture Decision Records (ADRs)
- [ADR-0001: Compute Selection](docs/adr/0001-compute.md)
- [ADR-0002: Datastore Selection](docs/adr/0002-datastore.md)
