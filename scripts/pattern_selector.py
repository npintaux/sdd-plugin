#!/usr/bin/env python3
"""
scripts/pattern_selector.py

Unified Pattern Recommendation Engine.
Analyzes natural language task descriptions, user stories, or requirements
and recommends both:
1. Domain Computational Pattern (from Maestro catalog)
2. Agentic Control & Safety Patterns (from Antonio Gulli's 21 Agentic Design Patterns)

Adheres to Agent Skills script hygiene:
- Recommends structured payload to stdout.
- Operational logs/errors to stderr.
- Exits 0 on success, 1 on invalid input.
"""

import argparse
import json
import re
import sys
from typing import Any, Dict, List, Tuple


DOMAIN_PATTERNS = {
    "decision-list": {
        "name": "decision-list",
        "description": "Request-in / decision-out with boolean predicates (Rule(ABC) + engine.py)",
        "best_for": ["validation", "policy", "underwriting", "fraud screening", "pricing rules", "gatekeeping", "eligibility"],
        "keywords": ["rule", "policy", "eligibility", "approve", "deny", "evaluate", "underwrite", "compliance", "filter"]
    },
    "repository-service": {
        "name": "repository-service",
        "description": "Key-value lookup, query, or CRUD (Repository(ABC) + service.py)",
        "best_for": ["metadata lookups", "database operations", "key-value stores", "entity management", "caching"],
        "keywords": ["crud", "database", "query", "lookup", "store", "fetch", "record", "repository", "get", "put", "save"]
    },
    "state-machine": {
        "name": "state-machine",
        "description": "Event-driven state transitions (State, Event, TransitionTable, StateMachine(ABC))",
        "best_for": ["order lifecycles", "booking flows", "multi-step sagas", "approval workflows"],
        "keywords": ["lifecycle", "state", "transition", "workflow", "order", "status", "stage", "step", "pending", "active"]
    },
    "pipeline-reducer": {
        "name": "pipeline-reducer",
        "description": "Stream transformation or accumulating calculation (PipelineStage(ABC) + pipeline.py)",
        "best_for": ["stream aggregation", "IoT telemetry", "stacked calculators", "data normalization"],
        "keywords": ["stream", "telemetry", "aggregate", "metric", "pipeline", "transform", "reduce", "series", "sensor", "iot"]
    },
    "algorithmic-core": {
        "name": "algorithmic-core",
        "description": "Cohesive algorithmic computation (Solver(ABC) or Strategy(ABC))",
        "best_for": ["routing (Dijkstra)", "graph traversal", "AST parsing", "compilers", "ML inference scoring"],
        "keywords": ["algorithm", "solve", "graph", "dijkstra", "optimize", "tree", "compiler", "score", "path", "matrix"]
    }
}


