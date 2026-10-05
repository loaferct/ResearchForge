"""Analyse TPAD results: rates with Wilson intervals, paired McNemar tests, paired bootstrap on costs, figures.

Reads only <out>/results.jsonl (one row per run, written by `researchforge bench run`). Writes
<paper>/generated/results.tex (macros and tables) and figures, plus a JSON summary.

  python scripts/tpad_analyze.py bench/tpad/runs-pilot --paper docs/paper/latex
"""

from __future__ import annotations

import argparse
import json
import math
import random
from collections import defaultdict
from pathlib import Path

SYSTEM_NAMES = {"full": "\\textsc{full}", "nochal": "\\textsc{nochal}", "pipe": "\\textsc{pipe}", "norecrit": "\\textsc{norecrit}", "pipe+": "\\textsc{pipe+}"}


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


def mcnemar_exact(b: int, c: int) -> float:
    """Two-sided exact McNemar p-value from discordant counts b (A yes, B no) and c (A no, B yes)."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    p = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, 2 * p)


def bootstrap_mean_diff(pairs: list[tuple[float, float]], iters: int = 10000, seed: int = 0) -> tuple[float, float, float]:
    rng = random.Random(seed)
    diffs = [a - b for a, b in pairs]
    if not diffs:
        return (float("nan"),) * 3
    means = []
    for _ in range(iters):
        s = [diffs[rng.randrange(len(diffs))] for _ in diffs]
        means.append(sum(s) / len(s))
    means.sort()
    return (sum(diffs) / len(diffs), means[int(0.025 * iters)], means[int(0.975 * iters)])


def median(xs):
    xs = sorted(xs)
    n = len(xs)
    return float("nan") if n == 0 else (xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2)


def load(out: Path) -> list[dict]:
    rows = [json.loads(l) for l in (out / "results.jsonl").read_text().splitlines() if l.strip()]
    latest = {}
    for r in rows:
        latest[r["key"]] = r  # a re-run replaces the earlier row
    return [r for r in latest.values() if not r.get("error")]


def analyse(rows: list[dict]) -> dict:
    systems = sorted({r["system"] for r in rows}, key=lambda s: list(SYSTEM_NAMES).index(s) if s in SYSTEM_NAMES else 99)
    by = {(r["item"], r["condition"], r["system"]): r for r in rows}
    items = sorted({r["item"] for r in rows})
    leaked = {r["item"] for r in rows if r["condition"] == "prepub" and r.get("leak")}
    res: dict = {"systems": systems, "items": len(items), "leaked_items": sorted(leaked), "per_system": {}, "pairs": {}}

    def rate(system, cond, key, exclude_leaked=False):
        rs = [by[(i, cond, system)] for i in items if (i, cond, system) in by and not (exclude_leaked and i in leaked)]
        k = sum(1 for r in rs if r.get(key))
        lo, hi = wilson(k, len(rs))
        return {"k": k, "n": len(rs), "rate": k / len(rs) if rs else float("nan"), "lo": lo, "hi": hi}

    # Per-item verdict discrimination: "already explored" when the realising paper is visible, not when it is hidden.
    for s in systems:
        for i in items:
            a, b = by.get((i, "scooped", s)), by.get((i, "prepub", s))
            if a and b and i not in leaked:
                a["discriminates"] = a.get("verdict") == "ALREADY_WELL_EXPLORED" and b.get("verdict") != "ALREADY_WELL_EXPLORED"
                a["scoop_both"] = a.get("verdict") == "ALREADY_WELL_EXPLORED" and b.get("verdict") == "ALREADY_WELL_EXPLORED"

    for s in systems:
        d = {
            "scoop_detected": rate(s, "scooped", "scoop_detected"),
            "realising_retrieved": rate(s, "scooped", "realising_retrieved"),
            "realising_analysed": rate(s, "scooped", "realising_analysed"),
            "realising_cited": rate(s, "scooped", "realising_cited_verified"),
            "false_scoop": rate(s, "prepub", "false_scoop_candidate", exclude_leaked=True),
            "discriminates": rate(s, "scooped", "discriminates", exclude_leaked=True),
            "scoop_both": rate(s, "scooped", "scoop_both", exclude_leaked=True),
        }
        verdicts = defaultdict(lambda: defaultdict(int))
        for r in rows:
            if r["system"] == s:
                verdicts[r["condition"]][r.get("verdict") or "NONE"] += 1
        d["verdicts"] = {c: dict(v) for c, v in verdicts.items()}
        for cond in ("scooped", "prepub"):
            rs = [by[(i, cond, s)] for i in items if (i, cond, s) in by and not (cond == "prepub" and i in leaked)]
            d[f"{cond}_cost"] = {k: median([r["cost"][k] for r in rs]) for k in ("iterations", "tool_calls", "tokens", "searches", "papers_retrieved", "papers_read")}
            d[f"{cond}_wall_min"] = median([r["wall_s"] / 60 for r in rs])
            d[f"{cond}_prior_recall"] = sum(r["prior_work_recall"] or 0 for r in rs) / len(rs) if rs else float("nan")
            d[f"{cond}_challenges"] = sum(r["process"]["challenges"] for r in rs) / len(rs) if rs else float("nan")
            d[f"{cond}_contradictions"] = sum(r["process"]["contradictory_evidence_found"] for r in rs) / len(rs) if rs else float("nan")
            d[f"{cond}_status"] = dict(sorted(defaultdict(int, {st: sum(1 for r in rs if r.get("status") == st) for st in {r.get("status") for r in rs}}).items()))
        res["per_system"][s] = d

    def paired(a, b, cond, key):
        common = [i for i in items if (i, cond, a) in by and (i, cond, b) in by and not (cond == "prepub" and i in leaked)]
        ya = [bool(by[(i, cond, a)].get(key)) for i in common]
        yb = [bool(by[(i, cond, b)].get(key)) for i in common]
        bb = sum(1 for x, y in zip(ya, yb) if x and not y)
        cc = sum(1 for x, y in zip(ya, yb) if y and not x)
        return {"n": len(common), "a_only": bb, "b_only": cc, "p": mcnemar_exact(bb, cc), "diff": (sum(ya) - sum(yb)) / len(common) if common else float("nan")}

    def paired_cost(a, b, cond, key):
        common = [i for i in items if (i, cond, a) in by and (i, cond, b) in by and not (cond == "prepub" and i in leaked)]
        m, lo, hi = bootstrap_mean_diff([(by[(i, cond, a)]["cost"][key], by[(i, cond, b)]["cost"][key]) for i in common])
        return {"n": len(common), "mean_diff": m, "lo": lo, "hi": hi}

    for a, b in (("full", "nochal"), ("full", "pipe"), ("nochal", "pipe")):
        if a in systems and b in systems:
            res["pairs"][f"{a}-vs-{b}"] = {
                "scoop_detected": paired(a, b, "scooped", "scoop_detected"),
                "realising_cited": paired(a, b, "scooped", "realising_cited_verified"),
                "realising_retrieved": paired(a, b, "scooped", "realising_retrieved"),
                "discriminates": paired(a, b, "scooped", "discriminates"),
                "false_scoop": paired(a, b, "prepub", "false_scoop_candidate"),
                "tool_calls_scooped": paired_cost(a, b, "scooped", "tool_calls"),
                "tool_calls_prepub": paired_cost(a, b, "prepub", "tool_calls"),
                "tokens_scooped": paired_cost(a, b, "scooped", "tokens"),
            }
    return res


SHORT = {"ALREADY_WELL_EXPLORED": "AWE", "INSUFFICIENT_EVIDENCE": "IE", "NEEDS_MODIFICATION": "NM", "PROMISING": "PR", None: "--"}


def write_item_verdicts(rows: list[dict], paper: Path) -> None:
    """Appendix table: per item, each system's verdict under both conditions, with P retrieved (r) / cited (c) marks."""
    systems = sorted({r["system"] for r in rows}, key=lambda s: list(SYSTEM_NAMES).index(s) if s in SYSTEM_NAMES else 99)
    by = {(r["item"], r["condition"], r["system"]): r for r in rows}
    items = sorted({r["item"] for r in rows})
    head = " & ".join(f"\\multicolumn{{2}}{{c}}{{{SYSTEM_NAMES.get(s, s)}}}" for s in systems)
    sub = " & ".join("\\textsc{sc} & \\textsc{pp}" for _ in systems)
    lines = [f"\\begin{{longtable}}{{l{'cc' * len(systems)}}}\\toprule", f"Item & {head} \\\\", f" & {sub} \\\\ \\midrule\\endhead"]
    for i in items:
        cells = []
        for s in systems:
            for c in ("scooped", "prepub"):
                r = by.get((i, c, s))
                if r is None:
                    cells.append("")
                    continue
                mark = ("$^{c}$" if r.get("realising_cited_verified") else "$^{r}$" if r.get("realising_retrieved") else "")
                cells.append(SHORT.get(r.get("verdict"), "?") + mark + ("$^{L}$" if r.get("leak") else ""))
        lines.append(f"{i.removeprefix('T-')} & " + " & ".join(cells) + " \\\\")
    lines.append("\\bottomrule\\end{longtable}")
    gen = paper / "generated"
    gen.mkdir(parents=True, exist_ok=True)
    (gen / "item_verdicts.tex").write_text("\n".join(lines) + "\n")


