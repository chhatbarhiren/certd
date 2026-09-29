# certd: Spec-Driven Development Workflow and SDLC

This document describes how the certd team builds software with
[GitHub Spec Kit](https://github.com/github/spec-kit) and Claude Code.

Interactive diagram: [sdlc-workflow.html](sdlc-workflow.html)
(source: [sdlc-workflow.json](sdlc-workflow.json)). Hover over or click any
step to see its activity and who does it. The step details live in
[add-step-details.py](add-step-details.py); rerun it after regenerating the
HTML with Archify.

Step-by-step checklists, prompts, and templates for each role are in
[PLAYBOOK.md](PLAYBOOK.md).

## Tooling

- **[GitHub Spec Kit](https://github.com/github/spec-kit)**: the `specify` CLI
  plus the templates, scripts, and `/speckit-*` skills that drive every stage.
  Install with `uv tool install specify-cli` (needs Python 3.11+ and `uv`).
  Docs: <https://github.github.io/spec-kit/>.
- **[Claude Code](https://www.anthropic.com/claude-code)**: the AI agent that
  runs the Spec Kit skills. Installed into the repo with
  `specify init --integration claude`.
- **Git and GitHub**: branches, PRs, CI, `CODEOWNERS`.

Full list with versions and install steps: [PLAYBOOK.md#tooling](PLAYBOOK.md#tooling).

## Team

The team is two people and one AI agent.

| Role | Type | Owns | Does not own |
|---|---|---|---|
| **Product Manager (PM)** | Human | Feature roadmap, feature specs (`spec.md`), prototype UI (`apps/web`), joint plan sign-off, product acceptance of the running feature | PR reviews and approvals, contract fit check, API, backend, CI, contract integration with the UI, any code outside the prototype |
| **Architect** | Human | Setup, constitution, `plan.md`, `data-model.md`, `contracts/`, backend (`apps/api`), `openapi.yaml`, contract fit check against the prototype, contract integration with the UI, joint plan sign-off, CI, all PR reviews and merges | Product intent, product acceptance |
| **Claude Code** | AI agent | Nothing. It runs the `/speckit-*` skills and writes artifacts and code for whichever person invoked it | Decisions, approvals, merges |

Rules for the AI agent:

- Each person runs their own Claude Code session on their own machine.
- Claude drafts; humans decide. Every artifact Claude writes is reviewed by
  its human owner before the next stage.
- Claude never approves a gate, merges a PR, or deploys.
- Agent-authored commits carry a `Co-Authored-By` trailer, and AI-generated PRs
  say so in the description.

## Feature roadmap

certd is a full product, not a demo. It is still built one feature at a
time, because Claude and the Spec Kit loop work best on small, bounded
features.

- The PM breaks the product into features and lists them in
  `specs/roadmap.md`, ordered so that features other features depend on come
  first (for example: accounts before billing).
- Each roadmap entry becomes one feature: one `specs/NNN-feature/` directory,
  one branch, one pass through the loop below.
- A **release** is whichever set of finished features the PM decides is ready
  to ship. The first release is simply the first such set.
- The roadmap is a living list. The PM adds, reorders, or drops features as
  the product evolves.

## Principles

- **One repo, one Spec Kit project at the repo root.** Each feature touches the
  UI and the API, so each feature gets one spec, one plan, one contract, and
  one branch.
- **Plan sign-off builds the shared mental model.** The PM and Architect
  review and approve each plan together, so both understand what will be
  built and how before any code exists.
- **The API contract is the handoff.** The PM and Architect agree the contract
  before either writes code that depends on it. After that, both sides build in
  parallel.
- **Spec Kit organizes the work. It does not guarantee quality.** Tests, CI,
  security scanning, and human review produce enterprise-grade code.

## Repository layout

```text
certd/
├── .specify/                  # constitution, templates, scripts (committed)
├── .claude/skills/            # speckit skills (committed)
├── .github/
│   ├── workflows/ci.yml       # test, lint, typecheck, contract test, CodeQL
│   └── CODEOWNERS
├── apps/
│   ├── api/
│   │   ├── openapi.yaml       # single source of truth for the API
│   │   ├── src/
│   │   └── tests/
│   └── web/
│       ├── src/api/           # client generated from openapi.yaml
│       └── tests/
└── specs/
    ├── roadmap.md
    └── 001-walking-skeleton/
        ├── spec.md            # PM owns
        ├── plan.md            # Architect owns
        ├── data-model.md
        ├── contracts/         # Architect owns and checks fit
        ├── quickstart.md
        └── tasks.md
```

`.specify/feature.json` (the current-feature pointer) is machine-local and is
already gitignored by Spec Kit.

## One-time setup (Architect)

Install [Spec Kit](https://github.com/github/spec-kit) first (see
[PLAYBOOK.md#install-each-person-once](PLAYBOOK.md#install-each-person-once)).

```bash
git init certd && cd certd
specify init --here --integration claude
mkdir -p apps/web apps/api
```

Then, in Claude Code:

```text
/speckit-constitution
```

Put these rules in the constitution:

- Layout: `apps/web` is the frontend; `apps/api` is the REST API.
- `apps/api/openapi.yaml` is the single source of truth for the API. The
  frontend never calls an endpoint that is not in it.
- Contract changes need Architect approval.
- Error format, authentication, API versioning, and required tests for each app.

`/speckit-plan` checks every plan against the constitution.

Add `.github/CODEOWNERS`:

```text
*                       @architect
```

Enable branch protection on `main`: require CI to pass and require CODEOWNERS
review. The Architect reviews and merges every PR, including the PM's spec
and prototype changes. The PM never approves PRs.

## SDLC stages

| Stage | Owner | Claude runs | Output | Exit gate |
|---|---|---|---|---|
| 0. Setup | Architect | `specify init`, `/speckit-constitution` | `.specify/`, `.claude/skills`, constitution, CI, `CODEOWNERS` | The walking skeleton builds and deploys |
| 1. Planning | PM | Feature roadmap ([spec of specs](https://github.github.io/spec-kit/concepts/spec-of-specs.html)). Optional: `assess` extension | `specs/roadmap.md` | Features are ordered by dependency |
| 2. Requirements | PM | `/speckit-specify`, `/speckit-clarify` | `specs/NNN-x/spec.md` on branch `NNN-x` | The Architect has read the spec. No open questions remain |
| 3. Design | Architect | `/speckit-plan` | `plan.md`, `data-model.md`, `contracts/`, `quickstart.md` | Architect confirms the contract covers every prototype screen |
| 3a. Plan sign-off | PM + Architect, together | None | Approved `plan.md` and `contracts/` | **Both approve the plan** |
| 3b. Breakdown | Architect | `/speckit-tasks`, `/speckit-analyze` | `tasks.md` | No gaps between spec, plan, and tasks |
| 4. Development | PM: prototype UI. Architect: API. In parallel | `/speckit-implement` scoped by path | Prototype UI, API code and tests | Unit and contract tests pass locally |
| 5. Integration and testing | Architect | Integrate contract with UI, `/speckit-converge` | Working feature, end to end | CI is green, converge reports **Converged**, PM accepts the running feature |
| 6. Release | CI/CD | None | Deployed build | Smoke tests pass and a rollback path exists |
| 7. Maintenance | Whoever finds the issue | `bug` extension | `.specify/bugs/<slug>/` | The verdict is `verified` |

## Per-feature loop

1. **PM:** run `/speckit-specify <feature and UI flow>`, then
   `/speckit-clarify`. Spec Kit creates the `NNN-feature` branch and
   `specs/NNN-feature/spec.md`. Push the branch.
2. **Architect:** run `/speckit-plan` with a hint such as
   `Web app layout: apps/web + apps/api; REST contract in contracts/openapi.yaml`.
3. **Contract fit check (Architect):** the Architect checks the contract
   against the PM's prototype: every screen and flow has the endpoints and
   fields it needs. If something is missing, the Architect revises the plan.
   Nobody writes code against the contract until it fits. The PM is only asked
   when the prototype's intent is unclear.
4. **Plan sign-off (PM + Architect, together):** a short walkthrough of
   `plan.md`, `data-model.md`, and `contracts/`. This is where the shared
   mental model is built.
   - The PM checks product fit: the plan delivers every user story in
     `spec.md`, scope and trade-offs are acceptable, and nothing changes the
     intended user experience.
   - The Architect checks technical fit: constitution rules, data model,
     contract, risks.
   - Both must approve. If either one objects, the Architect revises the plan
     (or the PM revises `spec.md`) and they review again.
   - Record the approval in the feature's `plan.md`, for example
     `Approved by: PM, Architect (YYYY-MM-DD)`.

   This is a plan review, not a code review. It is separate from PR approval,
   which stays with the Architect.
5. **Architect:** run `/speckit-tasks`, then `/speckit-analyze`.
6. **In parallel, on the same feature branch:**
   - Architect: `/speckit-implement only tasks under apps/api`
   - PM (prototype only): `/speckit-implement only tasks under apps/web; call the API through a mock until endpoints exist`

   Pull and rebase often. Both sessions tick boxes in `tasks.md`, so small
   merge conflicts there are expected.
7. **Architect, contract integration with the UI:** merge the feature's
   `contracts/` into `apps/api/openapi.yaml`, regenerate the typed client in
   `apps/web/src/api/`, switch the prototype from the mock to the real API,
   and run `/speckit-converge` until it reports **Converged**.
8. **Pull request:** CI must pass. The Architect reviews and merges. The PM
   does not review the PR. Instead, the PM tries the running feature (local
   run, preview, or staging) and accepts it against the acceptance criteria in
   `spec.md`. This is a product check, not a code review.

Start with feature `001-walking-skeleton`: one screen, one endpoint, and one
entity, end to end. It proves the loop and the layout before real features.

## Gates

| Gate | Blocks | Enforced by |
|---|---|---|
| Constitution check | A plan that breaks project rules | `/speckit-plan` |
| Contract fit | Code written before the API covers the prototype | Architect checks every prototype screen and flow |
| Plan sign-off | Building before both people share the same understanding | PM and Architect approve the plan together |
| Convergence | Code that does not match the spec | `/speckit-converge` |
| CI | Broken or unsafe code | Tests, lint, type checks, contract tests, CodeQL, Dependabot |
| Human review | Unreviewed changes | Architect review via `CODEOWNERS` and branch protection |

## Paths for different kinds of work

| Work | Path |
|---|---|
| New feature | Full loop, stages 2 to 6 |
| Change to an existing feature | Edit `spec.md`, then rerun `/speckit-plan` and `/speckit-tasks`. Contract or plan changes go back through the contract fit check and plan sign-off |
| Bug | `specify extension add bug`, then `/speckit-bug-assess`, `/speckit-bug-fix`, `/speckit-bug-test` |
| Tiny tweak or copy fix | A plain PR. CI and review still apply |
| Uncertain idea | `specify extension add assess` first. Specify only if the verdict is `go` |

## Speed and quality expectations

- **Speed:** the first one or two features are slower than prompting Claude
  directly, because specs, plans, and contract reviews come first. After that,
  delivery is faster: less rework, parallel frontend and backend work, and
  specs that keep context between sessions.
- **Quality:** Spec Kit gives written requirements, an agreed contract,
  consistent rules, and traceability. It does not replace tests, CI, security
  scanning, operations work, or human review. Code quality depends on how
  strict the constitution is, which CI gates exist, review discipline, and
  keeping features small.

## Recommended tools outside Spec Kit

- A typed frontend client generated from `openapi.yaml` (for example
  `openapi-typescript`), so API mismatches fail at compile time.
- A mock server driven by the same file (for example Prism), so the PM can
  build UI before the API exists.
- Logging, metrics, error tracking, database migrations, and a deploy and
  rollback pipeline.

## Cadence

- **Per feature:** a few days to a week. Keep features small; Claude works worse
  on large features.
- **Weekly:** the PM updates the roadmap. The Architect reviews contracts for
  upcoming features.
- **As needed:** when a rule keeps getting broken, update the constitution and
  add a CI check for it.

## References

- [GitHub Spec Kit repository](https://github.com/github/spec-kit)
- [Spec Kit quickstart](https://github.github.io/spec-kit/quickstart.html)
- [Contract-driven development](https://github.github.io/spec-kit/guides/contract-driven-development.html)
- [Monorepo guide](https://github.github.io/spec-kit/guides/monorepo.html)
- [Handling complex features](https://github.github.io/spec-kit/concepts/complex-features.html)
- [Spec persistence models](https://github.github.io/spec-kit/concepts/spec-persistence.html)
