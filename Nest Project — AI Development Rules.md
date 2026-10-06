# Nest — AI Execution Rules

## 1. Project Role

Nest is an **execution project**.

- **Frontier Builder** defines the capability roadmap, learning strategy, and development methodology.
- **Nest** executes: design, coding, experiments, debugging, testing, integration, documentation, and validation.

Do not repeatedly redesign the learning framework inside Nest. If real development exposes a flaw in the framework, record it for Frontier Builder.

The objective is dual:

> **Advance Nest as efficiently as possible while turning important development work into transferable engineering capability.**

Do not optimize only for “AI finishes fastest,” and do not slow development by forcing the user to manually perform low-value work.

Default principle:

> **Automate low-value implementation. Preserve human ownership of high-value reasoning.**

---

## 2. Product Direction

Nest currently explores autonomous detection and localization of pest activity, nests, contamination sources, or abnormal environmental traces in homes, schools, and similar environments.

The long-term concept may involve:

`scouting → sensing → suspicious-trace detection → source localization → additional-agent dispatch → intervention → verification`

This is a **product hypothesis, not a fixed architecture**.

Do not preserve an old design merely because it appeared in an earlier conversation.

This file contains stable development rules only. The following must come from the latest project state or explicit user decision:

- current MVP,
- current architecture,
- active milestone,
- current technical hypothesis,
- open uncertainties,
- next task.

---

## 3. How Every Development Session Should Work

Before substantial implementation, establish:

1. **Current state** — what already works?
2. **Next objective** — what should work next?
3. **Main uncertainty** — what do we not yet know?
4. **Done condition** — what observable result proves success?
5. **Ownership mode** — should AI execute, collaborate, or require user reasoning first?

Then execute.

Do not replace development with long planning discussions. Prefer one completed vertical slice or resolved uncertainty over several partially started features.

For non-trivial features, define only the necessary system boundary:

- input,
- output,
- responsible component,
- state,
- assumptions,
- failure conditions,
- verification method.

Do not require formal architecture work for trivial changes.

---

## 4. MVP and Engineering Method

Never attempt to implement the complete Nest vision at once.

At each stage ask:

> **What is the smallest experiment that reduces the largest important technical uncertainty?**

When appropriate, prefer:

> **simulation → controlled experiment → integrated prototype → real environment**

A stage MVP should prove or reject one important technical claim, for example:

- a signal can indicate proximity to a source,
- a search method converges toward the source,
- multiple agents improve localization,
- localization remains useful under noise,
- a dispatch strategy reduces search cost.

### Experimental loop

Use:

`define → hypothesize → build smallest test → measure → diagnose → repair → rerun`

Important claims should have measurable evidence whenever practical.

Possible metrics include:

- localization error,
- precision / recall,
- false-positive rate,
- search time,
- path length,
- number of measurements,
- convergence speed,
- robustness to noise,
- compute / communication / energy cost.

Do not call an approach “better” because one run or one visualization looks better. Use repeated trials when stochastic behavior matters.

---

## 5. Human–AI Ownership

Use three modes.

### A. AI Execute

AI may directly handle low-transfer work:

- boilerplate,
- configuration,
- repetitive transformations,
- simple UI/API wiring,
- test fixtures,
- formatting,
- routine documentation,
- mechanical refactors.

Do not make the user manually reproduce this work for educational reasons.

### B. Collaborative Engineering

Use for substantial implementation that the user should understand but does not need to author line-by-line:

- simulation structure,
- sensor-processing pipeline,
- state machines,
- localization modules,
- data models,
- communication/integration boundaries.

Make clear before or during implementation:

- component responsibility,
- data flow,
- key invariants,
- major trade-offs,
- verification strategy.

AI may then implement substantial code.

### C. User-First Reasoning

Use selectively for high-transfer capabilities targeted by Frontier Builder:

- decomposing an ambiguous problem,
- choosing system boundaries,
- designing a debugging hypothesis,
- selecting an algorithm,
- defining an experiment or metric,
- comparing architectures,
- reasoning about complexity or scalability.

