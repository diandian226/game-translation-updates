from pathlib import Path
import base64,hashlib,json,zipfile,io
encoded=''.join(Path(f'transfer.part{i}.b64').read_text().strip() for i in range(1))
transfer=zipfile.ZipFile(io.BytesIO(base64.b64decode(encoded)))
recipe=json.loads(transfer.read('recipe.json'))
base=Path('base/payload.zip').read_bytes()
assert hashlib.sha256(base).hexdigest()==recipe['base_sha256']
with Path('payload.zip').open('wb') as f:
    for item in recipe['entries']:
        f.write(base64.b64decode(item['prefix']))
        data=base[item['base_offset']:item['base_offset']+item['length']] if 'base_offset' in item else transfer.read(item['delta'])
        assert len(data)==item['length']
        f.write(data)
    f.write(transfer.read('tail.bin'))
blob=Path('payload.zip').read_bytes()
assert hashlib.sha256(blob).hexdigest()==recipe['target_sha256']
meta=json.loads(base64.b64decode(json.loads(Path('update.json').read_text())['signed_data']))
assert meta['version']==3 and meta['game']=='realmofevergrow'
assert meta['patch_url'].endswith('/realmofevergrow-patch-v3/payload.zip')
assert len(blob)==meta['patch_size'] and hashlib.sha256(blob).hexdigest()==meta['patch_sha256']
with zipfile.ZipFile(io.BytesIO(blob)) as z:
    assert z.testzip() is None
    assert len(z.infolist())==220
    assert all(n.startswith('assets/x-game/') and n.endswith(('.rpyc','.ttc','.ttf','.otf')) and '..' not in n for n in z.namelist())
catalog=json.loads(base64.b64decode(json.loads(Path('catalog.json').read_text())['signed_data']))
assert catalog['catalog_version']==3 and len(catalog['versions'])==1
assert any(r['version_code']==1 and json.loads(base64.b64decode(r['release']['signed_data']))==meta for r in catalog['versions'])
for name in ['update','catalog']:
    envelope=json.loads(Path(name+'.json').read_text())
    Path(name+'.signed').write_bytes(base64.b64decode(envelope['signed_data']))
    Path(name+'.sig').write_bytes(base64.b64decode(envelope['signature']))
print('Verified exact payload bytes, CRC, all 220 paths and the matching game catalogue')
