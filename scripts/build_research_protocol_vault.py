from __future__ import annotations

import json
import re
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
FACTOR_FILE = BASE_DIR / "data" / "factors" / "factor_registry.json"
FORMULA_FILE = BASE_DIR / "data" / "factors" / "prediction_formulas.json"
PAPER_FILE = BASE_DIR / "data" / "papers" / "dashboard_practices.json"
CONCEPT_FILE = BASE_DIR / "data" / "papers" / "quant_concepts.json"
FLOW_FILE = BASE_DIR / "data" / "factors" / "methodology_flow.json"
VAULT_DIR = BASE_DIR / "vault" / "market-map"
RESEARCH_DIR = VAULT_DIR / "research"
PAPER_DIR = VAULT_DIR / "papers"
CONCEPT_DIR = VAULT_DIR / "concepts"
WORKFLOW_DIR = VAULT_DIR / "workflows"


def slugify(value: str) -> str:
  return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def load_json(path: Path):
  return json.loads(path.read_text()) if path.exists() else []


def ensure_dirs() -> None:
  RESEARCH_DIR.mkdir(parents=True, exist_ok=True)
  PAPER_DIR.mkdir(parents=True, exist_ok=True)
  CONCEPT_DIR.mkdir(parents=True, exist_ok=True)
  WORKFLOW_DIR.mkdir(parents=True, exist_ok=True)


def write_factor_notes() -> None:
  factors = load_json(FACTOR_FILE)
  formulas = {item["key"]: item for item in load_json(FORMULA_FILE)}
  for factor in factors:
    formula = formulas.get(factor.get("key"))
    body = [
      "---",
      f"title: {factor.get('label', 'Factor')}",
      f"key: {factor.get('key', '')}",
      f"cadence: {factor.get('cadence', '')}",
      f"significance: {factor.get('significance', '')}",
      "---",
      "",
      f"# {factor.get('label', 'Factor')}",
      "",
      factor.get("why", ""),
      "",
      "## Facts first",
      "",
      factor.get("factsFirst", ""),
      "",
      "## Watch for",
      "",
      factor.get("watchFor", ""),
    ]
    if formula:
      body.extend(
        [
          "",
          "## Formula lens",
          "",
          f"`{formula.get('formula', '')}`",
          "",
          formula.get("why", ""),
        ]
      )
    (RESEARCH_DIR / f"{slugify(factor.get('label', 'factor'))}.md").write_text("\n".join(body).strip() + "\n")


def write_paper_notes() -> None:
  papers = load_json(PAPER_FILE)
  for paper in papers:
    body = "\n".join(
      [
        "---",
        f"title: {paper.get('title', 'Paper')}",
        f"year: {paper.get('year', '')}",
        f"type: {paper.get('type', '')}",
        f"url: {paper.get('url', '')}",
        "---",
        "",
        f"# {paper.get('title', 'Paper')}",
        "",
        f"Type: {paper.get('type', '')}",
        "",
        "## Dashboard practice",
        "",
        paper.get("practice", ""),
        "",
        "## Dashboard use",
        "",
        paper.get("dashboardUse", ""),
        "",
        "## Required factors",
        "",
        *[f"- {item}" for item in paper.get("requiredFactors", [])],
      ]
    )
    (PAPER_DIR / f"{slugify(paper.get('title', 'paper'))}.md").write_text(body.strip() + "\n")


def write_concept_notes() -> None:
  concepts = load_json(CONCEPT_FILE)
  for concept in concepts:
    body = [
      "---",
      f"title: {concept.get('label', 'Concept')}",
      f"key: {concept.get('key', '')}",
      f"family: {concept.get('family', '')}",
      f"phase: {concept.get('phase', '')}",
      f"cadence: {concept.get('cadence', '')}",
      f"url: {concept.get('url', '')}",
      "---",
      "",
      f"# {concept.get('label', 'Concept')}",
      "",
      concept.get("whyItMatters", ""),
      "",
      "## Formula",
      "",
      f"`{concept.get('formula', '')}`",
      "",
      "## Used in dashboard",
      "",
      concept.get("useWhere", ""),
      "",
      "## Impact path",
      "",
      concept.get("impactPath", ""),
      "",
      "## Source",
      "",
      concept.get("sourceTitle", ""),
    ]
    (CONCEPT_DIR / f"{slugify(concept.get('label', 'concept'))}.md").write_text("\n".join(body).strip() + "\n")


def write_workflow_notes() -> None:
  flow = load_json(FLOW_FILE)
  index_lines = [
    "---",
    "title: Market Decision Flow",
    "---",
    "",
    "# Market Decision Flow",
    "",
    "This workflow shows how the dashboard turns raw macro, market, and event inputs into scenario-based decision support.",
    "",
  ]
  for step in flow:
    body = [
      "---",
      f"title: {step.get('label', 'Workflow step')}",
      f"id: {step.get('id', '')}",
      "---",
      "",
      f"# {step.get('label', 'Workflow step')}",
      "",
      step.get("summary", ""),
      "",
      "## Included signals",
      "",
      *[f"- {item}" for item in step.get("kinds", [])],
    ]
    filename = f"{slugify(step.get('label', 'workflow-step'))}.md"
    (WORKFLOW_DIR / filename).write_text("\n".join(body).strip() + "\n")
    index_lines.append(f"- [[workflows/{step.get('label', 'Workflow step')}]]")
  (WORKFLOW_DIR / "Market Decision Flow.md").write_text("\n".join(index_lines).strip() + "\n")


def main() -> None:
  ensure_dirs()
  write_factor_notes()
  write_paper_notes()
  write_concept_notes()
  write_workflow_notes()
  print(
    json.dumps(
      {
        "researchNotes": len(list(RESEARCH_DIR.glob("*.md"))),
        "paperNotes": len(list(PAPER_DIR.glob("*.md"))),
        "conceptNotes": len(list(CONCEPT_DIR.glob("*.md"))),
        "workflowNotes": len(list(WORKFLOW_DIR.glob("*.md"))),
      },
      indent=2,
    )
  )


if __name__ == "__main__":
  main()