def pct(x):
    return "--" if x != x else f"{100 * x:.0f}"


def write_latex(res: dict, paper: Path) -> None:
    gen = paper / "generated"
    gen.mkdir(parents=True, exist_ok=True)
    ps = res["per_system"]
    lines = [f"% Generated by scripts/tpad_analyze.py from results.jsonl. Do not edit by hand.",
             f"\\newcommand{{\\ResItems}}{{{res['items']}}}",
             f"\\newcommand{{\\ResLeaked}}{{{len(res['leaked_items'])}}}"]
    # Main table
    t = ["\\begin{table}[t]\\centering\\small",
         "\\caption{Main results. \\textsc{scooped}: the realising paper is visible; \\textsc{prepub}: it is hidden. Rates in \\%, with Wilson 95\\% intervals; costs are medians per run.}\\label{tab:main}",
         "\\begin{tabular}{lcccccc}\\toprule",
         " & \\multicolumn{4}{c}{\\textsc{scooped}} & \\multicolumn{2}{c}{\\textsc{prepub}} \\\\ \\cmidrule(lr){2-5}\\cmidrule(lr){6-7}",
         "System & Detected & $P$ retrieved & $P$ cited (verified) & Tool calls & False-scoop cand. & Tool calls \\\\ \\midrule"]
    for s in res["systems"]:
        d = ps[s]
        f = lambda r: f"{pct(r['rate'])} [{pct(r['lo'])}, {pct(r['hi'])}] ({r['k']}/{r['n']})"  # noqa: E731
        t.append(f"{SYSTEM_NAMES.get(s, s)} & {f(d['scoop_detected'])} & {pct(d['realising_retrieved']['rate'])} & {pct(d['realising_cited']['rate'])} & "
                 f"{d['scooped_cost']['tool_calls']:.0f} & {f(d['false_scoop'])} & {d['prepub_cost']['tool_calls']:.0f} \\\\")
    t += ["\\bottomrule\\end{tabular}\\end{table}"]
    (gen / "table_main.tex").write_text("\n".join(t) + "\n")
    # Pairwise table
    t = ["\\begin{table}[t]\\centering\\small",
         "\\caption{Paired comparisons by item. Discordant counts are (A only / B only); $p$ is the exact McNemar test. Cost differences are mean A$-$B with paired-bootstrap 95\\% intervals.}\\label{tab:pairs}",
         "\\begin{tabular}{lccccc}\\toprule",
         "A vs.\\ B & Detected (\\textsc{scooped}) & $P$ cited & False scoop (\\textsc{prepub}) & $\\Delta$ tool calls (\\textsc{scooped}) & $\\Delta$ tokens (\\textsc{scooped}) \\\\ \\midrule"]
    for name, p in res["pairs"].items():
        a, b = name.split("-vs-")
        fm = lambda x: f"{x['a_only']}/{x['b_only']}, $p$={x['p']:.2f}"  # noqa: E731
        fc = lambda x, dec=0: f"{x['mean_diff']:+.{dec}f} [{x['lo']:+.{dec}f}, {x['hi']:+.{dec}f}]"  # noqa: E731
        tok = p["tokens_scooped"]
        tok_s = f"{tok['mean_diff']/1000:+.0f}k [{tok['lo']/1000:+.0f}k, {tok['hi']/1000:+.0f}k]" if tok["mean_diff"] == tok["mean_diff"] else "--"
        t.append(f"{SYSTEM_NAMES.get(a, a)} vs.\\ {SYSTEM_NAMES.get(b, b)} & {fm(p['scoop_detected'])} & {fm(p['realising_cited'])} & {fm(p['false_scoop'])} & {fc(p['tool_calls_scooped'])} & {tok_s} \\\\")
    t += ["\\bottomrule\\end{tabular}\\end{table}"]
    (gen / "table_pairs.tex").write_text("\n".join(t) + "\n")
    (gen / "results.tex").write_text("\n".join(lines) + "\n")


