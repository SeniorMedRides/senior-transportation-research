"""Link's automated QUALITY CHECKS. These are not independent validation.
Run: python3 -m unittest discover -s tests -v   (from /workspace/smr-phase1-estimates)
Set SMR_SKIP_FULL=1 to skip the tests that read real PUMS zips."""
import sys, os, json, math, pathlib, unittest, tempfile, zipfile, csv, io
BASE = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(BASE))
import estimate_joint as ej

def mkzip(path, member, header, rows):
    s = io.StringIO(); w = csv.writer(s, lineterminator='\n'); w.writerow(header); w.writerows(rows)
    with zipfile.ZipFile(path, 'w') as z: z.writestr(member, s.getvalue())

class Definitions(unittest.TestCase):
    def test_flags(self):
        hu = {'H1':'0','H2':'2'}
        self.assertIsNone(ej.flags({'SERIALNO':'H1','AGEP':'64','DPHY':'1'}, hu))          # under 65
        self.assertIsNone(ej.flags({'SERIALNO':'GQ9','AGEP':'80','DPHY':'1'}, hu))         # not in HU map
        self.assertEqual(ej.flags({'SERIALNO':'H1','AGEP':'65','DPHY':'1'}, hu),
            {'older_hh':True,'older_amb':True,'older_amb_noveh':True,'older_noveh':True})
        self.assertEqual(ej.flags({'SERIALNO':'H2','AGEP':'90','DPHY':'1'}, hu)['older_amb_noveh'], False)
        self.assertEqual(ej.flags({'SERIALNO':'H1','AGEP':'70','DPHY':'2'}, hu)['older_amb'], False)
    def test_se_formula(self):
        v = [100.0] + [100.0]*40 + [110.0]*40           # 40 reps differ by 10
        self.assertAlmostEqual(ej.se(v), math.sqrt(4/80*40*100))
        self.assertEqual(ej.se([5.0]*81), 0.0)

class JoinLogic(unittest.TestCase):
    def test_synthetic_state(self):
        d = pathlib.Path(tempfile.mkdtemp()); (d/'pums').mkdir()
        mkzip(d/'pums'/'csv_hnv.zip','psam_h32.csv',['SERIALNO','PUMA','TYPEHUGQ','VEH'],
              [['A','00401','1','0'],['B','00401','1','1'],['G','00401','2','b'],['X','99999','1','0']])
        wh = ['PWGTP']+[f'PWGTP{i}' for i in range(1,81)]
        def p(s,puma,age,dphy,w): return [s,puma,age,dphy]+[w]+[w+1]*80
        mkzip(d/'pums'/'csv_pnv.zip','psam_p32.csv',['SERIALNO','PUMA','AGEP','DPHY']+wh,
              [p('A','00401','70','1',10), p('A','00401','40','1',99),   # under 65 excluded
               p('B','00401','80','1',20), p('G','00401','85','1',50),   # GQ excluded
               p('X','99999','75','1',70), p('Z','00401','75','1',30)])  # other PUMA / unmatched serial excluded
        est, n = ej.accumulate_state(d, '32', {'t':{'00401'}})
        e = est['t']
        self.assertEqual(e['older_hh'][0], 30); self.assertEqual(e['older_amb_noveh'][0], 10)
        self.assertEqual(e['older_noveh'][0], 10); self.assertEqual(e['older_hh'][1], 32)
        self.assertEqual(n['t']['older_hh'], 2)
        s = ej.summarize(est['t'], n['t'])
        self.assertAlmostEqual(s['share_amb_in_noveh_hh_pct'], round(100*10/30,2))

@unittest.skipIf(os.environ.get('SMR_SKIP_FULL'), 'full-data tests skipped')
class RealData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out = pathlib.Path(tempfile.mkdtemp())
        ej.main(['--inputs', str(BASE/'inputs'), '--out', str(cls.out)])
        cls.res = {r['area_id']:r for r in json.loads((cls.out/'joint_estimates.json').read_text())['results']}
    def test_feasibility_match_nv_id(self):
        # stored feasibility figures (/workspace/smr-phase2/pums-joint-feasibility.json, copied to reference/)
        old = json.loads((BASE/'reference'/'pums-joint-feasibility.json').read_text())
        for o, aid in zip(old, ['las_vegas','boise']):
            for k, v in o.items():
                if k != 'area': self.assertEqual(self.res[aid][k], v, (aid,k))
        self.assertEqual((self.res['las_vegas']['older_amb_noveh'], self.res['las_vegas']['older_amb_noveh_moe90']), (11666,1007))
        self.assertEqual((self.res['boise']['older_amb_noveh'], self.res['boise']['older_amb_noveh_moe90']), (2621,468))
    def test_nesting(self):
        for aid, r in self.res.items():
            if aid == 'eight_area_total': continue
            self.assertEqual(r['pumas_exactly_nest_in_counties'], aid != 'boise', aid)
            self.assertEqual(r['study_counties_missing'], [])
        self.assertTrue(self.res['boise']['area'].startswith('Boise PUMA region'))
        self.assertEqual(self.res['boise']['extra_counties_in_pumas'], ['16045','16073','16075','16087'])
    def test_internal_consistency(self):
        for r in self.res.values():
            self.assertLessEqual(r['older_amb_noveh'], min(r['older_amb'], r['older_noveh']))
            self.assertLessEqual(r['older_amb'], r['older_hh'])
    def test_total_is_sum(self):
        t = self.res.pop('eight_area_total'); 
        for k in ej.KEYS:
            self.assertAlmostEqual(t['_unrounded_'+k], sum(r['_unrounded_'+k] for r in self.res.values()), places=3)
            self.assertEqual(t[k+'_unweighted_n'], sum(r[k+'_unweighted_n'] for r in self.res.values()))
        self.res['eight_area_total'] = t
    def test_matches_committed_outputs(self):
        self.assertEqual((self.out/'joint_estimates.json').read_bytes(), (BASE/'outputs'/'joint_estimates.json').read_bytes())
        self.assertEqual((self.out/'joint_estimates.csv').read_bytes(), (BASE/'outputs'/'joint_estimates.csv').read_bytes())
