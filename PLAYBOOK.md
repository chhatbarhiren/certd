# certd Playbook

Step-by-step run-sheet for the certd team. For the overview and the reasons
behind each step, see [WORKFLOW.md](WORKFLOW.md).

This is a first version, written before the first feature. Update it after
features `001` and `002` with what actually went wrong (see
[Known issues](#known-issues)).

## Tooling

| Tool | Used by | Purpose |
|---|---|---|
| [GitHub Spec Kit](https://github.com/github/spec-kit) (`specify` CLI) | Architect installs; both use its skills | Spec-Driven Development: templates, scripts, and the `/speckit-*` skills |
| [Claude Code](https://www.anthropic.com/claude-code) | PM and Architect, one session each | Runs the `/speckit-*` skills and writes specs, plans, and code |
| Python 3.11+ and [uv](https://docs.astral.sh/uv/) | Both | Required to install and run `specify` |
| Git and GitHub | Both | Repository, feature branches, PRs, CI, `CODEOWNERS` |
| Node.js | Both | Frontend tooling and `openapi-typescript` |
| [openapi-typescript](https://openapi-ts.dev/) | Architect | Generates the typed UI client from `openapi.yaml` |
| [Prism](https://stoplight.io/open-source/prism) (optional) | PM | Mock API from the contract, so the prototype works before the API exists |

Spec Kit documentation: <https://github.github.io/spec-kit/>. Spec Kit commands
used below are described in its
[command reference](https://github.github.io/spec-kit/reference/agentic-sdd.html).

### Install (each person, once)

```bash
uv tool install specify-cli          # from PyPI
specify version                      # confirm it is installed
```

To pin a release from the GitHub repository instead:

```bash
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git@vX.Y.Z
```

Both people should use the same Spec Kit version. Record it in the repo
README and upgrade together
([upgrade guide](https://github.github.io/spec-kit/upgrade.html)).

## Project setup (Architect, once)

1. Create the repository and initialize Spec Kit for Claude:

   ```bash
   git init certd && cd certd
   specify init --here --integration claude
   mkdir -p apps/web apps/api
   ```

2. Add the plan sign-off and contract fit sections to every future plan:

   ```bash
   mkdir -p .specify/templates/overrides
   cp .specify/templates/plan-template.md .specify/templates/overrides/plan-template.md
   cat /path/to/plan-template-additions.md >> .specify/templates/overrides/plan-template.md
   ```

   Spec Kit uses `.specify/templates/overrides/` before its own templates
   ([customization guide](https://github.github.io/spec-kit/guides/customization.html)).
   Source: [plan-template-additions.md](plan-template-additions.md).
   After a Spec Kit upgrade, compare the override with the new core
   `plan-template.md` and merge any changes.

3. In Claude Code, write the constitution:

   ```text
   /speckit-constitution Web app monorepo: apps/web is the frontend prototype,
   apps/api is the REST API. apps/api/openapi.yaml is the single source of truth
   for the API; the frontend never calls an endpoint not in it. Contract changes
   need Architect approval. Every plan needs a completed Plan Sign-off section
   before implementation. Errors use <format>. Auth uses <method>. API versioning
   uses <scheme>. Required tests: <unit/contract/e2e rules per app>.
   ```

4. Add `.github/CODEOWNERS` with `* @architect`, a CI workflow (tests, lint,
   type checks, contract tests, CodeQL), and branch protection on `main`
   (CI required, CODEOWNERS review required).
5. Commit `.specify/`, `.claude/skills/`, `.github/`, and `specs/`.
6. Run feature `001-walking-skeleton` (one screen, one endpoint, one entity)
   through the loop below before any real feature.

## Roadmap (PM, ongoing)

- [ ] Keep `specs/roadmap.md`: one line per feature, a scope boundary, and
      its dependencies.
- [ ] Order features so dependencies come first.
- [ ] Unsure if a feature is worth building? Assess it first:
      `specify extension add assess`, then `/speckit-assess-intake ...`
      ([assessment guide](https://github.github.io/spec-kit/guides/assessment.html)).

Roadmap method:
[Spec of specs](https://github.github.io/spec-kit/concepts/spec-of-specs.html).

## Per-feature checklist

### Step 1. Specify (PM + Claude)

- [ ] Pull `main`.
- [ ] Run:

  ```text
  /speckit-specify <feature name>: <what the user does and why>.
  Prototype flow: <screen 1> -> <screen 2> -> ... Acceptance: <how we know it works>.
  ```

- [ ] Run `/speckit-clarify` and answer every question.
- [ ] Read `specs/NNN-feature/spec.md`. It must describe behavior, not tech.
- [ ] Push the `NNN-feature` branch and tell the Architect.

### Step 2. Plan (Architect + Claude)

- [ ] Read `spec.md`. Raise questions with the PM now, not later.
- [ ] Run:

  ```text
  /speckit-plan Web app layout: apps/web (prototype UI) + apps/api (REST API).
  REST contract in contracts/openapi.yaml. Stack: <stack>.
  ```

- [ ] Review `plan.md`, `data-model.md`, `contracts/`, `quickstart.md`.

### Step 3. Contract fit check (Architect)

- [ ] Fill the **Contract Fit Check** table in `plan.md`: one row per
      prototype screen or flow.
- [ ] Every row must say Yes. If not, revise the plan.
- [ ] List questions for the PM only where the prototype's intent is unclear.

### Step 4. Plan sign-off (PM + Architect, together, about 30 minutes)

- [ ] Architect walks through `plan.md`, `data-model.md`, and `contracts/` in
      product terms: which endpoint serves which screen, what data each
      screen gets.
- [ ] PM checks product fit and ticks the PM box.
- [ ] Architect checks technical fit and ticks the Architect box.
- [ ] Fill **Approved by** and **Date**. Commit and push.
- [ ] Either says no: revise the plan (or the PM revises `spec.md`) and repeat.

### Step 5. Tasks (Architect + Claude)

- [ ] Run `/speckit-tasks`, then `/speckit-analyze`.
- [ ] Fix any gaps `analyze` reports. Push.

### Step 6. Build, in parallel

Architect (API):

- [ ] `/speckit-implement only tasks under apps/api`
- [ ] Large feature: `/speckit-implement only the Setup phase, then stop`
      ([complex features](https://github.github.io/spec-kit/concepts/complex-features.html)).

PM (prototype only):

- [ ] Optional mock: `npx @stoplight/prism-cli mock specs/NNN-feature/contracts/openapi.yaml`
- [ ] `/speckit-implement only tasks under apps/web; call the API through the mock until endpoints exist`

Both:

- [ ] Pull and rebase often. Resolve `tasks.md` checkbox conflicts by keeping
      both sets of ticks.
- [ ] Never change the contract while building. Contract changes go back to
      step 3.

### Step 7. Integrate (Architect + Claude)

- [ ] Merge `specs/NNN-feature/contracts/` into `apps/api/openapi.yaml`.
- [ ] Regenerate the client:
      `npx openapi-typescript apps/api/openapi.yaml -o apps/web/src/api/schema.d.ts`
- [ ] Switch the prototype from the mock to the real API.
- [ ] Run `/speckit-converge`. Repeat implement and converge until it reports
      **Converged**.

### Step 8. PR and acceptance

Architect:

- [ ] Open the PR. Say in the description that it was AI-assisted.
- [ ] CI must be green. Review and merge.

PM (product check, not code review):

- [ ] Run the feature (local, preview, or staging).
- [ ] Walk every acceptance criterion in `spec.md`:

  | Acceptance criterion | Result | Note |
  |---|---|---|
  | [from spec.md] | [Pass / Fail] | [what was wrong] |

- [ ] Any Fail: tell the Architect. Small fix: same branch. Behavior change:
      update `spec.md` and go back to step 2.
- [ ] All Pass: mark the feature done in `specs/roadmap.md`.

## Other paths

| Situation | Do this |
|---|---|
| Bug | `specify extension add bug`, then `/speckit-bug-assess "<symptom>" slug=<name>`, `/speckit-bug-fix slug=<name>`, `/speckit-bug-test slug=<name>` ([bug-fix guide](https://github.github.io/spec-kit/guides/bugfix.html)). Verdict must be `verified`. Normal PR. |
| Change to a shipped feature | Edit its `spec.md`, rerun `/speckit-plan` and `/speckit-tasks`, redo steps 3 and 4 ([evolving specs](https://github.github.io/spec-kit/guides/evolving-specs.html)) |
| Typo or copy fix | Plain PR. CI and Architect review still apply |

## Rules for Claude sessions

- One Claude session per person, on their own machine.
- Claude never ticks sign-off boxes, approves PRs, merges, or deploys.
- Review everything Claude writes before moving to the next step.
- AI-authored commits carry a `Co-Authored-By` trailer.

## Known issues

Nothing yet. After each of the first features, add what went wrong and the
fix. Examples to watch for:

- Contract changes discovered during the build.
- `tasks.md` merge conflicts between the two sessions.
- `/speckit-converge` not reaching Converged.
- Claude drifting from the spec on long implement runs.
- Missing screens found after sign-off.
