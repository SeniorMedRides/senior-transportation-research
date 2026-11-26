"""v1.1 quality checks for the age-standardized with/without contrast (author checks, not independent validation)."""
import json, csv, pathlib, unittest
B = pathlib.Path(__file__).resolve().parents[1]; V10 = pathlib.Path(__file__).resolve().parents[3] / 'v1.0-package' / 'sensitivity'
class T(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        d = json.loads((B/'outputs'/'with_without_std.json').read_text())
        cls.d = d; cls.std = {r['area_id']:r for r in d['age_standardized']}
        cls.crude = {r['area_id']:r for r in json.loads((B.parent/'outputs'/'with_without_contrast.json').read_text())['results']}
        cls.s = json.loads((B/'outputs'/'sensitivity.json').read_text())
    def test_crude_matches_contrast_output(self):
        for aid, r in self.std.items():
            c = self.crude[aid]
            self.assertEqual(r['crude_share_without_pct'], c['share_without_amb_in_noveh_hh_pct'])
            self.assertEqual(r['crude_diff_pp'], c['diff_with_minus_without_pp'])
            self.assertEqual(r['crude_diff_moe90_pp'], c['diff_with_minus_without_moe90_pp'])
            self.assertEqual(r['crude_ratio'], c['ratio_with_to_without'])
    def test_std_with_matches_v10_standardized(self):
        v = {r['area_id']:r for r in self.s['age_standardized']}
        for aid, r in self.std.items():
            self.assertEqual(r['std_share_with_pct'], v[aid]['std_share_amb_in_noveh_hh_pct'])
            self.assertEqual(r['std_share_with_moe90_pp'], v[aid]['std_share_amb_in_noveh_hh_moe90_pp'])
    def test_same_standard(self):
        self.assertEqual(self.d['standard_population_S1'], self.s['standard_population_S1'])
    def test_by_age_rows(self):
        self.assertEqual(len(self.d['by_age']), 27)
        self.assertTrue(all(r['with_amb_noveh_unweighted_n'] is not None for r in self.d['by_age']))
    def test_existing_sensitivity_outputs_byte_identical_to_v10(self):
        if not V10.exists(): self.skipTest('v1.0 not present')
        for f in ['age_specific.csv','age_standardized.csv','comparisons.csv','sensitivity.json']:
            self.assertEqual((B/'outputs'/f).read_bytes(), (V10/'outputs'/f).read_bytes(), f)
