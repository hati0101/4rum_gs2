"""Build 196-9 only from the user's hash-verified 196-8; preserve every active MPQ file."""
from pathlib import Path
import sys,struct,json,hashlib,zlib,importlib.util,difflib
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path[:0]=[str(HERE),str(ROOT/'tools'),str(ROOT/'reviews/ver195-9')]
import w3x
from objdata import iter_mods,load_objects
from patch import patch,GLOBALS,fn
inventory_source=(ROOT/'reviews/ver195-9/build.py').read_text()
exec(inventory_source[inventory_source.index('def inventory('):inventory_source.index('def build(')])
EXPECTED='d7fd2492fa1115985b6ad2b2e876749d469037c17e5dba7d117c2ad60ed4e7a5'
def fields(name):
 if name.endswith('.w3a'):
  # Native chain damage is absent at ranks 5-8; rank 1-4 already explicitly zero.
  out={'A02R':{}}
  for lv in range(5,9):
   out['A02R'][('Ocl1',lv,1)]=(2,0.0)
   out['A02R'][('Ocl3',lv,3)]=(2,0.0)
  out['A13E']={('aran',lv,0):(2,99999.0) for lv in range(1,9)}
  return out
 return {'nE15':{('unam',0,0):(3,'특성')}}
def objects(raw,name):
 ver=struct.unpack_from('<I',raw)[0];tabs=[[],[]];edits=fields(name)
 for tab,base,new,si,flag,mods in iter_mods(raw,name.endswith('.w3a')):
  if si==0:tabs[tab].append([base,new,[]])
  oid=new if new!='\0'*4 else base
  changes=edits.get(oid,{}) if si==0 else {}
  chunks=[m['raw'] for m in mods if (m['id'],m['level'],m['data']) not in changes]
  for (fid,lv,ptr),(typ,value) in changes.items():
   r=fid.encode()+struct.pack('<I',typ)
   if name.endswith('.w3a'):r+=struct.pack('<II',lv,ptr)
   r+=struct.pack('<i',value) if typ==0 else struct.pack('<f',value) if typ==2 else value.encode()+b'\0'
   chunks.append(r+new.encode('latin1'))
  tabs[tab][-1][2].append((flag,chunks))
 out=bytearray(struct.pack('<I',ver))
 for rows in tabs:
  out+=struct.pack('<I',len(rows))
  for base,new,sets in rows:
   out+=base.encode('latin1')+new.encode('latin1')
   if ver>=3:out+=struct.pack('<I',len(sets))
   for flag,chunks in sets:
    if ver>=3:out+=struct.pack('<I',flag)
    out+=struct.pack('<I',len(chunks))+b''.join(chunks)
 return bytes(out)
