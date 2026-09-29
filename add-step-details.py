"""Inject hover/click step details into sdlc-workflow.html.

Run after every `archify deliver`, because deliver overwrites the HTML:
    python3 add-step-details.py
"""
import html
import json
import re
from pathlib import Path

HTML = Path(__file__).with_name("sdlc-workflow.html")

# node id -> (who, activity lines)
STEPS = {
    "setup": ("Architect + Claude", [
        "specify init --here --integration claude",
        "/speckit-constitution: layout, openapi.yaml as API source of truth, error format, auth, versioning, test rules",
        "Set up CI, CODEOWNERS (* @architect) and branch protection",
        "Once per project"]),
    "roadmap": ("PM", [
        "List product features in specs/roadmap.md",
        "Order by dependency (for example accounts before billing)",
        "Pick the next feature; add, reorder or drop as the product evolves"]),
    "specify": ("PM + Claude · Architect reads", [
        "/speckit-specify <feature + prototype flow> creates branch NNN-feature and spec.md",
        "/speckit-clarify resolves open questions",
        "Architect reads the spec before planning"]),
    "plan": ("Architect + Claude", [
        "/speckit-plan with the web app layout hint (apps/web + apps/api)",
        "Writes plan.md, data-model.md, contracts/ (OpenAPI), quickstart.md",
        "Plan is checked against the constitution"]),
    "contract": ("Architect", [
        "Check every prototype screen and flow has the endpoints and fields it needs",
        "Missing pieces: revise the plan",
        "Ask the PM only when the prototype's intent is unclear"]),
    "signoff": ("PM + Architect, together", [
        "Walk through plan.md, data-model.md and contracts/ to build a shared mental model",
        "PM checks product fit: every user story covered, scope and trade-offs acceptable",
        "Architect checks technical fit: constitution, data model, contract, risks",
        "Both approve, recorded in plan.md; otherwise back to Plan"]),
    "implement": ("Architect + Claude · PM + Claude, in parallel", [
        "Architect: /speckit-tasks, /speckit-analyze, then /speckit-implement only tasks under apps/api",
        "PM: /speckit-implement only tasks under apps/web, against a mock API",
        "Pull and rebase often; tasks.md conflicts are normal"]),
    "converge": ("Architect + Claude", [
        "Merge the feature's contracts/ into apps/api/openapi.yaml",
        "Regenerate the typed client in apps/web/src/api/",
        "Switch the prototype from the mock to the real API",
        "/speckit-converge until it reports Converged"]),
    "pr_gate": ("CI (automated)", [
        "Tests, lint, type checks, contract tests against openapi.yaml, CodeQL, Dependabot",
        "Must be green before review"]),
    "review": ("Architect · PM accepts the product", [
        "Architect reviews and merges the PR (CODEOWNERS + branch protection)",
        "PM tries the running feature and accepts it against spec.md",
        "PM never reviews or approves PRs"]),
    "deploy": ("CI/CD pipeline, no agent", [
        "Deploy the merged build",
        "Smoke tests pass; rollback path ready"]),
    "bug": ("Reporter + Claude · Architect reviews", [
        "specify extension add bug",
        "/speckit-bug-assess, /speckit-bug-fix, /speckit-bug-test",
        "Verdict must be verified; fix lands as a normal PR"]),
}

START, END = "<!-- step-details:start -->", "<!-- step-details:end -->"

SNIPPET = START + """
<style>
#step-details{position:fixed;z-index:9999;max-width:360px;padding:12px 14px;border-radius:10px;
 background:rgba(15,23,42,.96);color:#e2e8f0;font:13px/1.45 system-ui,sans-serif;
 box-shadow:0 8px 24px rgba(0,0,0,.35);border:1px solid #334155;display:none}
#step-details b{display:block;font-size:14px;color:#fff}
#step-details i{display:block;margin:2px 0 6px;color:#7dd3fc;font-style:normal}
#step-details ul{margin:0;padding-left:18px}
#step-details .pin{margin-top:6px;color:#94a3b8;font-size:11px}
</style>
<div id="step-details" role="tooltip"></div>
<script>
(() => {
  const STEPS = __STEPS__;
  const box = document.getElementById("step-details");
  // Any SVG <title>, including the diagram's own, triggers the browser's native
  // tooltip on hover. Keep the accessible name as aria-label, then drop them all.
  document.querySelectorAll("svg[aria-labelledby]").forEach(svg => {
    const t = svg.querySelector(":scope > title");
    if (t) svg.setAttribute("aria-label", t.textContent);
    svg.removeAttribute("aria-labelledby");
    const d = svg.querySelector(":scope > desc");
    if (d && d.id) svg.setAttribute("aria-describedby", d.id);
  });
  document.querySelectorAll("svg title").forEach(t => t.remove());
  let pinned = null;
  const esc = s => s.replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  function show(node, pin) {
    const id = node.dataset.nodeId, s = STEPS[id];
    if (!s) return;
    box.innerHTML = "<b>" + esc(node.dataset.nodeTag + " · " + node.dataset.nodeLabel) + "</b><i>" + esc(s[0]) +
      "</i><ul>" + s[1].map(l => "<li>" + esc(l) + "</li>").join("") + "</ul>" +
      '<div class="pin">' + (pin ? "Pinned · Esc or click outside to close" : "Click to pin") + "</div>";
    box.style.display = "block";
    const r = node.getBoundingClientRect(), b = box.getBoundingClientRect();
    let x = r.right + 12, y = r.top;
    if (x + b.width > innerWidth - 8) x = r.left - b.width - 12;
    if (x < 8) x = 8;
    y = Math.max(8, Math.min(y, innerHeight - b.height - 8));
    box.style.left = x + "px"; box.style.top = y + "px";
  }
  const hide = () => { pinned = null; box.style.display = "none"; };
  const nodeOf = e => e.target.closest && e.target.closest("[data-node-id]");
  document.addEventListener("mouseover", e => { const n = nodeOf(e); if (n && !pinned) show(n, false); });
  document.addEventListener("mouseout", e => { const n = nodeOf(e); if (n && !pinned && !n.contains(e.relatedTarget)) box.style.display = "none"; });
  document.addEventListener("focusin", e => { const n = nodeOf(e); if (n && !pinned) show(n, false); });
  document.addEventListener("click", e => {
    const n = nodeOf(e);
    if (n) { pinned = n; show(n, true); } else if (!box.contains(e.target)) hide();
  });
  document.addEventListener("keydown", e => { if (e.key === "Escape") hide(); });
})();
</script>
""" + END


def main():
    text = HTML.read_text()
    text = re.sub(re.escape(START) + ".*?" + re.escape(END), "", text, flags=re.S)
    ids = set(re.findall(r'data-node-id="(\w+)"', text))
    missing = ids - STEPS.keys()
    assert not missing, f"no step details for nodes: {sorted(missing)}"
    # "</" inside JSON would end the <script> early
    data = json.dumps(STEPS).replace("</", "<\\/")
    text = text.replace("</body>", SNIPPET.replace("__STEPS__", data) + "\n</body>", 1)
    HTML.write_text(text)
    print(f"step details injected for {len(ids)} nodes")


if __name__ == "__main__":
    main()
