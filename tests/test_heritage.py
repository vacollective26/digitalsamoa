"""Village Heritage tests: association rules, permissions, missing entries and the public-build guard.

Run:  python -m unittest discover -s tests -v
"""
import copy, json, os, shutil, subprocess, sys, tempfile, unittest

import hashlib, re
# SHA-256 prefixes of distinctive words from the withdrawn Patamea transcription (SD-CD-008).
# Stored as hashes so the tests themselves never republish the text.
WITHDRAWN = {"8a95a155c2a67720", "cdb58071b688a792", "b594b4cb1b9d0511", "efb99e6425f80410", "95808378f6e85652"}
WORD = re.compile(r"[A-Za-zĀĒĪŌŪāēīōū‘ʻ']+")


def withdrawn_words(text):
    return sorted({w for w in WORD.findall(text) if hashlib.sha256(w.lower().encode()).hexdigest()[:16] in WITHDRAWN})

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import heritage_rules as R  # noqa: E402
import build as B  # noqa: E402
import heritage as H  # noqa: E402

SOURCES_CONFIRMED = [{"id": "src", "rights": {"confirmedForUse": True}}]
SOURCES_UNCONFIRMED = [{"id": "src", "rights": {"confirmedForUse": False}}]


def entry(**over):
    """A FICTIONAL test entry. Not real fa'alupega or source content."""
    e = {
        "id": "test-entry", "sourceId": "src",
        "pageRef": {"printedPage": "99"}, "headingAsPrinted": "TEST HEADING (fictional)",
        "level": "village",
        "associations": [{"targetType": "village", "targetId": "patamea", "evidence": ["community-confirmed"]}],
        "research": {"status": "verified-against-source"},
        "publication": {"status": "approved", "approvedBy": "Test reviewer", "approvalRef": "TEST-1", "scope": "citation-only"},
        "sensitivity": "public",
        "content": {"summary": "SECRET-SUMMARY", "transcription": "SECRET-TRANSCRIPTION"},
    }
    e.update(over)
    return e


class AssociationRules(unittest.TestCase):
    def test_name_match_alone_is_never_enough(self):
        for t in ("village", "district"):
            self.assertFalse(R.association_valid({"targetType": t, "targetId": "x", "evidence": ["name-match"]}))

    def test_name_match_entry_falls_back_to_uncertain(self):
        e = entry(associations=[{"targetType": "village", "targetId": "patamea", "evidence": ["name-match"]}])
        self.assertEqual(R.effective_level(e), "uncertain")
        self.assertEqual(R.associated_ids(e, "village"), [])

    def test_village_needs_community_or_two_kinds_of_evidence(self):
        ok = lambda ev: R.association_valid({"targetType": "village", "targetId": "v", "evidence": ev})
        self.assertTrue(ok(["community-confirmed"]))
        self.assertTrue(ok(["source-structure", "second-source"]))
        self.assertFalse(ok(["source-structure"]))
        self.assertFalse(ok(["second-source", "name-match"]))

    def test_district_rule(self):
        ok = lambda ev: R.association_valid({"targetType": "district", "targetId": "d", "evidence": ev})
        self.assertTrue(ok(["source-structure"]))
        self.assertTrue(ok(["community-confirmed"]))
        self.assertFalse(ok(["second-source"]))

    def test_unknown_evidence_is_rejected(self):
        self.assertFalse(R.association_valid({"targetType": "village", "targetId": "v", "evidence": ["looks-right"]}))

    def test_levels_stay_distinct(self):
        d = entry(level="district", associations=[{"targetType": "district", "targetId": "gagaemauga", "evidence": ["source-structure"]}])
        self.assertEqual(R.effective_level(d), "district")
        self.assertEqual(R.associated_ids(d, "village"), [])
        # a village-level claim backed only by a district association is NOT village-level
        mixed = entry(level="village", associations=[{"targetType": "district", "targetId": "gagaemauga", "evidence": ["source-structure"]}])
        self.assertEqual(R.effective_level(mixed), "uncertain")


