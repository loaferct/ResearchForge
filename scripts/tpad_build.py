"""Build TPAD items from recent arXiv papers (docs/paper/research_plan.md §4.1).

Stages:
  candidates  arXiv method papers in a date window -> candidates.json (for a human to choose from)
  build       chosen arXiv ids -> draft items: prior work from Semantic Scholar references, a paraphrased idea
              written by a different model than the agent, overlap and name-leak checks, and a closed-book probe
              of the agent's model. Every field needed to audit the item is kept in the draft.

The output is a draft. Each item must be read and accepted by a person before use; items are never generated
from memory. Credentials come from the environment (.env), like the rest of ResearchForge.

  python scripts/tpad_build.py candidates --from 2026-08-01 --to 2026-09-15 --out candidates.json
  python scripts/tpad_build.py build --ids 2608.01234,2608.05678 --out draft.yaml
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import httpx
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from researchforge.config import load_dotenv, load_settings  # noqa: E402
from researchforge.literature.merge import title_key, title_name  # noqa: E402
from researchforge.literature.sources import ArxivClient, query_terms  # noqa: E402

UA = {"User-Agent": "ResearchForge/0.1 (TPAD item builder)"}
S2 = "https://api.semanticscholar.org/graph/v1"
PARAPHRASE_MODEL = "gpt-oss:120b"   # deliberately not the agent's model
PROBE_MODEL = "deepseek-v4.1-flash"  # the agent's model: does it already know the paper?

PARAPHRASE_PROMPT = """Rewrite the core idea of the paper below as a short research proposal (80-150 words) written BEFORE the work was done.
Rules:
- State the problem and the proposed approach so a researcher could recognise the idea.
- Do NOT use the paper's method name, any acronym it coins, its title words in sequence, author names, numbers, or results.
- Do not claim it works; phrase it as a plan ("We propose to ...", "The idea is to ...").
- Use your own wording; do not copy phrases from the abstract.
Output only the proposal text.

Title: {title}
Abstract: {abstract}"""

PROBE_PROMPT = """Here is a research idea. Do you know of a specific published paper (arXiv or venue) that proposes essentially this idea?
If yes, give its exact title and year. If you are not sure, answer NONE. Answer in one line.

