import base64,copy,json,unittest
from pathlib import Path
from catalog_history import Crypto,read,catalog,release,add_history,advance,assert_successor
ROOT=Path(__file__).resolve().parents[2]
class CatalogHistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.crypto=Crypto();cls.env=read(ROOT/'catalogs/fmgworld.json');cls.data=catalog(cls.crypto,cls.env)
        cls.entry=next(e for e in cls.data['versions'] if e['patch_history'])
    def test_legacy_latest_patch_still_present(self):
        self.assertGreaterEqual(len(self.data['versions']),4)
        self.assertGreaterEqual(release(self.crypto,self.entry['release'],'fmgworld')['version'],17)
        self.assertTrue({16,15}.issubset({x['revision'] for x in self.entry['patch_history']}))
    def test_tampered_outer_signature_rejected(self):
        broken=copy.deepcopy(self.env);d=copy.deepcopy(self.data);d['catalog_version']+=1
        broken['signed_data']=base64.b64encode(json.dumps(d).encode()).decode()
        with self.assertRaises(Exception):self.crypto.verify(broken)
    def test_cross_game_history_rejected(self):
        other=catalog(self.crypto,read(ROOT/'catalogs/realmofevergrow.json'))
        with self.assertRaises(ValueError):add_history(self.crypto,self.data,[other['versions'][0]['release']])
    def test_other_original_apk_rejected(self):
        sha=release(self.crypto,self.entry['release'],'fmgworld')['source_sha256']
        other=next(e for e in self.data['versions'] if release(self.crypto,e['release'],'fmgworld')['source_sha256']!=sha)
        with self.assertRaises(ValueError):release(self.crypto,other['release'],'fmgworld',sha)
    def test_history_cannot_be_published_as_latest(self):
        with self.assertRaises(ValueError):advance(self.crypto,self.data,self.entry['patch_history'][0]['release'],self.entry['version_name'],self.entry['version_code'],self.entry['label'])
    def test_history_removal_rejected(self):
        after=copy.deepcopy(self.data);after['catalog_version']+=1
        next(e for e in after['versions'] if e['patch_history'])['patch_history'].pop()
        with self.assertRaises(ValueError):assert_successor(self.crypto,self.data,after)
    def test_wrong_original_version_metadata_rejected(self):
        with self.assertRaises(ValueError):advance(self.crypto,self.data,self.entry['release'],self.entry['version_name'],self.entry['version_code']+1,self.entry['label'])
    def test_idempotent_history_and_preserving_all_originals(self):
        duplicate=self.entry['patch_history'][0]['release']
        after=add_history(self.crypto,self.data,[duplicate,duplicate])
        self.assertEqual(self.data,after)
        after=advance(self.crypto,self.data,self.entry['release'],self.entry['version_name'],self.entry['version_code'],self.entry['label'])
        self.assertEqual(len(self.data['versions']),len(after['versions']));assert_successor(self.crypto,self.data,after)
    def test_catalogue_replay_rejected(self):
        after=copy.deepcopy(self.data);after['catalog_version']-=1
        with self.assertRaises(ValueError):assert_successor(self.crypto,self.data,after)
if __name__=='__main__':unittest.main()
