from pathlib import Path
import json,base64,hashlib,zipfile,io
parts=json.loads(Path('parts.json').read_text())
encoded=''.join(Path(n).read_text().strip() for n in parts)
with zipfile.ZipFile(io.BytesIO(base64.b64decode(encoded))) as transfer:
    r=json.loads(transfer.read('recipe.json'))
    base=Path('base/payload.zip').read_bytes()
    assert hashlib.sha256(base).hexdigest()==r['base_sha256']
    with Path('payload.zip').open('wb') as out:
        for e in r['entries']:
            out.write(base64.b64decode(e['prefix']))
            b=base[e['base_offset']:e['base_offset']+e['length']] if 'base_offset' in e else transfer.read(e['delta'])
            assert len(b)==e['length'];out.write(b)
        out.write(transfer.read('tail.bin'))
blob=Path('payload.zip').read_bytes();assert hashlib.sha256(blob).hexdigest()==r['target_sha256']
meta=json.loads(base64.b64decode(json.loads(Path('update.json').read_text())['signed_data']))
assert meta['version']==16 and meta['game']=='fmgworld'
assert meta['source_sha256']=='c286e9f1579bc26e2843d405239d25b3a28c188f6fd121c08617e8213289a6a6'
assert meta['patch_url'].endswith('/fmgworld-patch-v16/payload.zip')
assert len(blob)==meta['patch_size'] and r['target_sha256']==meta['patch_sha256']
with zipfile.ZipFile(io.BytesIO(blob)) as z:
    assert z.testzip() is None
    names=z.namelist();assert len(names)==233 and len(names)==len(set(names))
    assert all(n.startswith('assets/x-game/') and '..' not in n.split('/') and '\\' not in n and not n.endswith(('.apk','.rpy','.bak')) and 'qa_' not in n and 'fontcheck_only' not in n for n in names)
    for n in ['zzzzzzzz_fmg_inventory_fix','zzzzzzzzz_fmg_sprite_fix','zzzzzzzzzz_fmg_build1793629832_zh','zzzzzzzzzzz_fmg_confirm_zh']:
        assert 'assets/x-game/x-'+n+'.rpyc' in names
catalog=json.loads(base64.b64decode(json.loads(Path('catalog.json').read_text())['signed_data']))
assert catalog['game']=='fmgworld' and catalog['catalog_version']==11
assert {v['version_code'] for v in catalog['versions']}=={1793047536,1793127647,1793478118,1793629832}
for row in catalog['versions']:
    release=json.loads(base64.b64decode(row['release']['signed_data']))
    if row['version_code']==1793629832:assert release==meta
    else:assert release['version']==14
for name in ['update','catalog']:
    envelope=json.loads(Path(name+'.json').read_text())
    Path(name+'.signed').write_bytes(base64.b64decode(envelope['signed_data']))
    Path(name+'.sig').write_bytes(base64.b64decode(envelope['signature']))
print('PASS exact patch bytes, CRC, 232 safe paths, new source hash and four-build catalogue')