class Permissions(unittest.TestCase):
    def test_fully_approved_entry_is_public(self):
        self.assertTrue(R.is_public(entry(), SOURCES_CONFIRMED))

    def test_unconfirmed_rights_block_everything(self):
        self.assertFalse(R.is_public(entry(), SOURCES_UNCONFIRMED))

    def test_each_gate_blocks(self):
        cases = {
            "unpublished": dict(publication={"status": "unpublished"}),
            "community review": dict(publication={"status": "community-review"}),
            "restricted": dict(publication={"status": "restricted", "approvedBy": "x", "approvalRef": "y"}),
            "withdrawn": dict(publication={"status": "withdrawn", "approvedBy": "x", "approvalRef": "y"}),
            "no approver": dict(publication={"status": "approved", "approvalRef": "y"}),
            "not verified": dict(research={"status": "indexed"}),
            "restricted sensitivity": dict(sensitivity="restricted"),
            "missing sensitivity": {"sensitivity": None},
            "no page": dict(pageRef={}),
            "unknown source": dict(sourceId="nope"),
        }
        for name, over in cases.items():
            e = entry(**over)
            if over.get("sensitivity", 1) is None:
                e.pop("sensitivity")
            with self.subTest(name):
                self.assertFalse(R.is_public(e, SOURCES_CONFIRMED))
                self.assertTrue(R.problems(e, SOURCES_CONFIRMED))

    def test_uncertain_needs_explicit_approval_to_publish(self):
        u = entry(level="uncertain", associations=[])
        self.assertFalse(R.is_public(u, SOURCES_CONFIRMED))
        u["publication"]["publishAsUncertain"] = True
        self.assertTrue(R.is_public(u, SOURCES_CONFIRMED))

    def test_scope_limits_what_is_published(self):
        v = R.public_view(entry())
        self.assertNotIn("summary", v)
        self.assertNotIn("transcription", v)
        v = R.public_view(entry(publication={**entry()["publication"], "scope": "summary"}))
        self.assertEqual(v["summary"], "SECRET-SUMMARY")
        self.assertNotIn("transcription", v)


class CreativeDirectorOverride(unittest.TestCase):
    OV = {"by": "CD", "ref": "SD-CD-X", "covers": ["source-rights", "village-association"]}

    def ov_entry(self, evidence=("source-structure",), **pub):
        e = entry(associations=[{"targetType": "village", "targetId": "patamea", "evidence": list(evidence)}])
        e["publication"] = {**e["publication"], "override": {**self.OV, **pub}}
        return e

    def test_override_publishes_ahead_of_rights_and_village_review(self):
        e = self.ov_entry()
        self.assertTrue(R.is_public(e, SOURCES_UNCONFIRMED))
        self.assertEqual(R.effective_level(e), "village")
        self.assertEqual(R.public_view(e)["override"]["ref"], "SD-CD-X")

    def test_override_never_rescues_a_name_match(self):
        e = self.ov_entry(evidence=("name-match",))
        self.assertEqual(R.effective_level(e), "uncertain")
        self.assertFalse(R.is_public(e, SOURCES_UNCONFIRMED))

    def test_incomplete_or_unknown_override_does_nothing(self):
        for bad in ({"by": ""}, {"ref": ""}, {"covers": []}, {"covers": ["source-rights", "verification"]}):
            with self.subTest(bad):
                self.assertFalse(R.is_public(self.ov_entry(**bad), SOURCES_UNCONFIRMED))

    def test_override_does_not_bypass_other_gates(self):
        for over in (dict(research={"status": "indexed"}), dict(sensitivity="restricted"), dict(pageRef={})):
            e = self.ov_entry(); e.update(over)
            with self.subTest(over):
                self.assertFalse(R.is_public(e, SOURCES_UNCONFIRMED))

    def test_override_never_publishes_text(self):
        for scope in ("summary", "full-text"):
            with self.subTest(scope):
                e = self.ov_entry(); e["publication"]["scope"] = scope
                self.assertFalse(R.is_public(e, SOURCES_UNCONFIRMED))
                self.assertFalse(R.is_public(e, SOURCES_CONFIRMED))   # no community confirmation either

    def test_rights_only_override_still_needs_village_evidence(self):
        e = self.ov_entry(covers=["source-rights"])
        self.assertEqual(R.effective_level(e), "uncertain")
        self.assertFalse(R.is_public(e, SOURCES_UNCONFIRMED))


