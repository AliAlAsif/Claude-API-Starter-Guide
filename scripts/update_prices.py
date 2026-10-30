#!/usr/bin/env python3
"""Update prices.json from Anthropic's pricing page (Markdown version).

- Reads the table whose header has "Base Input Tokens" and "Output Tokens".
- Takes the FIRST dollar amount in each cell (the base / up-to-100K rate).
- Writes prices.json only when a price changed, and writes pr_body.md for the PR.
- Exits with an error if a model row cannot be found, so a layout change
  fails loudly instead of publishing wrong prices.
Standard library only.
"""
import datetime
import json
import pathlib
import re
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
PRICES = ROOT / "prices.json"
BODY = ROOT / "pr_body.md"
AMOUNT = re.compile(r"\$\s*([0-9]+(?:\.[0-9]+)?)")


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "price-updater (GitHub Actions)"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", "replace")


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def tables(md):
    """Yield (input_col, output_col, rows) for each pricing table found."""
    lines = md.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.lstrip().startswith("|") and "Base Input" in line and "Output Tokens" in line:
            head = cells(line)
            ic = next(n for n, c in enumerate(head) if "Base Input" in c)
            oc = next(n for n, c in enumerate(head) if c.startswith("Output"))
            rows, j = [], i + 1
            while j < len(lines) and lines[j].lstrip().startswith("|"):
                if not re.match(r"^\s*\|[\s:|-]+\|?\s*$", lines[j]):  # skip |---|---|
                    rows.append(cells(lines[j]))
                j += 1
            yield ic, oc, rows
            i = j
        else:
            i += 1


def first_amount(cell):
    m = AMOUNT.search(cell)
    return float(m.group(1)) if m else None


def find_price(md, patterns):
    if isinstance(patterns, str):
        patterns = [patterns]
    for pat in patterns:
        rx = re.compile(pat, re.I)
        for ic, oc, rows in tables(md):
            for row in rows:
                if row and rx.search(row[0]) and len(row) > max(ic, oc):
                    inp, out = first_amount(row[ic]), first_amount(row[oc])
                    if inp is not None and out is not None:
                        return inp, out, row[0]
    return None


def main():
    data = json.loads(PRICES.read_text(encoding="utf-8"))
    md = fetch(data["source_md"])
    changes, warnings = [], []

    for m in data["models"]:
        found = find_price(md, m.get("match") or re.escape(m["name"]))
        if not found:
            sys.exit(f"ERROR: no price row found for {m['name']} (match={m.get('match')}). "
                     "The page layout or model name may have changed.")
        new_in, new_out, label = found
        print(f"{m['name']}: matched '{label}' -> input ${new_in}, output ${new_out}")
        if new_in <= 0 or new_out <= 0 or new_out < new_in:
            sys.exit(f"ERROR: implausible prices for {m['name']}: {new_in} / {new_out}")
        if abs(new_out / new_in - 5) > 0.05:
            warnings.append(f"{m['name']}: output is {new_out / new_in:.2f}x input, not 5x. "
                            "Update the '5x' wording in index.html.")
        if (new_in, new_out) != (m["input"], m["output"]):
            for old, new, what in ((m["input"], new_in, "input"), (m["output"], new_out, "output")):
                if old > 0 and not 0.5 <= new / old <= 1.5:
                    warnings.append(f"{m['name']}: large {what} price change (${old} -> ${new}). Double-check.")
            changes.append((m["name"], m["input"], m["output"], new_in, new_out))
            m["input"], m["output"] = new_in, new_out

    if not changes:
        BODY.unlink(missing_ok=True)
        print("No price changes.")
        return

    data["updated"] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    PRICES.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    body = ["Anthropic's pricing page shows different prices from `prices.json`.", "",
            "| Model | Input (old -> new) | Output (old -> new) |", "|---|---|---|"]
    for name, oi, oo, ni, no in changes:
        body.append(f"| {name} | ${oi} -> ${ni} | ${oo} -> ${no} |")
    if warnings:
        body += ["", "**Warnings**"] + [f"- {w}" for w in warnings]
    body += ["", "**Before merging:** compare with " + data["source"],
             "Long-context rates and the \"best for\" text are not checked automatically."]
    BODY.write_text("\n".join(body) + "\n", encoding="utf-8")
    print(f"{len(changes)} model(s) changed; wrote prices.json and pr_body.md")


if __name__ == "__main__":
    main()
