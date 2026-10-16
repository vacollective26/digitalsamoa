"""Rules for historical source entries (Village Heritage).

These rules decide whether an entry may be associated with a village or district,
and whether it may ever appear on the public site. The same rules are mirrored in
the site's JavaScript (HeritageRules in src/site.html) as a second line of defence.

Nothing here infers a village from a name. A name match is recorded as a research
lead only and never counts as evidence on its own.
"""

LEVELS = ("village", "district", "uncertain")
EVIDENCE = (
    "source-structure",     # the entry sits under the relevant heading in the source itself (page cited)
    "second-source",        # an independent published or archival source agrees
    "community-confirmed",  # confirmed by the village or district through an agreed process
    "name-match",           # names look alike: a research lead, never sufficient
)
RESEARCH_STATUSES = ("draft", "indexed", "verified-against-source")
PUBLICATION_STATUSES = ("unpublished", "community-review", "approved", "restricted", "withdrawn")
SCOPES = ("citation-only", "summary", "full-text")


def association_valid(assoc):
    """True when an association has enough evidence for its target type."""
    ev = set(assoc.get("evidence") or [])
    unknown = ev - set(EVIDENCE)
    if unknown:
        return False
    real = ev - {"name-match"}
    if not real:
        return False                      # name similarity alone is never enough
    t = assoc.get("targetType")
    if t == "village":
        return "community-confirmed" in real or {"source-structure", "second-source"} <= real
    if t == "district":
        return "source-structure" in real or "community-confirmed" in real
    return False


def effective_level(entry):
    """The level the site may present. Falls back to 'uncertain' unless a matching, valid association exists."""
    level = entry.get("level")
    if level not in ("village", "district"):
        return "uncertain"
    ok = [a for a in entry.get("associations") or [] if a.get("targetType") == level and association_valid(a)]
    return level if ok else "uncertain"


def associated_ids(entry, target_type):
    return [a["targetId"] for a in entry.get("associations") or []
            if a.get("targetType") == target_type and association_valid(a)]


def is_public(entry, sources):
    """Every gate must pass. Missing information always means 'not public'."""
    src = next((s for s in sources if s.get("id") == entry.get("sourceId")), None)
    if not src or not (src.get("rights") or {}).get("confirmedForUse"):
        return False
    if (entry.get("research") or {}).get("status") != "verified-against-source":
        return False
    pub = entry.get("publication") or {}
    if pub.get("status") != "approved" or not pub.get("approvedBy") or not pub.get("approvalRef"):
        return False
    if pub.get("scope", "citation-only") not in SCOPES:
        return False
    if entry.get("sensitivity", "restricted") != "public":
        return False
    if not (entry.get("pageRef") or {}).get("printedPage") and not (entry.get("pageRef") or {}).get("pdfPage"):
        return False                      # a public entry must be citable to a page
    if effective_level(entry) == "uncertain" and not pub.get("publishAsUncertain"):
        return False
    return True


def problems(entry, sources):
    """Human-readable reasons an entry is not public (for the research tools)."""
    out = []
    src = next((s for s in sources if s.get("id") == entry.get("sourceId")), None)
    if not src:
        out.append("unknown source")
    elif not (src.get("rights") or {}).get("confirmedForUse"):
        out.append("source rights not yet confirmed for this use")
    if (entry.get("research") or {}).get("status") != "verified-against-source":
        out.append("not yet verified against the source")
    pub = entry.get("publication") or {}
    if pub.get("status") != "approved":
        out.append("publication status is '%s', not 'approved'" % pub.get("status", "missing"))
    if pub.get("status") == "approved" and (not pub.get("approvedBy") or not pub.get("approvalRef")):
        out.append("approval is missing who approved it or the approval reference")
    if entry.get("sensitivity", "restricted") != "public":
        out.append("sensitivity is not 'public'")
    pr = entry.get("pageRef") or {}
    if not pr.get("printedPage") and not pr.get("pdfPage"):
        out.append("no page reference")
    for a in entry.get("associations") or []:
        if not association_valid(a):
            ev = set(a.get("evidence") or [])
            why = "name similarity only" if ev <= {"name-match"} else "not enough evidence"
            out.append("association to %s '%s' is not valid (%s)" % (a.get("targetType"), a.get("targetId"), why))
    if effective_level(entry) == "uncertain" and entry.get("level") in ("village", "district"):
        out.append("treated as 'uncertain' until a valid %s association exists" % entry.get("level"))
    return out


def public_view(entry):
    """The subset of an approved entry that may be published, limited by its approved scope."""
    pub = entry.get("publication") or {}
    scope = pub.get("scope", "citation-only")
    view = {
        "id": entry["id"],
        "sourceId": entry["sourceId"],
        "pageRef": entry.get("pageRef") or {},
        "headingAsPrinted": entry.get("headingAsPrinted", ""),
        "level": effective_level(entry),
        "villageIds": associated_ids(entry, "village"),
        "districtIds": associated_ids(entry, "district"),
        "evidence": sorted({e for a in entry.get("associations") or [] if association_valid(a) for e in a.get("evidence") or []} - {"name-match"}),
        "variantNames": entry.get("variantNames") or [],
        "approval": {"by": pub.get("approvedBy"), "ref": pub.get("approvalRef"), "on": pub.get("approvedOn", ""), "scope": scope},
    }
    if scope in ("summary", "full-text"):
        view["summary"] = (entry.get("content") or {}).get("summary", "")
    if scope == "full-text":
        view["transcription"] = (entry.get("content") or {}).get("transcription", "")
    return view
