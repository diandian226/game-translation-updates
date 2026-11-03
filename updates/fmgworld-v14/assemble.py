from pathlib import Path
import json,base64,hashlib,zipfile,io
parts=json.loads(Path('parts.json').read_text())
encoded=''.join(Path(n).read_text().strip() for n in parts)
with zipfile.ZipFile(io.BytesIO(base64.b64decode(encoded))) as transfer:
    recipes=json.loads(transfer.read('recipes.json'))
    assert len(recipes)==3
    for row in recipes:
        base=Path('bases',row['name'],row['base_asset']).read_bytes()
        assert hashlib.sha256(base).hexdigest()==row['base_sha256']
        with Path(row['asset']).open('wb') as f:
            for item in row['entries']:
                f.write(base64.b64decode(item['prefix']))
                data=base[item['base_offset']:item['base_offset']+item['length']] if 'base_offset' in item else transfer.read(item['delta'])
                assert len(data)==item['length'];f.write(data)
            f.write(transfer.read(row['tail']))
        blob=Path(row['asset']).read_bytes()
        assert hashlib.sha256(blob).hexdigest()==row['target_sha256']
        manifest='update.json' if row['name']=='new' else 'update-'+row['name']+'.json'
        data=json.loads(base64.b64decode(json.loads(Path(manifest).read_text())['signed_data']))
        assert data['version']==14 and data['game']=='fmgworld'
        assert data['patch_url'].endswith('/fmgworld-patch-v14/'+row['asset'])
        assert data['patch_size']==len(blob) and data['patch_sha256']==row['target_sha256']
        with zipfile.ZipFile(io.BytesIO(blob)) as z:
            assert z.testzip() is None
            names=z.namelist();assert len(names)==len(set(names))
            assert all(n.startswith('assets/x-game/') and '..' not in n.split('/') and '\\' not in n and not n.endswith('.apk') for n in names)
            assert 'assets/x-game/x-zzzzzzzz_fmg_inventory_fix.rpyc' in names
            assert 'assets/x-game/x-zzzzzzzzz_fmg_sprite_fix.rpyc' in names
catalog=json.loads(base64.b64decode(json.loads(Path('catalog.json').read_text())['signed_data']))
assert catalog['game']=='fmgworld' and catalog['catalog_version']==9
assert {v['version_code'] for v in catalog['versions']}=={1793047536,1793127647,1793478118}
for row in catalog['versions']:
    data=json.loads(base64.b64decode(row['release']['signed_data']))
    assert data['version']==14
    filename=data['patch_url'].rsplit('/',1)[1]
    assert hashlib.sha256(Path(filename).read_bytes()).hexdigest()==data['patch_sha256']
for name in ['update','update-old','update-middle','catalog']:
    envelope=json.loads(Path(name+'.json').read_text())
    Path(name+'.signed').write_bytes(base64.b64decode(envelope['signed_data']))
    Path(name+'.sig').write_bytes(base64.b64decode(envelope['signature']))
print('PASS: three exact payloads, signed manifest membership, safe ZIPs, CRC, original build coverage')