def figures(res: dict, paper: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    gen = paper / "generated"
    systems = res["systems"]
    ps = res["per_system"]
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.6))
    for ax, (key, cond, title) in zip(axes, (("scoop_detected", "scooped", "Scoop detected (SCOOPED)"), ("false_scoop", "prepub", "False-scoop candidates (PREPUB)"))):
        vals = [ps[s][key] for s in systems]
        x = range(len(systems))
        ax.bar(x, [100 * v["rate"] for v in vals], color="#4C72B0", width=0.6)
        ax.errorbar(x, [100 * v["rate"] for v in vals], yerr=[[100 * (v["rate"] - v["lo"]) for v in vals], [100 * (v["hi"] - v["rate"]) for v in vals]],
                    fmt="none", ecolor="black", capsize=3, lw=1)
        ax.set_xticks(list(x), [s.upper() for s in systems])
        ax.set_ylim(0, 100)
        ax.set_ylabel("% of items")
        ax.set_title(title, fontsize=9)
        ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(gen / "fig_rates.pdf")
    plt.close(fig)


def tex_escape(t: str) -> str:
    for a, b in (("\\", "\\textbackslash{}"), ("&", "\\&"), ("%", "\\%"), ("_", "\\_"), ("#", "\\#"), ("$", "\\$"), ("{", "\\{"), ("}", "\\}"), ("~", "\\textasciitilde{}"), ("^", "\\textasciicircum{}")):
        t = t.replace(a, b)
    return t


