"""Village Heritage rendering tests in a real browser (Playwright + Chromium).

Skipped automatically if Playwright isn't installed.
Optional: SD_CHROMIUM=/path/to/chrome   SD_THREE_JS=/path/to/three.min.js (offline copy of the 3D library)
"""
import json, os, shutil, sys, tempfile, unittest
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import build as B  # noqa: E402

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover
    sync_playwright = None

TEPAPA = "https://collections.tepapa.govt.nz/object/1094507"


def fictional(id_, level, assoc, heading, **pub):
    """FICTIONAL fixtures for layout tests only. Not real fa'alupega or source content."""
    return {"id": id_, "sourceId": "tusi-faalupega-1981", "pageRef": {"printedPage": "0"},
            "headingAsPrinted": heading, "level": level, "associations": assoc,
            "research": {"status": "verified-against-source"}, "sensitivity": "public",
            "publication": {"status": "approved", "approvedBy": "Test reviewer", "approvalRef": "TEST", "scope": "citation-only", **pub}}


@unittest.skipIf(sync_playwright is None, "Playwright not installed")
class HeritageRendering(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        cls.real = B.build(out=os.path.join(cls.tmp, "real.html"))
        fx = os.path.join(cls.tmp, "fx")
        for d in ("src", "data"):
            shutil.copytree(os.path.join(ROOT, d), os.path.join(fx, d))
        sp = os.path.join(fx, "data/heritage/sources.json")
        s = json.load(open(sp, encoding="utf-8")); s[0]["rights"]["confirmedForUse"] = True
        json.dump(s, open(sp, "w", encoding="utf-8"))
        ap = os.path.join(fx, "data/heritage/approved")
        shutil.rmtree(ap); os.makedirs(ap)
        for e in [
            fictional("fx-v", "village", [{"targetType": "village", "targetId": "patamea", "evidence": ["community-confirmed"]}], "FIXTURE VILLAGE ENTRY"),
            fictional("fx-d", "district", [{"targetType": "district", "targetId": "gagaemauga", "evidence": ["source-structure"]}], "FIXTURE DISTRICT ENTRY"),
            fictional("fx-u", "uncertain", [{"targetType": "district", "targetId": "gagaemauga", "evidence": ["source-structure"]}], "FIXTURE UNCERTAIN ENTRY", publishAsUncertain=True),
            fictional("fx-n", "village", [{"targetType": "village", "targetId": "patamea", "evidence": ["name-match"]}], "FIXTURE NAME MATCH ONLY", publishAsUncertain=True),
        ]:
            json.dump(e, open(os.path.join(ap, e["id"] + ".json"), "w", encoding="utf-8"))
        cls.fixture = B.build(root=fx, out=os.path.join(cls.tmp, "fixture.html"))
        cls.pw = sync_playwright().start()
        kw = {"args": ["--use-angle=swiftshader", "--enable-unsafe-swiftshader"]}
        if os.environ.get("SD_CHROMIUM"):
            kw["executable_path"] = os.environ["SD_CHROMIUM"]
        cls.browser = cls.pw.chromium.launch(**kw)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close(); cls.pw.stop(); shutil.rmtree(cls.tmp)

    def open(self, path, hash_, width=1280):
        pg = self.browser.new_page(viewport={"width": width, "height": 860})
        if os.environ.get("SD_THREE_JS"):
            pg.route("**/three.min.js", lambda r: r.fulfill(path=os.environ["SD_THREE_JS"], content_type="application/javascript"))
        pg.route("https://fonts.googleapis.com/**", lambda r: r.abort())
        self.errors = []
        pg.on("pageerror", lambda e: self.errors.append(str(e)))
        pg.goto("file://" + path + "#" + hash_)
        pg.wait_for_selector("#heritage-host .heritage", timeout=15000)
        return pg

    def test_patamea_shows_citation_and_review_pending_without_text(self):
        pg = self.open(self.real, "patamea-history")
        self.assertEqual(pg.locator(".hentry").count(), 0)
        self.assertIn("community review pending", pg.text_content(".hs-check").lower())
        box = pg.text_content(".hreview")
        self.assertIn("p. 23", box)
        self.assertIn("Patamea", box)
        self.assertEqual(pg.locator(".hreview a.cite").get_attribute("href"), TEPAPA)
        body = pg.text_content("body")
        from test_heritage import withdrawn_words
        self.assertEqual(withdrawn_words(body), [])
        self.assertEqual(self.errors, [])
        pg.close()

    def test_empty_state_for_leauvaa(self):
        for vid, name in (("leauvaa", "Le‘auva‘a"),):
            with self.subTest(vid):
                pg = self.open(self.real, vid + "-history")
                self.assertEqual(pg.locator("[data-htab]").count(), 3)
                self.assertIn("No historical entry for " + name, pg.text_content(".hempty"))
                self.assertEqual(pg.locator(".hentry").count(), 0)
                self.assertIn("no entry identified", pg.text_content(".hs-check").lower())
                link = pg.locator(".hsource a.cite")
                self.assertEqual(link.get_attribute("href"), TEPAPA)
                self.assertEqual(link.get_attribute("target"), "_blank")
                self.assertIn("noopener", link.get_attribute("rel"))
                self.assertEqual(self.errors, [])
                pg.close()

    def test_three_views_and_keyboard(self):
        pg = self.open(self.real, "patamea-history")
        pg.click("#ht-understand")
        self.assertIn("Draft explanation", pg.text_content("#hpanel"))
        pg.focus("#ht-understand"); pg.keyboard.press("ArrowRight")
        self.assertEqual(pg.get_attribute("#ht-living", "aria-selected"), "true")
        self.assertIn("Living knowledge from Patamea", pg.text_content("#hpanel"))
        pg.close()

    def test_levels_render_separately_and_name_match_is_not_linked(self):
        pg = self.open(self.fixture, "patamea-history")
        groups = pg.locator(".hgroup")
        texts = [groups.nth(i).text_content() for i in range(groups.count())]
        self.assertEqual(len(texts), 3)
        self.assertIn("FIXTURE VILLAGE ENTRY", texts[0]); self.assertIn("About Patamea", texts[0])
        self.assertIn("FIXTURE DISTRICT ENTRY", texts[1]); self.assertNotIn("FIXTURE VILLAGE ENTRY", texts[1])
        self.assertIn("FIXTURE UNCERTAIN ENTRY", texts[2])
        self.assertNotIn("FIXTURE NAME MATCH ONLY", pg.text_content("#hpanel"))
        for i in range(pg.locator(".hentry a.cite").count()):
            self.assertEqual(pg.locator(".hentry a.cite").nth(i).get_attribute("href"), TEPAPA)
        pg.close()
        pg = self.open(self.fixture, "leauvaa-history")
        txt = pg.text_content("#hpanel")
        self.assertNotIn("FIXTURE VILLAGE ENTRY", txt)        # village-level entry belongs to Patamea only
        self.assertIn("FIXTURE DISTRICT ENTRY", txt)
        pg.close()

    def test_phone_layout_has_no_sideways_scroll(self):
        pg = self.open(self.real, "patamea-history", width=390)
        self.assertFalse(pg.evaluate("document.documentElement.scrollWidth>innerWidth"))
        pg.close()


if __name__ == "__main__":
    unittest.main()