class TextNeedsCulturalReview(unittest.TestCase):
    def text_entry(self, scope="full-text", review=True):
        e = entry(publication={**entry()["publication"], "scope": scope})
        if review:
            e["culturalReview"] = {"approvedBy": "Village council (test)", "ref": "CR-TEST", "scopesApproved": [scope]}
        return e

    def test_text_is_never_public_without_cultural_review(self):
        for scope in ("summary", "full-text"):
            with self.subTest(scope):
                self.assertFalse(R.is_public(self.text_entry(scope, review=False), SOURCES_CONFIRMED))
                self.assertTrue(R.problems(self.text_entry(scope, review=False), SOURCES_CONFIRMED))

    def test_review_must_cover_the_scope(self):
        e = self.text_entry("full-text")
        e["culturalReview"]["scopesApproved"] = ["summary"]
        self.assertFalse(R.is_public(e, SOURCES_CONFIRMED))

    def test_text_needs_confirmed_rights_and_community_confirmation(self):
        self.assertFalse(R.is_public(self.text_entry(), SOURCES_UNCONFIRMED))
        e = self.text_entry()
        e["associations"] = [{"targetType": "village", "targetId": "patamea", "evidence": ["source-structure", "second-source"]}]
        self.assertFalse(R.is_public(e, SOURCES_CONFIRMED))

    def test_fully_reviewed_text_can_publish(self):
        self.assertTrue(R.is_public(self.text_entry(), SOURCES_CONFIRMED))
        self.assertEqual(R.public_view(self.text_entry())["culturalReview"]["ref"], "CR-TEST")


class ImportFormat(unittest.TestCase):
    def test_imports_are_always_unpublished_and_restricted(self):
        row = {"entry_id": "t1", "source_id": "tusi-faalupega-1981", "printed_page": "1", "level": "village",
               "village_id": "patamea", "village_evidence": "name-match", "research_status": "verified-against-source"}
        e = H.row_to_entry(row)
        self.assertEqual(e["publication"]["status"], "unpublished")
        self.assertEqual(e["sensitivity"], "restricted")
        self.assertEqual(R.effective_level(e), "uncertain")   # name match only

    def test_blank_values_are_not_guessed(self):
        e = H.row_to_entry({"entry_id": "t2", "source_id": "s"})
        self.assertEqual(e["level"], "uncertain")
        self.assertEqual(e["associations"], [])
        self.assertEqual(e["headingAsPrinted"], "")

    def test_bad_values_are_rejected(self):
        with self.assertRaises(ValueError):
            H.row_to_entry({"entry_id": "t3", "source_id": "s", "level": "probably"})
        with self.assertRaises(ValueError):
            H.row_to_entry({"entry_id": "t4", "source_id": "s", "village_id": "x", "village_evidence": "vibes"})


