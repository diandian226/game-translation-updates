"""Reconstruct the locally signed APK byte-for-byte; no signing key is needed in CI."""
import hashlib,json,sys,zipfile
from pathlib import Path

def assemble(base,delta,output):
    source=Path(base).read_bytes()
    with zipfile.ZipFile(delta) as z:
        assert set(z.namelist())=={'recipe.json','literal.bin'} and z.testzip() is None
        recipe=json.loads(z.read('recipe.json'))
        literal=z.read('literal.bin')
    assert hashlib.sha256(source).hexdigest()==recipe['base_sha256']
    assert 0<recipe['target_size']<=150*1024*1024
    total=0
    with Path(output).open('wb') as out:
        for segment in recipe['segments']:
            length=segment['length']
            data=source if 'base' in segment else literal
            offset=segment.get('base',segment.get('literal'))
            assert isinstance(offset,int) and isinstance(length,int) and 0<=offset<=offset+length<=len(data)
            total+=length
            assert total<=recipe['target_size']
            out.write(data[offset:offset+length])
    assert total==recipe['target_size']
    assert hashlib.sha256(Path(output).read_bytes()).hexdigest()==recipe['target_sha256']
    with zipfile.ZipFile(output) as z:
        assert z.testzip() is None
        assert all('\\' not in i.orig_filename for i in z.infolist())
        for game in ['fmgworld','outgrow']:
            assert z.read('assets/catalog-'+game+'.json')==z.read('assets/catalogs/'+game+'.json')
    print('SIGNED_APK_RECONSTRUCTED_EXACTLY',recipe['target_sha256'])

if __name__=='__main__':
    assemble(*sys.argv[1:4])
