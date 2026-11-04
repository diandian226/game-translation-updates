"""Signed patch-history protocol v1. Python stdlib + JDK; no private key in repository."""
from pathlib import Path
import argparse,base64,copy,hashlib,json,os,re,shutil,subprocess,tempfile
from urllib.parse import urlparse

LIMIT=512*1024
REPO='diandian226/game-translation-updates'
def read(path):
    data=Path(path).read_bytes()
    if len(data)>LIMIT:raise ValueError('File exceeds catalogue envelope limit')
    return json.loads(data.decode('utf-8-sig'))
def save(path,data):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    encoded=json.dumps(data,ensure_ascii=False,separators=(',',':')).encode('utf-8')
    if len(encoded)>LIMIT:raise ValueError('Catalogue exceeds old-tool 512 KiB limit')
    temporary=path.with_name(path.name+'.next');temporary.write_bytes(encoded);temporary.replace(path)
def encoded(data):return json.dumps(data,ensure_ascii=False,separators=(',',':')).encode('utf-8')
class Crypto:
    def __init__(self,cert=None):
        self.cert=Path(cert or Path(__file__).with_name('update-cert.pem')).resolve()
        self.temp=tempfile.TemporaryDirectory(prefix='patch-catalog-');self.work=Path(self.temp.name);self.cache={}
        home=os.environ.get('JAVA_HOME')
        self.java=str(Path(home)/'bin/java') if home else 'java'
        javac=str(Path(home)/'bin/javac') if home else 'javac'
        subprocess.run([javac,'-encoding','UTF-8','-d',str(self.work),str(Path(__file__).with_name('CatalogCrypto.java'))],check=True,capture_output=True)
    def _call(self,mode,raw,last):
        path=self.work/'payload.json';path.write_bytes(raw)
        return subprocess.run([self.java,'-cp',str(self.work),'CatalogCrypto',mode,str(self.cert),str(path),str(last)],check=True,capture_output=True,text=True,encoding='utf-8').stdout.strip()
    def verify(self,envelope):
        if set(envelope)!={'signed_data','signature'}:raise ValueError('Unexpected envelope fields')
        raw=base64.b64decode(envelope['signed_data'],validate=True);sig=base64.b64decode(envelope['signature'],validate=True)
        if not raw or len(raw)>LIMIT or len(sig)>4096:raise ValueError('Invalid signed payload size')
        digest=hashlib.sha256(raw+sig).hexdigest()
        if digest not in self.cache:
            p=self.work/'signature.bin';p.write_bytes(sig);self._call('verify',raw,p);self.cache[digest]=json.loads(raw)
        return copy.deepcopy(self.cache[digest])
    def sign(self,data,key):
        raw=encoded(data);signature=self._call('sign',raw,Path(key).resolve())
        envelope={'signed_data':base64.b64encode(raw).decode(),'signature':signature}
        assert self.verify(envelope)==data
        if len(encoded(envelope))>LIMIT:raise ValueError('Encoded catalogue too large for old tools')
        return envelope

def release(crypto,envelope,game,source=None):
    d=crypto.verify(envelope)
    if d.get('schema')!=1 or d.get('game')!=game:raise ValueError('Wrong release game/schema')
    if not isinstance(d.get('version'),int) or d['version']<1:raise ValueError('Invalid patch revision')
    if not isinstance(d.get('min_tool'),int) or d['min_tool']<1:raise ValueError('Invalid min_tool')
    for name in ['source_sha256','patch_sha256']:
        if not re.fullmatch('[0-9a-f]{64}',d.get(name,'')):raise ValueError('Invalid SHA256')
    if source and d['source_sha256']!=source:raise ValueError('History patch belongs to different original APK')
    if not isinstance(d.get('patch_size'),int) or d['patch_size']<1:raise ValueError('Invalid patch size')
    u=urlparse(d.get('patch_url',''))
    if u.scheme!='https' or u.hostname!='github.com' or not u.path.startswith('/'+REPO+'/releases/download/') or u.query or u.fragment or u.username:raise ValueError('Untrusted patch asset URL')
    if not isinstance(d.get('label'),str) or not d['label'].strip():raise ValueError('Missing patch label')
    return d

def catalog(crypto,envelope,game=None):
    d=crypto.verify(envelope);game=game or d.get('game')
    if d.get('schema')!=1 or d.get('kind')!='game-version-catalog' or d.get('game')!=game:raise ValueError('Wrong catalogue identity')
    if not isinstance(d.get('catalog_version'),int) or d['catalog_version']<1:raise ValueError('Invalid catalogue revision')
    if not isinstance(d.get('min_tool'),int) or d['min_tool']<1:raise ValueError('Invalid catalogue min_tool')
    if 'patch_history_schema' in d and d['patch_history_schema']!=1:raise ValueError('Unsupported patch history schema')
    if any('patch_history' in e for e in d.get('versions',[])) and d.get('patch_history_schema')!=1:raise ValueError('History schema is required')
    if not 1<=len(d.get('versions',[]))<=64:raise ValueError('Invalid original count')
    hashes=set()
    for e in d['versions']:
        latest=release(crypto,e['release'],game);sha=latest['source_sha256']
        if sha in hashes:raise ValueError('Duplicate original APK')
        hashes.add(sha)
        if not isinstance(e.get('version_code'),int) or e['version_code']<1 or not e.get('version_name') or len(e['version_name'])>80 or not e.get('label') or len(e['label'])>160:raise ValueError('Invalid original version metadata')
        seen=set();history=e.get('patch_history',[])
        if len(history)>64:raise ValueError('Too many historical revisions')
        for item in history:
            old=release(crypto,item['release'],game,sha);number=old['version']
            if number>=latest['version'] or number in seen or item.get('revision')!=number:raise ValueError('Invalid or repeated history revision')
            if item.get('label')!=old['label'] or not isinstance(item.get('stable'),bool):raise ValueError('Invalid history display metadata')
            seen.add(number)
    return d