Idea: {idea}"""


def get(url, params=None, tries=8):
    for i in range(tries):
        r = httpx.get(url, params=params, headers=UA, timeout=60, follow_redirects=True)
        if r.status_code == 200:
            return r
        time.sleep(min(60, 5 * (i + 1)))
    r.raise_for_status()


def chat(model: str, prompt: str, max_tokens: int = 600) -> str:
    s = load_settings()
    c = s.model.custom
    if c is None:
        raise SystemExit("configure [model.custom] (Ollama Cloud) in researchforge.toml")
    for attempt in range(4):
        try:
            r = httpx.post(f"{c.base_url.rstrip('/')}/chat/completions", timeout=600,
                           headers={"Authorization": f"Bearer {os.environ[c.api_key_env]}"},
                           json={"model": model, "max_tokens": max_tokens, "temperature": 0.2, "messages": [{"role": "user", "content": prompt}]})
        except httpx.TransportError:
            time.sleep(15 * (attempt + 1))
            continue
        if r.status_code < 500:
            break
        time.sleep(15 * (attempt + 1))
    r.raise_for_status()
    return (r.json()["choices"][0]["message"].get("content") or "").strip()


def ngram_overlap(a: str, b: str, n: int = 5) -> float:
    ta, tb = re.findall(r"[a-z0-9]+", a.lower()), re.findall(r"[a-z0-9]+", b.lower())
    ga = {tuple(ta[i:i + n]) for i in range(len(ta) - n + 1)}
    gb = {tuple(tb[i:i + n]) for i in range(len(tb) - n + 1)}
    return round(len(ga & gb) / len(ga), 3) if ga else 0.0


def words(text: str) -> set[str]:
    return {t for t in query_terms(text or "") if len(t) > 3}


def jaccard(a: str, b: str) -> float:
    wa, wb = words(a), words(b)
    return len(wa & wb) / len(wa | wb) if wa and wb else 0.0


def cmd_candidates(args):
    cats = "(cat:cs.CL OR cat:cs.LG OR cat:cs.IR OR cat:cs.AI)"
    q = f'{cats} AND abs:"we propose" AND submittedDate:[{args.date_from.replace("-", "")}0000 TO {args.date_to.replace("-", "")}2359]'
    out = []
    for start in range(0, args.n, 100):
        r = get("https://export.arxiv.org/api/query", {"search_query": q, "start": start, "max_results": 100, "sortBy": "submittedDate"})
        papers = ArxivClient.parse(r.text)
        out += [{"arxiv": p.arxiv_id, "title": p.title, "published": p.published, "abstract": p.abstract} for p in papers]
        time.sleep(3.5)
    Path(args.out).write_text(json.dumps(out, indent=1))
    print(f"{len(out)} candidates -> {args.out}")


def s2_paper(arxiv_id: str) -> dict:
    return get(f"{S2}/paper/arXiv:{arxiv_id}", {"fields": "title,publicationDate,externalIds,abstract"}).json()


def s2_references(arxiv_id: str) -> list[dict]:
    r = get(f"{S2}/paper/arXiv:{arxiv_id}/references", {"fields": "title,publicationDate,year,externalIds,abstract", "limit": 500})
    return [x["citedPaper"] for x in r.json().get("data") or [] if x.get("citedPaper") and x["citedPaper"].get("title")]


def arxiv_record(arxiv_id: str) -> dict:
    r = get("https://export.arxiv.org/api/query", {"id_list": arxiv_id, "max_results": 1})
    p = ArxivClient.parse(r.text)[0]
    return {"arxiv": p.arxiv_id, "title": p.title, "published": p.published, "abstract": p.abstract}


def ref_date(x: dict) -> str | None:
    """A reference's date: its publication date, else January 1 of its year (only used if the year is earlier)."""
    return x.get("publicationDate") or (f"{x['year']}-01-01" if x.get("year") else None)


def select_prior(rec: dict, refs: list[dict], k: int) -> tuple[list[dict], int]:
    """Closest earlier references by distinctive-word overlap with the realising abstract (abstract, else title)."""
    earlier = [x for x in refs if (d := ref_date(x)) and d[:4] < rec["published"][:4] or (x.get("publicationDate") and x["publicationDate"] < rec["published"])]
    ranked = sorted(earlier, key=lambda x: -jaccard(rec["abstract"], x.get("abstract") or x["title"]))[:k]
    prior = [{"title": x["title"], "arxiv": (x.get("externalIds") or {}).get("ArXiv"), "doi": (x.get("externalIds") or {}).get("DOI"),
              "published": ref_date(x), "similarity": round(jaccard(rec["abstract"], x.get("abstract") or x["title"]), 3)} for x in ranked]
    return prior, len(earlier)


def probe(idea: str, rec: dict, model: str | None = None) -> tuple[str, bool]:
    model = model or PROBE_MODEL
    # Reasoning models think at length before answering; leave room, and retry once if the answer is still cut off.
    answer = chat(model, PROBE_PROMPT.format(idea=idea), max_tokens=8000)
    if not answer:
        answer = chat(model, PROBE_PROMPT.format(idea=idea), max_tokens=16000)
    name = title_name(rec["title"])
    hit = title_key(rec["title"])[:40] in title_key(answer) or bool(name and name in re.sub(r"[^a-z0-9]", "", answer.lower()))
    return answer, hit


