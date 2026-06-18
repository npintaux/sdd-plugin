# Specification — Barista Agent

> **Source of truth.** GitHub Issues are intake; this file is the contract the
> agent obeys. When the two disagree, this file (and its owners) decide.

## Overview

Given a free-text spoken order and optional customer metadata, the Barista Agent returns a structured `Decision` to `MAKE` the order (and produce a priced kitchen ticket), `ASK` a single clarifying question for missing information, or politely `REFUSE` the order with a clear reason, evaluating declarative rules in a strict precedence order.

## Domain model

- **Request** — the input. Fields:
  - `order`: `str` — free-text customer order (e.g. `"medium oat latte"`).
  - `customer_allergies`: `list[str]` — list of customer's declared food allergies (e.g. `["nuts"]`).
- **Decision** — the output. Fields:
  - `action`: `str` — one of `MAKE`, `ASK`, `REFUSE`.
  - `ticket`: `dict` or `None` — the structured order details (populated only when action is `MAKE`):
    - `item`: `str` — matched menu item.
    - `size`: `str` — drink size.
    - `milk`: `str` — milk type.
  - `notes`: `list[str]` — clarifying questions (when `ASK`) or refusal reasons (when `REFUSE`), or general order comments.
  - `rule_ids`: `list[str]` — the stable rule IDs that determined this outcome.

## Global constraints

- **Determinism:** The decision evaluation is strictly deterministic. The same `Request` against the same menu and stock state must always yield the identical `Decision` (same `action`, `ticket`, `notes`, and `rule_ids`).
- **Single action:** Every evaluation must yield exactly one action: `MAKE`, `ASK`, or `REFUSE`.
- **Precedence resolution:** When an order needs both clarifying and could be made/refused, the agent must prioritize clarifying first (`ASK` precedence).
- **Rule citation:** Every decision must cite at least one active rule ID in the `rule_ids` list.

## Rules

### R2: Clarify Missing Attributes (ASK)

- **Behavior:** If a requested menu item is in stock, but is missing required attributes (such as size or milk type), the outcome is `ASK` with a clarifying question.
- **Example:** 
  `take_order(order="latte", customer_allergies=[])` 
  → `ASK`, `ticket=None`, `notes=["What size?"]`, `rule_ids=["R2"]`
- **Precedence:** Evaluated first. Overrides `R1` (MAKE) and `R3` (REFUSE).
- **Source:** Issue #1 (US1)

### R1: Valid Menu Item & In Stock (MAKE)

- **Behavior:** If the requested item is on the menu, currently in stock, and has all required attributes specified, the outcome is `MAKE`.
- **Example:** 
  `take_order(order="medium oat latte", customer_allergies=[])` 
  → `MAKE`, `ticket={"item": "latte", "size": "medium", "milk": "oat"}`, `notes=[]`, `rule_ids=["R1"]`
- **Precedence:** Defers to `R2` (ASK). Overrides `R3` (REFUSE).
- **Source:** Issue #1 (US1)

### R3: Catch-All Safe Default (REFUSE)

- **Behavior:** Any other request—such as off-menu items, items that are currently out of stock, or unrecognized gibberish—yields `REFUSE` with an explanatory note.
- **Examples:**
  * *Off-menu:* `take_order(order="unicorn frappe", customer_allergies=[])` 
    → `REFUSE`, `ticket=None`, `notes=["unicorn frappe is off-menu"]`, `rule_ids=["R3"]`
  * *Out of stock:* `take_order(order="large drip", customer_allergies=[])` (assuming drip coffee is marked out of stock) 
    → `REFUSE`, `ticket=None`, `notes=["large drip is out of stock"]`, `rule_ids=["R3"]`
- **Precedence:** Catch-all. Lowest priority.
- **Source:** Issue #1 (US1)

## Precedence order

Rules are evaluated as an ordered list where earlier rules win on conflicts:

1. `R2` — Clarify Missing Attributes (ASK)
2. `R1` — Valid Menu Item & In Stock (MAKE)
3. `R3` — Catch-All Safe Default (REFUSE)

## Glossary

- **MAKE** — Structured decision to approve the order and construct a kitchen ticket.
- **ASK** — Structured decision to request further information from the customer.
- **REFUSE** — Structured decision to decline processing the order.
- **Menu** — The canonical declaration of supported drinks (latte, drip, etc.) and their required attributes.
- **In Stock** — Real-time availability indicator of ingredients and drinks.
