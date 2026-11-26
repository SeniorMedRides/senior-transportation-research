"""v1.1 quality checks by the author (Link). Not independent validation.
Covers validator notes 1-3: CSV/dictionary reconciliation, --out protection, with/without contrast.
Reads bundled v1.1 outputs/ and the frozen v1.0 package at ../v1.0-package/ (read only; sibling of analysis/)."""
import sys, os, csv, json, math, io, pathlib, unittest, tempfile
BASE = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(BASE))
V10 = pathlib.Path(__file__).resolve().parents[2] / 'v1.0-package'
import estimate_joint as ej, supplementary_difference as sd, with_without_contrast as ww

class Note1CsvDictionary(unittest.TestCase):
    def test_total_method_column(self):
        rows = list(csv.DictReader(open(BASE/'outputs'/'joint_estimates.csv')))
        self.assertIn('total_method', rows[0])
        self.assertTrue(rows[-1]['total_method'].startswith('Replicate-by-replicate'))
        self.assertTrue(all(r['total_method']=='' for r in rows[:-1]))
        self.assertIn('| total_method |', (BASE/'DATA_DICTIONARY.md').read_text())
    @unittest.skipUnless(V10.exists(), 'v1.0 package not present')
    def test_csv_otherwise_identical_to_v10(self):
        new = list(csv.reader(open(BASE/'outputs'/'joint_estimates.csv'))); old = list(csv.reader(open(V10/'outputs'/'joint_estimates.csv')))
        self.assertEqual(new[0][:-1], old[0]); self.assertEqual(new[0][-1], 'total_method')
        self.assertEqual([r[:-1] for r in new], old)
    @unittest.skipUnless(V10.exists(), 'v1.0 package not present')
    def test_json_and_supplementary_byte_identical_to_v10(self):
        for f in ['joint_estimates.json','supplementary_difference.json']:
            self.assertEqual((BASE/'outputs'/f).read_bytes(), (V10/'outputs'/f).read_bytes(), f)

class Note2OutProtection(unittest.TestCase):
    def test_refuses_bundled(self):
        with self.assertRaises(SystemExit): sd.out_dir('outputs', False)
        with self.assertRaises(SystemExit): sd.out_dir(str(BASE/'outputs'), False)
    def test_default_and_custom(self):
        d = tempfile.mkdtemp(); self.assertEqual(sd.out_dir(d, False), pathlib.Path(d))
        import argparse, inspect
        self.assertIn("default='rerun'", inspect.getsource(sd.main)); self.assertIn("default='rerun'", inspect.getsource(ww.main))

class Note3Contrast(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = {x['area_id']:x for x in json.loads((BASE/'outputs'/'with_without_contrast.json').read_text())['results']}
        cls.j = {x['area_id']:x for x in json.loads((BASE/'outputs'/'joint_estimates.json').read_text())['results']}
    def test_synthetic_formula(self):
        e = {'older_hh':[100.0]*81,'older_amb':[20.0]*81,'older_amb_noveh':[5.0]*81,'older_noveh':[13.0]*81}
        c,_ = ww.contrast(e)
        self.assertEqual(c['share_with_amb_in_noveh_hh_pct'], 25.0); self.assertEqual(c['share_without_amb_in_noveh_hh_pct'], 10.0)
        self.assertEqual(c['diff_with_minus_without_pp'], 15.0); self.assertEqual(c['ratio_with_to_without'], 2.5)
        self.assertEqual(c['diff_with_minus_without_moe90_pp'], 0.0)
    def test_validator_reported_total(self):
        t = self.r['eight_area_total']
        self.assertEqual((t['share_with_amb_in_noveh_hh_pct'], t['share_without_amb_in_noveh_hh_pct'], t['share_without_amb_in_noveh_hh_moe90_pp'],
                          t['diff_with_minus_without_pp'], t['diff_with_minus_without_moe90_pp']), (13.46, 4.46, 0.13, 9.0, 0.51))
    def test_every_area_difference_exceeds_moe(self):
        self.assertTrue(all(x['diff_exceeds_moe90'] for x in self.r.values()))
    def test_matches_validator_independent_csv(self):
        p = pathlib.Path(__file__).resolve().parents[2] / 'independent' / 'indep_estimates.csv'
        if not p.exists(): self.skipTest('validator evidence not present')
        for v in csv.DictReader(open(p)):
            x = self.r[v['area_id']]
            self.assertAlmostEqual(x['share_without_amb_in_noveh_hh_pct'], float(v['x_share_nonamb_in_noveh_hh_pct']), places=2)
            self.assertAlmostEqual(x['share_without_amb_in_noveh_hh_moe90_pp'], float(v['x_share_nonamb_moe90_pp']), places=2)
            self.assertAlmostEqual(x['diff_with_minus_without_pp'], float(v['x_diff_amb_vs_nonamb_pp']), places=2)
            self.assertAlmostEqual(x['diff_with_minus_without_moe90_pp'], float(v['x_diff_amb_vs_nonamb_moe90_pp']), places=2)
    def test_consistent_with_joint(self):
        for aid, x in self.r.items():
            j = self.j[aid]
            self.assertEqual(x['share_with_amb_in_noveh_hh_pct'], j['share_amb_in_noveh_hh_pct'])
            self.assertLessEqual(abs(x['older_without_amb'] - (j['older_hh']-j['older_amb'])), 1)
            self.assertLessEqual(abs(x['older_without_amb_noveh'] - (j['older_noveh']-j['older_amb_noveh'])), 1)
            # the all-65+ share lies between the with and without shares
            self.assertTrue(x['share_without_amb_in_noveh_hh_pct'] <= j['share_older_in_noveh_hh_pct'] <= x['share_with_amb_in_noveh_hh_pct'])

@unittest.skipIf(os.environ.get('SMR_SKIP_FULL'), 'full-data tests skipped')
class RerunReproducible(unittest.TestCase):
    def test_rerun_contrast_to_tempdir_identical(self):
        d = tempfile.mkdtemp(); ww.main(['--out', d])
        for f in ['with_without_contrast.json','with_without_contrast.csv']:
            self.assertEqual((pathlib.Path(d)/f).read_bytes(), (BASE/'outputs'/f).read_bytes(), f)
