from pathlib import Path
import base64,hashlib,json,zipfile,io
parts=sorted(Path('.').glob('payload.part*.b64'),key=lambda p:p.name)
blob=base64.b64decode(''.join(p.read_text().strip() for p in parts))
meta_env=json.loads(Path('update.json').read_text())
meta=json.loads(base64.b64decode(meta_env['signed_data']))
assert meta['version']==11 and meta['game']=='fmgworld'
assert meta['source_sha256']=='c0855194f299367aac51512f70499eca2c8658a715dcf4d231def099cea49e34'
assert meta['patch_url'].endswith('/fmgworld-patch-v11/payload.zip')
assert len(blob)==meta['patch_size'] and hashlib.sha256(blob).hexdigest()==meta['patch_sha256']
with zipfile.ZipFile(io.BytesIO(blob)) as z:
    assert z.testzip() is None
    assert len(z.infolist())==229
    assert all(n.startswith('assets/x-game/') and n.endswith(('.rpyc','.ttc','.ttf','.otf')) and '..' not in n and '\\' not in n for n in z.namelist())
Path('payload.zip').write_bytes(blob)
Path('update.signed').write_bytes(base64.b64decode(meta_env['signed_data']))
Path('update.sig').write_bytes(base64.b64decode(meta_env['signature']))
cat_env=json.loads(Path('catalog.json').read_text())
cat=json.loads(base64.b64decode(cat_env['signed_data']))
assert cat['game']=='fmgworld' and cat['catalog_version']==8 and len(cat['versions'])==3
row=[r for r in cat['versions'] if r['version_code']==1793478118][0]
assert row['release']==meta_env
Path('catalog.signed').write_bytes(base64.b64decode(cat_env['signed_data']))
Path('catalog.sig').write_bytes(base64.b64decode(cat_env['signature']))
print('assembled payload',len(blob))
