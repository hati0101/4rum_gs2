"""Pin Flame Burst dummy costs/radius at every base/trait rank; no other gameplay changes."""
from pathlib import Path
import sys,struct,hashlib,json,zlib,re
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'reviews/ver195-9')]
from w3x import Archive
import w3x
from objdata import iter_mods,load_objects
import importlib.util
_spec=importlib.util.spec_from_file_location("performance1959_build",ROOT/"reviews/ver195-9/build.py")
_previous=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(_previous)
inventory=_previous.inventory
def ability_patch(data):
 ver=struct.unpack_from('<I',data)[0];tables=[[],[]]
 for table,orig,new,si,flag,mods in iter_mods(data,True):
  if si==0:tables[table].append([orig,new,[]])
  modified=list(mods)
  if (new if new!='\0'*4 else orig)=='A0CV':
   assert si==0
   modified=[m for m in modified if m['id'] not in ('amcs','aare')]
   for level in range(1,9):
    for fid,typ,val in [('amcs',0,0),('aare',1,300.0)]:
     raw=fid.encode()+struct.pack('<III',typ,level,0)+(struct.pack('<i',val) if typ==0 else struct.pack('<f',val))+b'A0CV'
     modified.append(dict(raw=raw))
  tables[table][-1][2].append((flag,modified))
 out=bytearray(struct.pack('<I',ver))
 for rows in tables:
  out+=struct.pack('<I',len(rows))
  for orig,new,sets in rows:
   out+=orig.encode('latin1')+new.encode('latin1')
   if ver>=3:out+=struct.pack('<I',len(sets))
   for flag,mods in sets:
    if ver>=3:out+=struct.pack('<I',flag)
    out+=struct.pack('<I',len(mods))+b''.join(m['raw'] for m in mods)
 return bytes(out)
def build():
 source=ROOT/'maps/release/GS2vF_ver195-9.w3x';dest=ROOT/'maps/release/GS2vF_ver195-10.w3x'
 a=Archive(str(source));before=inventory(a);replacement={}
 for name in ['war3map.w3a','war3mapSkin.w3a']:replacement[name]=ability_patch(a.read(name))
 replacement['war3map.j']=a.read('war3map.j').decode().replace('195-9','195-10').encode()
 data=a.read('war3map.w3i');end=data.index(b'\0',28);replacement['war3map.w3i']=data[:28]+data[28:end].replace(b'195-9',b'195-10')+data[end:]
 data=a.read('war3map.wct');pos=data.index(b'\0',8)+1;out=bytearray(data[:pos]);blocks=0
 while pos<len(data):
  n=struct.unpack_from('<I',data,pos)[0];pos+=4;chunk=data[pos:pos+n];pos+=n
  if n:chunk=chunk.replace(b'195-9',b'195-10')
  out+=struct.pack('<I',len(chunk))+chunk;blocks+=1
 replacement['war3map.wct']=bytes(out)
 tmp=Path('/workspace/audit195/195-10-uncompacted.w3x');a.save_with_replacements(str(tmp),replacement)
 b=Archive(str(tmp));uncompacted=inventory(b);assert b.base==0 and '(signature)' not in uncompacted
 buf=bytearray(b.data[:32]);bt=[]
 for off,cs,fs,flags in b.block_table:
  assert not(flags&w3x.FLAG_ENCRYPTED and flags&w3x.FLAG_FIX_KEY)
  bt.append([len(buf),cs,fs,flags]);buf+=b.data[off:off+cs]
 hoff=len(buf);buf+=w3x.encrypt(b''.join(struct.pack('<IIHHI',*r) for r in b.hash_table),w3x.hash_string('(hash table)',3))
 boff=len(buf);buf+=w3x.encrypt(b''.join(struct.pack('<IIII',*r) for r in bt),w3x.hash_string('(block table)',3))
 struct.pack_into('<I',buf,8,len(buf));struct.pack_into('<II',buf,16,hoff,boff);dest.write_bytes(buf)
 c=Archive(str(dest));after=inventory(c);assert after==uncompacted and before.keys()==after.keys()
 changed=[before[k][0] for k in before if before[k][1]!=after[k][1]]
 assert set(changed)<=set(replacement)|{'(attributes)'}
 for name in ['war3map.w3a','war3mapSkin.w3a']:
  old=load_objects(a,name);new=load_objects(c,name);assert old.keys()==new.keys()
  for id in old:
   if id!='A0CV':assert old[id]==new[id],id
  for lv in range(1,9):assert new['A0CV']['amcs'+str(lv)]==0 and new['A0CV']['aare'+str(lv)]==300.0
  for k in set(old['A0CV'])|set(new['A0CV']):
   if not re.fullmatch(r'(amcs|aare)[1-8]',k):assert old['A0CV'].get(k)==new['A0CV'].get(k),k
 assert a.read('war3map.j').replace(b'195-9',b'195-10')==c.read('war3map.j')
 attr=c.read('(attributes)')
 for n,d in replacement.items():assert struct.unpack_from('<I',attr,8+4*c.find(n))[0]==zlib.crc32(d)&0xffffffff
 stats=dict(source_sha256=hashlib.sha256(a.data).hexdigest(),result_sha256=hashlib.sha256(buf).hexdigest(),source_bytes=len(a.data),result_bytes=len(buf),active_files=len(after),changed_files=changed,ability_changed='A0CV',levels=list(range(1,9)),explicit_mana_cost=0,explicit_radius=300,other_ability_objects_unchanged=True,runtime_only_version_labels_changed=True,wct_blocks=blocks,compaction_bytes_saved=len(b.data)-len(buf))
 (HERE/'verification.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2)+'\n')
 Path('/workspace/audit195/10-war3map.j').write_bytes(c.read('war3map.j'))
 print(json.dumps(stats,ensure_ascii=False,indent=2))
if __name__=='__main__':build()