def history_item(d,envelope,notes='历史修订，未重新进行完整真机验证；建议优先使用最新补丁。',stable=False):
    return {'revision':d['version'],'label':d['label'],'stable':stable,'notes':notes,'release':envelope}

def add_history(crypto,data,envelopes):
    d=copy.deepcopy(data);game=d['game']
    d['patch_history_schema']=1
    for e in d['versions']:e.setdefault('patch_history',[])
    for candidate in envelopes:
        old=release(crypto,candidate,game)
        matches=[e for e in d['versions'] if release(crypto,e['release'],game)['source_sha256']==old['source_sha256']]
        if len(matches)!=1:raise ValueError('No unique matching original APK for approved history')
        e=matches[0];latest=release(crypto,e['release'],game)
        if old['version']>=latest['version']:raise ValueError('History must be older than latest')
        existing={item['revision']:item for item in e['patch_history']}
        if old['version'] in existing:
            previous=release(crypto,existing[old['version']]['release'],game)
            if previous!=old:raise ValueError('Conflicting content for same patch revision')
        else:e['patch_history'].append(history_item(old,candidate))
        e['patch_history'].sort(key=lambda x:x['revision'],reverse=True)
    return d

def advance(crypto,baseline,manifest,version_name,version_code,label):
    d=add_history(crypto,baseline,[]);game=d['game'];new=release(crypto,manifest,game)
    found=None
    for e in d['versions']:
        current=release(crypto,e['release'],game)
        if current['source_sha256']!=new['source_sha256']:continue
        found=e
        if e['version_name']!=version_name or e['version_code']!=version_code:raise ValueError('Exact original SHA has inconsistent version metadata')
        if new['version']<current['version']:raise ValueError('Cannot publish lower latest patch revision')
        if new['version']==current['version'] and new!=current:raise ValueError('Same revision has different signed content')
        if new['version']>current['version']:e['patch_history'].insert(0,history_item(current,e['release']))
        e.update(label=label,release=manifest)
    if found is None:d['versions'].append({'version_name':version_name,'version_code':version_code,'label':label,'release':manifest,'patch_history':[]})
    d['catalog_version']+=1
    return d

def assert_successor(crypto,previous,current):
    if current['game']!=previous['game'] or current['catalog_version']<previous['catalog_version']:raise ValueError('Catalogue rollback')
    if current!=previous and current['catalog_version']==previous['catalog_version']:raise ValueError('Catalogue content changed without revision bump')
    for old in previous['versions']:
        r=release(crypto,old['release'],previous['game'])
        new=next((e for e in current['versions'] if release(crypto,e['release'],current['game'])['source_sha256']==r['source_sha256']),None)
        if new is None:raise ValueError('Existing original APK mapping removed')
        latest=release(crypto,new['release'],current['game'])
        if latest['version']<r['version']:raise ValueError('Latest patch downgraded')
        approved=[new['release']]+[i['release'] for i in new.get('patch_history',[])]
        expected=[old['release']]+[i['release'] for i in old.get('patch_history',[])]
        for envelope in expected:
            if crypto.verify(envelope) not in [crypto.verify(x) for x in approved]:raise ValueError('Previously approved revision disappeared or changed')

def main():
    p=argparse.ArgumentParser();p.add_argument('--cert');subs=p.add_subparsers(dest='command',required=True)
    v=subs.add_parser('verify');v.add_argument('files',nargs='+');v.add_argument('--previous-directory')
    h=subs.add_parser('history');h.add_argument('--baseline',required=True);h.add_argument('--history',nargs='*',default=[]);h.add_argument('--key',required=True);h.add_argument('--output',required=True)
    u=subs.add_parser('advance');u.add_argument('--baseline',required=True);u.add_argument('--manifest',required=True);u.add_argument('--version-name',required=True);u.add_argument('--version-code',required=True,type=int);u.add_argument('--label',required=True);u.add_argument('--key',required=True);u.add_argument('--output',required=True)
    a=p.parse_args();crypto=Crypto(a.cert)
    if a.command=='verify':
        for name in a.files:
            d=catalog(crypto,read(name))
            if a.previous_directory:
                old=Path(a.previous_directory)/Path(name).name
                if old.exists():assert_successor(crypto,catalog(crypto,read(old)),d)
            print(json.dumps({'file':name,'game':d['game'],'catalog_version':d['catalog_version'],'originals':len(d['versions']),'history_revisions':sum(len(e.get('patch_history',[])) for e in d['versions'])},ensure_ascii=False))
    else:
        before=catalog(crypto,read(a.baseline))
        if a.command=='history':d=add_history(crypto,before,[read(x) for x in a.history]);d['catalog_version']+=1
        else:d=advance(crypto,before,read(a.manifest),a.version_name,a.version_code,a.label)
        envelope=crypto.sign(d,a.key);catalog(crypto,envelope);assert_successor(crypto,before,d);save(a.output,envelope)
        print(json.dumps({'game':d['game'],'catalog_version':d['catalog_version'],'history_revisions':sum(len(e.get('patch_history',[])) for e in d['versions']),'output':a.output},ensure_ascii=False))

if __name__=='__main__':main()
