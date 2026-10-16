---
name: pm-po-product-discovery
description: "Use when shaping a wallet reconciliation product need into a validated problem statement, user story, acceptance criteria, product specification, or prioritized backlog item; verify behavior against the project's code, tests, and SDD."
argument-hint: "Describe the product need, user problem, or candidate finding to shape."
---

# PM/PO Product Discovery

Use this workflow to turn a product need for the Peru wallet reconciliation MVP into clear, evidence-based requirements. The output defines product behavior and verification, not technical design or implementation.

## When to use

- Clarify a product request, user problem, opportunity, or confirmed finding.
- Draft or refine user stories, functional requirements, acceptance criteria, or backlog items.
- Prepare a product specification for human review and a possible later handoff to Architect.
- Analyze whether a proposed change alters the current reconciliation behavior, reports, metrics, or investigation workflow.

## Workflow

### 1. Establish the evidence

Read only the relevant files, using this precedence:

1. `backend/app/`, `frontend/src/`, and relevant tests under `backend/tests/` to verify implemented behavior.
2. `docs/sdd/conciliacion-operativa/spec.md` and `docs/sdd/conciliacion-operativa/design.md` for documented functional behavior and design; verify claims against code and tests.
3. `docs/sdd/conciliacion-operativa/proposal.md`, `docs/sdd/conciliacion-operativa/tasks.md`, and `README.md` for product intent, delivered scope, and proposed backlog.

Check the relevant end-to-end surfaces. For example, a change to discrepancy classification may affect reconciliation rules, report schemas, daily-summary calculations, UI display, and tests. Do not claim a surface is affected without evidence.

For every material statement, label it as one of:

- **Implemented** — confirmed in code and, where available, tests.
- **Documented** — stated in the SDD but not independently confirmed.
- **Proposed** — requested or listed as future work, not implemented.
- **Open** — evidence or product decision is insufficient.

If sources conflict, report the conflict and cite their exact repository-relative paths. Do not silently treat older proposal language or a backlog entry as current behavior.

### 2. Frame the product need

Capture:

- affected user or operational role, only if supported by the request or project evidence;
- problem or opportunity;
- desired user or business outcome;
- observable scope and exclusions;
- constraints, dependencies, and confirmed findings.

Separate facts, requirements, assumptions, and open questions. Do not invent business policies, financial rules, SLAs, thresholds, priorities, actors, or workflows. Where an assumption would change financial classification, state transitions, metrics, API/UI behavior, or scope, leave it as a decision for the product owner.

### 3. Draft verifiable requirements

Write a concise user story where useful:

> Como [usuario respaldado por la evidencia], quiero [capacidad], para [resultado observable].

Then define acceptance criteria that are:

- observable and testable by a user, API response, report, or test;
- explicit about relevant conditions, inputs, outcomes, and errors;
- consistent with the current product terminology and metric definitions;
- clear about behavior before and after any proposed threshold or state transition.

Use Given/When/Then when it improves clarity. Include negative, boundary, and unaffected behavior where relevant. Do not turn an unresolved assumption into a definite criterion. Mark candidate criteria that depend on an open decision.

For reconciliation changes, explicitly assess relevant effects on source ingestion, matching, discrepancy types, investigation states, date/channel runs, per-run reports, daily summaries, and dashboard behavior. Preserve current behavior unless the approved request explicitly changes it.

### 4. Identify decisions and approval state

List only the questions that block unambiguous requirements or acceptance. For each, explain briefly what product behavior depends on the answer. Do not answer a product-policy question by selecting a technical implementation.

Keep the status explicit:

- **Draft / not approved** until a responsible human confirms the scope and acceptance criteria.
- Product approval does not approve architecture or authorize implementation.
- If essential product decisions remain open, recommend resolving them before architecture review.

### 5. Handle artifacts and handoff safely

- If there is an active OpenSpec change and the team is using OpenSpec, place product artifacts only in the active change's established structure. If the request asks to create or update OpenSpec artifacts, follow the repository's OpenSpec workflow.
- Otherwise, present the proposal in the conversation. Do not create files, modify the canonical SDD, or initialize OpenSpec as a side effect.
- Create or update GitHub issues only when explicitly requested or approved. Search for duplicates first and use the repository that owns the work.
- Do not edit application code, tests, agent/skill configuration, or technical architecture as part of product discovery.
- Prepare a handoff to Architect only after human approval of the product scope and criteria. Include the approved requirements, evidence, affected contracts/surfaces, open technical questions, and expected test outcomes; do not send it automatically.

## Output format

Adapt detail to the request. Include the relevant sections:

1. **Contexto y evidencia** — current behavior, evidence labels, and repository-relative paths.
2. **Problema y resultado esperado** — affected user, need, and outcome.
3. **Historia o requisitos** — proposed product behavior.
4. **Criterios de aceptación** — testable scenarios, with unresolved assumptions marked.
5. **Alcance** — included, excluded, and product dependencies.
6. **Decisiones abiertas** — decisions needed and why they matter.
7. **Estado y siguiente gate** — approval status and the next responsible review.

Do not claim files were changed, tests were run, issues were created, or approvals were obtained unless that actually happened.