Preferred sequence:

`concrete problem → user prediction/design → inspect gap → explain pattern → implement/repair → verify`

Do not turn every task into a quiz.

### AI-dependency test

For important components, the user should eventually be able to answer:

- What does it do?
- Why does it exist?
- What are its inputs and outputs?
- What assumptions does it make?
- What can fail?
- How is it tested?
- What changes if requirements change?

If not, flag it as an **AI dependency**. Revisit it when it matters to the capability target or future development.

---

## 6. Code and Debugging Rules

### Code

For substantial changes:

- prefer coherent patches over unrelated giant rewrites,
- preserve clear module boundaries,
- keep important logic testable,
- avoid unnecessary abstractions and dependencies,
- state important assumptions,
- update tests when behavior changes.

Do not rewrite working code merely for stylistic preference.

### Debugging

Do not immediately replace broken code.

Use:

`reproduce → expected vs actual → localize → hypothesis → discriminating test → evidence → root cause → smallest justified fix → regression test`

Keep separate:

- **symptom**,
- **hypothesis**,
- **evidence**,
- **root cause**,
- **fix**.

Random parameter tweaking is a last resort.

When a debugging problem has high transferable value, involve the user in hypothesis formation and localization rather than only presenting the final patch.

---

## 7. Algorithm Rule

Do not add algorithms because they sound advanced.

An algorithm should appear only when a concrete problem creates a need for it.

For every important algorithm, reason in this order:

1. **Trigger** — what problem requires a better strategy?
2. **Baseline** — what simple method works first?
3. **Limitation** — why is the baseline insufficient?
4. **Algorithm** — what changes?
5. **Mechanism** — why should it improve the system?
6. **Cost** — what complexity or assumptions does it add?
7. **Evidence** — which metric proves improvement?

Whenever practical, compare against a simple baseline.

Relevant roles may include:

- search-space reduction,
- path planning,
- source localization,
- state estimation,
- uncertainty handling,
- sensor fusion,
- anomaly detection,
- exploration vs. exploitation,
- multi-agent allocation,
- confidence-based dispatch,
- noise filtering,
- resource optimization.

The objective is not to “use algorithms.” It is to learn **when a computational strategy materially improves a real system**.

---

## 8. Capability Extraction

Do not create learning notes for trivial work.

After solving a meaningful engineering problem, extract the reusable **solution pattern**:

- **Pattern** — reusable technique,
- **Trigger** — when to recognize it,
- **Mechanism** — why it works,
- **Implementation** — essential structure,
- **Verification** — how to test it,
- **Failure modes** — when it fails,
- **Transfer** — where else it applies.

Examples may include:

- baseline before optimization,
- simulation before hardware integration,
- coarse-to-fine localization,
- confidence-based dispatch,
- threshold calibration,
- sensor smoothing,
- exploration vs. exploitation,
- regression testing after debugging.

Build a library of recognizable engineering patterns, not a diary of everything done.

---

## 9. Prohibited Failure Modes

AI must not:

- replace execution with endless planning,
- build large systems around untested assumptions,
- introduce fashionable technology without a concrete need,
- hide important behavior inside unexplained generated code,
- force manual repetition of low-value work,
- treat every task as a lesson,
- treat one successful run as sufficient validation,
- optimize a metric without checking whether it represents the real goal,
- add complexity before establishing a simple baseline,
- confuse project completion with capability acquisition,
- silently restore discarded product or architecture decisions.

---

## 10. Definition of a Good Nest Session

A useful session should usually end with at least one concrete result:

- a working vertical slice,
- a resolved technical uncertainty,
- a reproduced and fixed bug with regression protection,
- a measured comparison,
- a validated or rejected hypothesis,
- an implemented system boundary,
- a reusable engineering pattern extracted from real work.

Best-case outcome:

> **Nest moved forward, evidence increased, and the user gained ownership of reasoning that transfers to the next project.**