def write_items_table(items_path: Path, paper: Path) -> None:
    import yaml
    data = yaml.safe_load(items_path.read_text())
    rows = ["\\begin{longtable}{p{2.1cm}p{9.6cm}cc}\\toprule",
            "Item & Realising paper & $d(P)$ & Prior \\\\ \\midrule\\endhead"]
    for it in data["items"]:
        r = it["realising"]
        rows.append(f"{it['id'].removeprefix('T-')} & {tex_escape(r['title'])} & {r['published']} & {len(it.get('prior_work') or [])} \\\\")
    rows.append("\\bottomrule\\end{longtable}")
    gen = paper / "generated"
    gen.mkdir(parents=True, exist_ok=True)
    (gen / "items_table.tex").write_text("\n".join(rows) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--paper", default="docs/paper/latex")
    ap.add_argument("--items", default=None, help="items.yaml, to write the appendix item table")
    ap.add_argument("--exclude-items", default="", help="comma-separated item ids for a sensitivity analysis (written to analysis-sensitivity.json)")
    args = ap.parse_args()
    out, paper = Path(args.out), Path(args.paper)
    if args.items:
        write_items_table(Path(args.items), paper)
    rows = load(out)
    write_item_verdicts(rows, paper)
    if args.exclude_items:
        drop = {x.strip() for x in args.exclude_items.split(",") if x.strip()}
        (out / "analysis-sensitivity.json").write_text(json.dumps({"excluded": sorted(drop), **analyse([r for r in rows if r["item"] not in drop])}, indent=1, default=str))
    res = analyse(rows)
    (out / "analysis.json").write_text(json.dumps(res, indent=1, default=str))
    write_latex(res, paper)
    figures(res, paper)
    print(json.dumps({s: {k: (v["rate"] if isinstance(v, dict) and "rate" in v else None) for k, v in d.items() if isinstance(v, dict) and "rate" in v}
                      for s, d in res["per_system"].items()}, indent=1))


if __name__ == "__main__":
    main()