GULLI_PATTERNS = {
    "prompt-chaining": {
        "tier": "Tier 1: Core",
        "chapter": 1,
        "name": "Prompt Chaining",
        "intent": "Decompose linear sequential tasks into step-by-step prompt pipelines",
        "keywords": ["chain", "sequential", "step-by-step", "pipeline", "linear", "multi-step"]
    },
    "routing": {
        "tier": "Tier 1: Core",
        "chapter": 2,
        "name": "Routing",
        "intent": "Dynamically direct incoming requests to specialized persona agents or handlers",
        "keywords": ["route", "classify", "categorize", "intent", "dispatch", "branch", "direct to"]
    },
    "parallelization": {
        "tier": "Tier 1: Core",
        "chapter": 3,
        "name": "Parallelization",
        "intent": "Execute concurrent sub-queries simultaneously (Sectioning or Voting)",
        "keywords": ["parallel", "concurrent", "fan-out", "vote", "section", "simultaneous"]
    },
    "reflection": {
        "tier": "Tier 1: Core",
        "chapter": 4,
        "name": "Reflection",
        "intent": "Iterative self-critique and feedback-driven refinement loop",
        "keywords": ["reflection", "critique", "review", "evaluate output", "self-correct", "revise", "audit output"]
    },
    "tool-use": {
        "tier": "Tier 1: Core",
        "chapter": 5,
        "name": "Tool Use",
        "intent": "Enable LLM agents to call external APIs, databases, code execution sandboxes, or search",
        "keywords": ["tool", "api", "function calling", "database", "calculator", "search", "web", "external"]
    },
    "planning": {
        "tier": "Tier 1: Core",
        "chapter": 6,
        "name": "Planning",
        "intent": "Dynamic goal decomposition, execution tracking, and adaptive replanning",
        "keywords": ["plan", "replan", "autonomous", "milestone", "goal decomposition", "strategy"]
    },
    "multi-agent": {
        "tier": "Tier 1: Core",
        "chapter": 7,
        "name": "Multi-Agent Collaboration",
        "intent": "Coordinate specialized persona subagents via hierarchical or swarm communication",
        "keywords": ["multi-agent", "swarm", "team", "coordinator", "hierarchy", "collaborate", "personas"]
    },
    "memory-management": {
        "tier": "Tier 2: Advanced",
        "chapter": 8,
        "name": "Memory Management",
        "intent": "Maintain short-term, long-term, episodic, or semantic state across sessions",
        "keywords": ["memory", "session", "persistent state", "history", "recall", "store state"]
    },
    "mcp": {
        "tier": "Tier 2: Advanced",
        "chapter": 10,
        "name": "Model Context Protocol (MCP)",
        "intent": "Standardize cross-system tool and resource interfaces via JSON-RPC",
        "keywords": ["mcp", "model context protocol", "json-rpc", "tool server", "external server"]
    },
    "exception-handling": {
        "tier": "Tier 3: Production",
        "chapter": 12,
        "name": "Exception Handling & Recovery",
        "intent": "Provide fallback models, retry mechanisms, and graceful degradation paths",
        "keywords": ["fallback", "retry", "exception", "degrade", "error recovery", "timeout", "circuit breaker"]
    },
    "human-in-the-loop": {
        "tier": "Tier 3: Production",
        "chapter": 13,
        "name": "Human-in-the-Loop",
        "intent": "Enforce interactive approval gates before irreversible or sensitive mutations",
        "keywords": ["hitl", "human", "approval", "escalate", "confirm", "permission", "gate"]
    },
    "rag": {
        "tier": "Tier 3: Production",
        "chapter": 14,
        "name": "Knowledge Retrieval (RAG)",
        "intent": "Ground agent responses in proprietary vector databases or document indices",
        "keywords": ["rag", "retrieval", "vector", "embedding", "grounding", "documents", "knowledge base"]
    },
    "guardrails": {
        "tier": "Tier 4: Enterprise",
        "chapter": 18,
        "name": "Guardrails & Safety",
        "intent": "Sanitize inputs against prompt injection and filter outputs for PII and safety",
        "keywords": ["guardrail", "safety", "sanitize", "injection", "jailbreak", "pii", "redact", "filter"]
    }
}


def score_domain_pattern(desc: str) -> Tuple[str, Dict[str, Any], int, List[str]]:
    desc_lower = desc.lower()
    best_pattern = "decision-list"
    best_score = 0
    best_matches: List[str] = []
    
    for key, data in DOMAIN_PATTERNS.items():
        matched = [kw for kw in data["keywords"] if re.search(rf"\b{re.escape(kw)}\b", desc_lower)]
        score = len(matched)
        if score > best_score:
            best_score = score
            best_pattern = key
            best_matches = matched
            
    return best_pattern, DOMAIN_PATTERNS[best_pattern], best_score, best_matches