def build_item(arxiv_id: str, k_prior: int) -> dict:
    rec = arxiv_record(arxiv_id)
    time.sleep(3.5)
    refs = s2_references(arxiv_id)
    time.sleep(1.5)
    prior, n_earlier = select_prior(rec, refs, k_prior)
    idea = chat(PARAPHRASE_MODEL, PARAPHRASE_PROMPT.format(title=rec["title"], abstract=rec["abstract"]), max_tokens=4000)
    name = title_name(rec["title"])
    leaks = [w for w in {name} if w and w in re.sub(r"[^a-z0-9]", "", idea.lower())]
    probe_answer, probe_hit = probe(idea, rec)
    earlier = range(n_earlier)
    return {
        "id": f"T-{arxiv_id}",
        "idea": idea,
        "realising": {"title": rec["title"], "arxiv": rec["arxiv"], "published": rec["published"]},
        "prior_work": [{k: v for k, v in p.items() if k in ("title", "arxiv", "doi", "published") and v} for p in prior],
        "domain": "cs",
        "verification": "",
        "_audit": {
            "realising_abstract": rec["abstract"],
            "references_total": len(refs),
            "references_earlier_with_abstract": len(earlier),
            "prior_similarity": [p["similarity"] for p in prior],
            "idea_5gram_overlap_with_abstract": ngram_overlap(idea, rec["abstract"]),
            "method_name_leaks": leaks,
            "paraphrase_model": PARAPHRASE_MODEL,
            "probe_model": PROBE_MODEL,
            "probe_answer": probe_answer,
            "probe_names_realising_paper": probe_hit,
        },
    }


def cmd_build(args):
    out = Path(args.out)
    existing = yaml.safe_load(out.read_text()) if out.exists() else {"name": "tpad-draft", "items": []}
    have = {i["realising"]["arxiv"] for i in existing["items"]}
    for aid in [x.strip() for x in args.ids.split(",") if x.strip()]:
        if aid in have:
            continue
        try:
            item = build_item(aid, args.k_prior)
        except Exception as exc:  # keep going; report the failure
            print(f"{aid}: FAILED {type(exc).__name__}: {exc}")
            continue
        existing["items"].append(item)
        out.write_text(yaml.safe_dump(existing, sort_keys=False, allow_unicode=True, width=120))
        a = item["_audit"]
        print(f"{aid}: prior={len(item['prior_work'])} overlap={a['idea_5gram_overlap_with_abstract']} leaks={a['method_name_leaks']} "
              f"probe_hit={a['probe_names_realising_paper']}")


def cmd_refresh(args):
    """Recompute prior work and the closed-book probe for every draft item, keeping the idea text."""
    out = Path(args.out)
    data = yaml.safe_load(out.read_text())
    for item in data["items"]:
        if item["_audit"].get("refreshed"):
            continue
        rec = {"title": item["realising"]["title"], "published": str(item["realising"]["published"]), "abstract": item["_audit"]["realising_abstract"]}
        refs = s2_references(item["realising"]["arxiv"])
        time.sleep(1.5)
        prior, n_earlier = select_prior(rec, refs, args.k_prior)
        answer, hit = probe(item["idea"], rec)
        item["prior_work"] = [{k: v for k, v in p.items() if k in ("title", "arxiv", "doi", "published") and v} for p in prior]
        item["_audit"].update({"references_total": len(refs), "references_earlier_with_abstract": n_earlier,
                               "prior_similarity": [p["similarity"] for p in prior], "probe_answer": answer, "probe_names_realising_paper": hit, "refreshed": True})
        out.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=120))
        print(f"{item['id']}: prior={len(prior)} probe_hit={hit} probe={answer[:100]!r}", flush=True)


