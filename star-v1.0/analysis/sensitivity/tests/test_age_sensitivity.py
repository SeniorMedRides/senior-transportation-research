"""Link's quality checks for the sensitivity analysis (NOT independent validation).
Run from sensitivity/: python3 -m unittest discover -s tests -v   (reads outputs/ produced by age_sensitivity.py)"""
import json, csv, pathlib, unittest, sys
B = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(B)); sys.path.insert(0, str(B.parent))
import age_sensitivity as a
class T(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = json.loads((B/'outputs'/'sensitivity.json').read_text())
        cls.j = {r['area_id']:r for r in json.loads((B.parent/'outputs'/'joint_estimates.json').read_text())['results']}
    def test_age_groups(self):
        self.assertEqual([a.age_group(x) for x in (64,65,74,75,84,85,99)], [None,'65_74','65_74','75_84','75_84','85_plus','85_plus'])
    def test_age_groups_sum_to_joint(self):
        rows = self.s['age_specific']
        for aid, r in self.j.items():
            for k in ['older_hh','older_amb','older_amb_noveh','older_noveh']:
                tot = sum(x[k] for x in rows if x['area_id']==aid)
                self.assertLessEqual(abs(tot - r[k]), 2, (aid,k))   # rounding of 3 groups
                self.assertEqual(sum(x[k+'_unweighted_n'] for x in rows if x['area_id']==aid), r[k+'_unweighted_n'])
    def test_crude_matches_joint(self):
        for r in self.s['age_standardized']:
            j = self.j[r['area_id']]
            self.assertEqual(r['crude_share_amb_in_noveh_hh_pct'], j['share_amb_in_noveh_hh_pct'])
            self.assertEqual(r['crude_share_older_in_noveh_hh_pct'], j['share_older_in_noveh_hh_pct'])
            self.assertEqual(r['crude_share_amb_in_noveh_hh_moe90_pp'], j['share_amb_in_noveh_hh_moe90_pp'])
    def test_standard_sums_to_one_and_total_identity(self):
        for S in ('standard_population_S1','standard_population_S2'):
            self.assertAlmostEqual(sum(self.s[S].values()), 1.0, places=5)
        t = [r for r in self.s['age_standardized'] if r['area_id']=='eight_area_total'][0]
        # standardizing the total to its own distribution reproduces the crude rate
        self.assertEqual(t['std_share_older_in_noveh_hh_pct'], t['crude_share_older_in_noveh_hh_pct'])
        self.assertEqual(t['std_alt_share_amb_in_noveh_hh_pct'], t['crude_share_amb_in_noveh_hh_pct'])
    def test_holm(self):
        t = a.holm([{'p':0.01},{'p':0.04},{'p':0.03},{'p':0.5}], alpha=0.10)
        self.assertEqual([x['holm_significant'] for x in t], [True,True,True,False])
        t = a.holm([{'p':0.03},{'p':0.03},{'p':0.2}], alpha=0.10)
        self.assertEqual([x['holm_significant'] for x in t], [True,True,False])
        t = a.holm([{'p':0.04},{'p':0.06}], alpha=0.10)   # 0.04<=0.05 yes; 0.06<=0.10 yes
        self.assertEqual([x['holm_significant'] for x in t], [True,True])
    def test_family_sizes(self):
        fam = [c['family'] for c in self.s['comparisons']]
        self.assertEqual((fam.count('1'),fam.count('2'),fam.count('3')), (24,28,9))