def score_agentic_patterns(desc: str) -> Tuple[List[Dict[str, Any]], bool]:
    desc_lower = desc.lower()
    matches: List[Tuple[int, Dict[str, Any], List[str]]] = []
    
    for data in GULLI_PATTERNS.values():
        matched = [kw for kw in data["keywords"] if re.search(rf"\b{re.escape(kw)}\b", desc_lower)]
        score = len(matched)
        if score > 0:
            pattern_info = dict(data)
            pattern_info["matched_keywords"] = matched
            matches.append((score, pattern_info, matched))
            
    # Sort by relevance score descending
    matches.sort(key=lambda x: x[0], reverse=True)
    
    # Return top 4 matched agentic patterns, or default to Tool Use + Guardrails if none
    if not matches:
        return [GULLI_PATTERNS["tool-use"], GULLI_PATTERNS["guardrails"]], True
    return [item[1] for item in matches[:4]], False


def recommend(description: str) -> Dict[str, Any]:
    dom_key, dom_data, dom_score, dom_matches = score_domain_pattern(description)
    agentic, agentic_is_default = score_agentic_patterns(description)
    
    confidence = "high" if dom_score >= 2 else ("low" if dom_score == 1 else "none")
    
    return {
        "domain_pattern": {
            "key": dom_key,
            "name": dom_data["name"],
            "description": dom_data["description"],
            "relevance_score": dom_score,
            "confidence": confidence,
            "is_fallback": dom_score == 0,
            "matched_keywords": dom_matches
        },
        "agentic_patterns": agentic,
        "agentic_is_fallback": agentic_is_default,
        "composition_guidance": "Combine the primary Domain Pattern for core logic with selected Agentic Patterns for control & safety."
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Recommend Domain and Agentic patterns from task description.")
    parser.add_argument("task", nargs="?", type=str, help="Natural language description of the task.")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    
    args = parser.parse_args()
    
    if args.task:
        desc = args.task
    else:
        desc = sys.stdin.read().strip()
        
    if not desc:
        sys.stderr.write("Error: Task description cannot be empty.\n")
        sys.exit(1)
        
    result = recommend(desc)
    
    if args.json:
        sys.stdout.write(json.dumps(result, indent=2) + "\n")
    else:
        sys.stdout.write("=================================================================\n")
        sys.stdout.write("           UNIFIED PATTERN SELECTION RECOMMENDATION              \n")
        sys.stdout.write("=================================================================\n\n")
        dom = result['domain_pattern']
        fallback_str = " [FALLBACK DEFAULT — 0 keywords matched, review carefully]" if dom['is_fallback'] else f" (confidence: {dom['confidence']}, matched: {', '.join(dom['matched_keywords'])})"
        sys.stdout.write(f"1. DOMAIN COMPUTATIONAL PATTERN:\n")
        sys.stdout.write(f"   Pattern:     {dom['name']}{fallback_str}\n")
        sys.stdout.write(f"   Description: {dom['description']}\n")
        if dom['is_fallback']:
            sys.stdout.write("   Note:        No domain keywords matched. Review whether state-machine, repository, or pipeline better fits your use case.\n\n")
        else:
            sys.stdout.write("\n")
            
        sys.stdout.write(f"2. AGENTIC DESIGN PATTERNS (Antonio Gulli Catalog):\n")
        if result.get('agentic_is_fallback'):
            sys.stdout.write("   Note:        No agentic triggers matched. Providing baseline control patterns (Tool Use + Guardrails).\n")
        for p in result['agentic_patterns']:
            kw_hint = f" [matched: {', '.join(p['matched_keywords'])}]" if "matched_keywords" in p else ""
            sys.stdout.write(f"   - [{p['tier']}] Ch {p['chapter']}: {p['name']}{kw_hint}\n")
            sys.stdout.write(f"     Intent: {p['intent']}\n")
        sys.stdout.write("\n3. COMPOSITION GUIDANCE:\n")
        sys.stdout.write(f"   {result['composition_guidance']}\n")
        sys.stdout.write("=================================================================\n")
        
    sys.exit(0)


if __name__ == "__main__":
    main()
