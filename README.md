# certd

How the certd team builds software with
[GitHub Spec Kit](https://github.com/github/spec-kit) and Claude Code: a Product
Manager, an Architect, and Claude as the AI agent.

## Diagram

- [SDLC workflow diagram](https://chhatbarhiren.github.io/certd/sdlc-workflow.html):
  interactive; hover over or click any step to see its activity and who does it.

## Documents

| Document | What it covers |
|---|---|
| [WORKFLOW.md](WORKFLOW.md) | Overview: team and roles, tooling, repository layout, SDLC stages, gates, speed and quality expectations |
| [PLAYBOOK.md](PLAYBOOK.md) | Step-by-step checklists and ready-to-paste prompts for each role and each feature |
| [plan-template-additions.md](plan-template-additions.md) | Contract Fit Check and Plan Sign-off sections added to every generated `plan.md` |

## Source files

| File | Purpose |
|---|---|
| [sdlc-workflow.json](sdlc-workflow.json) | Diagram source for [Archify](https://github.com/tt-a1i/archify) |
| [add-step-details.py](add-step-details.py) | Adds the hover and click step details to `sdlc-workflow.html` |

To update the diagram: regenerate `sdlc-workflow.html` from `sdlc-workflow.json`
with Archify, run `python3 add-step-details.py`, then commit and push. GitHub
Pages republishes it within a few minutes.