class PublicBuild(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        for d in ("src", "data"):
            shutil.copytree(os.path.join(ROOT, d), os.path.join(self.tmp, d))

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def _write(self, rel, obj):
        p = os.path.join(self.tmp, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(obj, f)

    def _confirm_rights(self):
        p = os.path.join(self.tmp, "data", "heritage", "sources.json")
        s = json.load(open(p, encoding="utf-8"))
        s[0]["rights"]["confirmedForUse"] = True
        json.dump(s, open(p, "w", encoding="utf-8"))

    def test_missing_entries_build_with_empty_profiles(self):
        shutil.rmtree(os.path.join(self.tmp, "data/heritage/approved"))
        out = B.build(root=self.tmp, out=os.path.join(self.tmp, "index.html"))
        p = B.heritage_payload(self.tmp)
        self.assertEqual(p["entries"], [])
        ids = {v["villageId"] for v in p["villages"]}
        self.assertEqual(ids, {"patamea", "leauvaa"})
        self.assertTrue(os.path.exists(out))

    def test_published_record_state(self):
        p = B.heritage_payload(self.tmp)
        self.assertEqual(p["entries"], [])
        checks = {v["villageId"]: v["sourceChecks"][0] for v in p["villages"]}
        self.assertEqual(checks["patamea"]["status"], "entry-under-review")
        self.assertEqual(checks["patamea"]["pageRef"]["printedPage"], "23")
        self.assertEqual(checks["leauvaa"]["status"], "searched-none-found")
        self.assertFalse(p["sources"][0]["rights"]["confirmedForUse"])

    def test_research_folder_never_reaches_public_build(self):
        self._write("research/entries/secret.json", entry(id="RESEARCH-ONLY-ID", headingAsPrinted="RESEARCH-ONLY-HEADING",
                                                          publication={"status": "unpublished"}))
        out = B.build(root=self.tmp, out=os.path.join(self.tmp, "index.html"))
        html = open(out, encoding="utf-8").read()
        self.assertNotIn("RESEARCH-ONLY-ID", html)
        self.assertNotIn("RESEARCH-ONLY-HEADING", html)
        prev = B.build(root=self.tmp, research=True, out=os.path.join(self.tmp, "preview.html"))
        self.assertIn("RESEARCH-ONLY-ID", open(prev, encoding="utf-8").read())

    def test_unapproved_file_in_approved_folder_stops_the_build(self):
        self._write("data/heritage/approved/bad.json", entry(publication={"status": "community-review"}))
        with self.assertRaises(B.BuildError):
            B.build(root=self.tmp, out=os.path.join(self.tmp, "index.html"))

    def test_approved_entry_needs_confirmed_rights(self):
        shutil.rmtree(os.path.join(self.tmp, "data/heritage/approved"))
        self._write("data/heritage/approved/ok.json", entry(sourceId="tusi-faalupega-1981"))
        with self.assertRaises(B.BuildError):
            B.build(root=self.tmp, out=os.path.join(self.tmp, "index.html"))
        self._confirm_rights()
        out = B.build(root=self.tmp, out=os.path.join(self.tmp, "index.html"))
        html = open(out, encoding="utf-8").read()
        self.assertIn("TEST HEADING (fictional)", html)
        self.assertNotIn("SECRET-SUMMARY", html)          # citation-only scope
        self.assertNotIn("SECRET-TRANSCRIPTION", html)


class RepositoryGuard(unittest.TestCase):
    def test_research_is_ignored_by_git(self):
        r = subprocess.run(["git", "check-ignore", "research/entries/x.json", "research-preview.html"],
                           cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(len(r.stdout.split()), 2)

    def test_no_unapproved_records_are_tracked(self):
        files = subprocess.run(["git", "ls-files", "data"], cwd=ROOT, capture_output=True, text=True).stdout.split()
        sources = json.load(open(os.path.join(ROOT, "data/heritage/sources.json"), encoding="utf-8"))
        for f in files:
            if f.startswith("data/heritage/approved/") and f.endswith(".json"):
                e = json.load(open(os.path.join(ROOT, f), encoding="utf-8"))
                self.assertTrue(R.is_public(e, sources), f)

    def test_withdrawn_transcription_is_in_no_tracked_file(self):
        """Canary phrases from the withdrawn Patamea transcription (SD-CD-008) must not be in the public repo."""
        files = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True).stdout.split()
        hits = []
        for f in files:
            try:
                txt = open(os.path.join(ROOT, f), encoding="utf-8").read()
            except (UnicodeDecodeError, IsADirectoryError, FileNotFoundError):
                continue
            hits += ["%s: %d withdrawn word(s)" % (f, len(withdrawn_words(txt)))] if withdrawn_words(txt) else []
        self.assertEqual(hits, [])

    def test_committed_site_matches_a_fresh_build(self):
        tmp = tempfile.mkdtemp()
        try:
            out = B.build(out=os.path.join(tmp, "index.html"))
            self.assertEqual(open(out, encoding="utf-8").read(), open(os.path.join(ROOT, "index.html"), encoding="utf-8").read(),
                             "index.html is out of date: run python tools/build.py")
        finally:
            shutil.rmtree(tmp)


if __name__ == "__main__":
    unittest.main()