def cmd_regen(args):
    """Rewrite the idea of one item (e.g. a truncated paraphrase) and re-run its checks and probe."""
    out = Path(args.out)
    data = yaml.safe_load(out.read_text())
    item = next(i for i in data["items"] if i["id"] == args.id)
    rec = {"title": item["realising"]["title"], "published": str(item["realising"]["published"]), "abstract": item["_audit"]["realising_abstract"]}
    idea = chat(PARAPHRASE_MODEL, PARAPHRASE_PROMPT.format(title=rec["title"], abstract=rec["abstract"]), max_tokens=4000)
    name = title_name(rec["title"])
    answer, hit = probe(idea, rec)
    item["idea"] = idea
    item["_audit"].update({"idea_5gram_overlap_with_abstract": ngram_overlap(idea, rec["abstract"]),
                           "method_name_leaks": [w for w in {name} if w and w in re.sub(r"[^a-z0-9]", "", idea.lower())],
                           "probe_answer": answer, "probe_names_realising_paper": hit, "regenerated": True})
    out.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=120))
    print(idea, "\n", item["_audit"]["idea_5gram_overlap_with_abstract"], hit, answer[:100])


def cmd_reprobe(args):
    """Run the closed-book probe for every item with the agent's model (after changing the agent model)."""
    out = Path(args.out)
    data = yaml.safe_load(out.read_text())
    for item in data["items"]:
        rec = {"title": item["realising"]["title"]}
        answer, hit = probe(item["idea"], rec, args.model)
        item["_audit"].setdefault("probes", {})[args.model] = {"answer": answer, "names_realising_paper": hit}
        item["_audit"].update({"probe_model": args.model, "probe_answer": answer, "probe_names_realising_paper": hit})
        out.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=120))
        print(f"{item['id']}: hit={hit} answer={answer[:110]!r}", flush=True)


def cmd_finalize(args):
    """Apply the exclusion rules (name leak, 5-gram overlap > 0.10, probe names the paper) and write the item set."""
    data = yaml.safe_load(Path(args.draft).read_text())
    kept, excluded = [], []
    for item in data["items"]:
        a = item["_audit"]
        why = [r for r, bad in (("method name leaks", a["method_name_leaks"]), ("5-gram overlap > 0.10", a["idea_5gram_overlap_with_abstract"] > 0.10),
                                ("closed-book probe names the paper", a["probe_names_realising_paper"])) if bad]
        if why:
            excluded.append({"id": item["id"], "reasons": why})
            continue
        item = {k: v for k, v in item.items() if k != "_audit"}
        item["verification"] = args.verification
        kept.append(item)
    Path(args.out).write_text(yaml.safe_dump({"name": args.name, "description": args.description, "items": kept}, sort_keys=False, allow_unicode=True, width=120))
    print(f"kept {len(kept)}, excluded {len(excluded)}: {excluded}")


def main():
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(required=True)
    c = sub.add_parser("candidates")
    c.add_argument("--from", dest="date_from", required=True)
    c.add_argument("--to", dest="date_to", required=True)
    c.add_argument("--n", type=int, default=300)
    c.add_argument("--out", default="candidates.json")
    c.set_defaults(fn=cmd_candidates)
    b = sub.add_parser("build")
    b.add_argument("--ids", required=True)
    b.add_argument("--k-prior", type=int, default=3)
    b.add_argument("--out", default="draft.yaml")
    b.set_defaults(fn=cmd_build)
    r = sub.add_parser("refresh")
    r.add_argument("--k-prior", type=int, default=3)
    r.add_argument("--out", default="draft.yaml")
    r.set_defaults(fn=cmd_refresh)
    g = sub.add_parser("regen")
    g.add_argument("--id", required=True)
    g.add_argument("--out", default="draft.yaml")
    g.set_defaults(fn=cmd_regen)
    q = sub.add_parser("reprobe")
    q.add_argument("--model", required=True)
    q.add_argument("--out", default="draft.yaml")
    q.set_defaults(fn=cmd_reprobe)
    f = sub.add_parser("finalize")
    f.add_argument("--draft", default="draft.yaml")
    f.add_argument("--out", default="items.yaml")
    f.add_argument("--name", default="tpad-pilot")
    f.add_argument("--description", default="")
    f.add_argument("--verification", default="")
    f.set_defaults(fn=cmd_finalize)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
