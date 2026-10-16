"""Research tools for indexing historical sources (Village Heritage).

    python tools/heritage.py import research/index.csv   # CSV rows -> research/entries/<id>.json
    python tools/heritage.py check                        # report what each research entry still needs
    python tools/heritage.py promote <entry-id>           # copy an approved, verified entry into the public data

Research material lives in research/, which git ignores. Only `promote` moves an entry
into data/heritage/approved/, and it refuses unless every publication gate passes.
"""
import csv, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import heritage_rules as R  # noqa: E402

RESEARCH = os.path.join(ROOT, "research", "entries")
APPROVED = os.path.join(ROOT, "data", "heritage", "approved")
SOURCES = os.path.join(ROOT, "data", "heritage", "sources.json")

LIST_SEP = ";"


def sources():
    with open(SOURCES, encoding="utf-8") as f:
        return json.load(f)


def split(v):
    return [x.strip() for x in (v or "").split(LIST_SEP) if x.strip()]


def row_to_entry(row):
    """One CSV row -> one entry record. Unknown or blank values stay blank; nothing is guessed."""
    assoc = []
    for kind in ("village", "district"):
        tid = (row.get("%s_id" % kind) or "").strip()
        if tid:
            assoc.append({"targetType": kind, "targetId": tid,
                          "evidence": split(row.get("%s_evidence" % kind)),
                          "confirmedBy": (row.get("%s_confirmed_by" % kind) or "").strip()})
    for e in assoc:
        bad = set(e["evidence"]) - set(R.EVIDENCE)
        if bad:
            raise ValueError("row %s: unknown evidence %s" % (row.get("entry_id"), sorted(bad)))
    level = (row.get("level") or "uncertain").strip()
    if level not in R.LEVELS:
        raise ValueError("row %s: level must be one of %s" % (row.get("entry_id"), R.LEVELS))
    return {
        "id": row["entry_id"].strip(),
        "sourceId": row["source_id"].strip(),
        "pageRef": {"printedPage": (row.get("printed_page") or "").strip(),
                    "pdfPage": int(row["pdf_page"]) if (row.get("pdf_page") or "").strip().isdigit() else None,
                    "section": (row.get("section_heading") or "").strip()},
        "headingAsPrinted": (row.get("heading_as_printed") or "").strip(),
        "level": level,
        "associations": assoc,
        "variantNames": [{"name": n, "kind": "variant"} for n in split(row.get("variant_names"))],
        "content": {"summary": (row.get("summary") or "").strip(), "transcription": ""},
        "provenance": {"indexedBy": (row.get("indexed_by") or "").strip(), "indexedOn": (row.get("indexed_on") or "").strip(),
                       "method": (row.get("method") or "").strip(), "checkedBy": (row.get("checked_by") or "").strip()},
        "research": {"status": (row.get("research_status") or "draft").strip(), "notes": (row.get("notes") or "").strip()},
        "publication": {"status": "unpublished"},   # imports are ALWAYS unpublished
        "sensitivity": "restricted",                  # and restricted until reviewed
    }


def cmd_import(path):
    os.makedirs(RESEARCH, exist_ok=True)
    n = 0
    with open(path, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            if not (row.get("entry_id") or "").strip():
                continue
            e = row_to_entry(row)
            with open(os.path.join(RESEARCH, e["id"] + ".json"), "w", encoding="utf-8") as out:
                json.dump(e, out, ensure_ascii=False, indent=2)
            n += 1
    print("Imported %d research entries into research/entries (unpublished, restricted)." % n)


def load_research():
    out = []
    if os.path.isdir(RESEARCH):
        for name in sorted(os.listdir(RESEARCH)):
            if name.endswith(".json"):
                with open(os.path.join(RESEARCH, name), encoding="utf-8") as f:
                    out.append(json.load(f))
    return out


def cmd_check():
    src = sources()
    entries = load_research()
    if not entries:
        print("No research entries yet.")
    for e in entries:
        p = R.problems(e, src)
        print("%-28s %-9s %s" % (e["id"], R.effective_level(e), "ready to promote" if not p else "; ".join(p)))


def cmd_promote(entry_id):
    src = sources()
    e = next((x for x in load_research() if x["id"] == entry_id), None)
    if not e:
        sys.exit("No research entry '%s'." % entry_id)
    if not R.is_public(e, src):
        sys.exit("Not promoted. Still needed: " + "; ".join(R.problems(e, src)))
    os.makedirs(APPROVED, exist_ok=True)
    with open(os.path.join(APPROVED, entry_id + ".json"), "w", encoding="utf-8") as f:
        json.dump(e, f, ensure_ascii=False, indent=2)
    print("Promoted %s. Run `python tools/build.py`, review, then commit." % entry_id)


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ("import", "check", "promote"):
        sys.exit(__doc__)
    if sys.argv[1] == "import":
        cmd_import(sys.argv[2])
    elif sys.argv[1] == "check":
        cmd_check()
    else:
        cmd_promote(sys.argv[2])
