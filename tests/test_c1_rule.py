import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import datadecision as dd

# Fixture built from the phrase of PMID 39468688 ("human AD brain and in a tauopathy mouse model").
AD_MOUSE = "Title. We show APOE4 alters endosomal pH in human AD brain and in a tauopathy mouse model compared with APOE3."
AD_MOUSE_IPSC = AD_MOUSE + " Findings were confirmed in iPSC-derived astrocytes from non-AD donors."
IPSC_ONLY = "APOE4 iPSC-derived astrocytes show lower endosomal pH than APOE3 isogenic cells."
YES = {"v": "yes", "q": "x"}


class C1Rule(unittest.TestCase):
    def test_ad_brain_plus_mouse_fails(self):
        c, chg = dd.c1_rule(AD_MOUSE, dict(YES))
        self.assertEqual(c["v"], "no")
        self.assertTrue(chg)

    def test_ipsc_exception_is_partial(self):
        c, chg = dd.c1_rule(AD_MOUSE_IPSC, dict(YES))
        self.assertEqual(c["v"], "yes")
        self.assertIn("iPSC findings only", c["partial"])
        self.assertFalse(chg)

    def test_plain_ipsc_untouched(self):
        c, chg = dd.c1_rule(IPSC_ONLY, dict(YES))
        self.assertEqual(c, YES)
        self.assertFalse(chg)

if __name__ == "__main__":
    unittest.main()