def build():
 src=ROOT/'maps/reference/GS2vF_ver196-8.w3x';assert hashlib.sha256(src.read_bytes()).hexdigest()==EXPECTED
 a=w3x.Archive(str(src));before=inventory(a);assert a.base==0 and '(signature)' not in before
 j0=a.read('war3map.j').decode();assert 'GS1969_Init' not in j0
 helper=(HERE/'helpers.j').read_text()
 j=patch(j0).replace('endglobals',GLOBALS+'endglobals',1)
 # Helpers use only natives + existing globals; must precede their callers.
 p=j.index('\nfunction ');j=j[:p]+'\n'+helper+j[p:]
 changes={'war3map.j':j.encode()}
 for name in ['war3map.w3a','war3mapSkin.w3a','war3map.w3u','war3mapSkin.w3u']:
  changes[name]=objects(a.read(name),name)
  if changes[name]==a.read(name):del changes[name]
 d=a.read('war3map.w3i');e=d.index(b'\0',28);assert b'196-8' in d[28:e]
 changes['war3map.w3i']=d[:28]+d[28:e].replace(b'196-8',b'196-9')+d[e:]
 d=a.read('war3map.wct');p=d.index(b'\0',8)+1;out=bytearray(d[:p]);blocks=0;coverage={}
 while p<len(d):
  n=struct.unpack_from('<I',d,p)[0];p+=4;chunk=d[p:p+n];p+=n
  if n:
   text=chunk.rstrip(b'\0').decode().replace('\r\n','\n')
   text=patch(text)
   # Existing editor copies lagged behind runtime; retain runtime behavior on rebuild.
   for name in ['GSRI_Range','Trig_random_Actions']:
    old_fn=fn(text,name)
    if old_fn:text=text.replace(old_fn,fn(j,name),1)
   if blocks==0:text='globals\n'+GLOBALS+'endglobals\n'+helper+'\n'+text
   chunk=text.encode()+b'\0'
  out+=struct.pack('<I',len(chunk))+chunk;blocks+=1
 changes['war3map.wct']=bytes(out)
 work=Path('/workspace/fix1969');tmp=work/'uncompacted.w3x';a.save_with_replacements(str(tmp),changes)
 b=w3x.Archive(str(tmp));precompact=inventory(b);buf=bytearray(b.data[:32]);bt=[]
 for off,cs,fs,flags in b.block_table:
  assert not(flags&w3x.FLAG_ENCRYPTED and flags&w3x.FLAG_FIX_KEY)
  bt.append([len(buf),cs,fs,flags]);buf+=b.data[off:off+cs]
 hoff=len(buf);buf+=w3x.encrypt(b''.join(struct.pack('<IIHHI',*r) for r in b.hash_table),w3x.hash_string('(hash table)',3))
 boff=len(buf);buf+=w3x.encrypt(b''.join(struct.pack('<IIII',*r) for r in bt),w3x.hash_string('(block table)',3))
 struct.pack_into('<I',buf,8,len(buf));struct.pack_into('<II',buf,16,hoff,boff)
 dest=ROOT/'maps/release/GS2vF_ver196-9.w3x';dest.write_bytes(buf);c=w3x.Archive(str(dest));after=inventory(c)
 assert precompact==after and before.keys()==after.keys()
 changed=[before[k][0] for k in before if before[k][1]!=after[k][1]]
 assert set(changed)==set(changes)|{'(attributes)'}
 attrs=c.read('(attributes)')
 for n,data in changes.items():assert struct.unpack_from('<I',attrs,8+4*c.find(n))[0]==zlib.crc32(data)&0xffffffff
 # All unchanged object modifications must remain byte-for-byte equivalent.
 diff=[]
 for n in ['war3map.w3a','war3mapSkin.w3a','war3map.w3u','war3mapSkin.w3u']:
  d0=load_objects(a,n);d1=load_objects(c,n);assert d0.keys()==d1.keys()
  for oid in d0:
   allowed={fid+(str(lv) if lv else '') for fid,lv,ptr in fields(n).get(oid,{})}
   for k in d0[oid].keys()|d1[oid].keys():
    if d0[oid].get(k)!=d1[oid].get(k):
     assert k in allowed,(n,oid,k);diff.append([n,oid,k,d0[oid].get(k),d1[oid].get(k)])
 (HERE/'object-diff.json').write_text(json.dumps(diff,ensure_ascii=False,indent=2)+'\n')
 (work/'war3map.j').write_text(j)
 (HERE/'script.diff').write_text(''.join(difflib.unified_diff(j0.splitlines(True),j.splitlines(True),fromfile='196-8/war3map.j',tofile='196-9/war3map.j')))
 stats=dict(source_sha256=EXPECTED,result_sha256=hashlib.sha256(buf).hexdigest(),result_bytes=len(buf),active_files=len(after),unchanged_files=len(after)-len(changed),changed_files=changed,editor_blocks=blocks,compaction_bytes_saved=len(b.data)-len(buf),no_active_resource_deleted=True,branch='fix/196-9-handoff',published_to_main=False)
 (HERE/'verification.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2)+'\n');print(json.dumps(stats,ensure_ascii=False,indent=2))
if __name__=='__main__':build()
