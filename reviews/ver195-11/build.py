"""Conservative trait-helper cost pinning and a separate pre-195-9 comparison build."""
from pathlib import Path
import sys,struct,json,hashlib,zlib,re,importlib.util
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'reviews/ver195-9')]
import w3x
from objdata import iter_mods,load_objects
_spec=importlib.util.spec_from_file_location('previous_build',ROOT/'reviews/ver195-9/build.py');_previous=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(_previous)
inventory=_previous.inventory
HELPERS=['A0XP','A009','A01O','A00J','A0KS','A0DD','A0DF','A041','A0EQ','A0IM','A0XR','A08X','A011']
def patch_abilities(data):
 ver=struct.unpack_from('<I',data)[0];tables=[[],[]]
 for table,orig,new,si,flag,mods in iter_mods(data,True):
  if si==0:tables[table].append([orig,new,[]])
  oid=new if new!='\0'*4 else orig;fields=list(mods)
  if oid in HELPERS or oid=='A0CV':
   assert si==0
   lv=next((m['value'] for m in mods if m['id']=='alev'),None)
   # Skin does not normally carry level count; obtain the corresponding base definition.
   if lv is None:lv=LEVELS[oid]
   for m in mods:
    if m['id']=='amcs':assert m['value']==0,(oid,m)
   pinned=['amcs','aare'] if oid=='A0CV' else ['amcs']
   fields=[m for m in fields if m['id'] not in pinned]
   for level in range(1,lv+1):
    for fid in pinned:
     typ=0 if fid=='amcs' else 1;value=0 if typ==0 else 300.0
     raw=fid.encode()+struct.pack('<III',typ,level,0)+(struct.pack('<i',value) if typ==0 else struct.pack('<f',value))+oid.encode()
     fields.append(dict(raw=raw))
  tables[table][-1][2].append((flag,fields))
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
def build(source,destination,old_version,new_version):
 global LEVELS
 a=w3x.Archive(str(source));before=inventory(a);assert a.base==0 and '(signature)' not in before
 objs=load_objects(a,'war3map.w3a');LEVELS={id:objs[id]['alev'] for id in HELPERS+['A0CV']}
 for id in HELPERS:
  costs=[v for k,v in objs[id].items() if re.fullmatch(r'amcs\d+',k)];assert costs and all(v==0 for v in costs)
 replacement={n:patch_abilities(a.read(n)) for n in ['war3map.w3a','war3mapSkin.w3a']}
 replacement['war3map.j']=a.read('war3map.j').replace(old_version.encode(),new_version.encode())
 data=a.read('war3map.w3i');end=data.index(b'\0',28);replacement['war3map.w3i']=data[:28]+data[28:end].replace(old_version.encode(),new_version.encode())+data[end:]
 data=a.read('war3map.wct');p=data.index(b'\0',8)+1;out=bytearray(data[:p]);blocks=0
 while p<len(data):
  n=struct.unpack_from('<I',data,p)[0];p+=4;chunk=data[p:p+n];p+=n
  if n:chunk=chunk.replace(old_version.encode(),new_version.encode())
  out+=struct.pack('<I',len(chunk))+chunk;blocks+=1
 replacement['war3map.wct']=bytes(out)
 tmp=Path('/workspace/audit195/full/uncompacted.w3x');a.save_with_replacements(str(tmp),replacement);b=w3x.Archive(str(tmp));uncompacted=inventory(b)
 buf=bytearray(b.data[:32]);bt=[]
 for off,cs,fs,flags in b.block_table:
  assert not(flags&w3x.FLAG_ENCRYPTED and flags&w3x.FLAG_FIX_KEY)
  bt.append([len(buf),cs,fs,flags]);buf+=b.data[off:off+cs]
 hoff=len(buf);buf+=w3x.encrypt(b''.join(struct.pack('<IIHHI',*r) for r in b.hash_table),w3x.hash_string('(hash table)',3))
 boff=len(buf);buf+=w3x.encrypt(b''.join(struct.pack('<IIII',*r) for r in bt),w3x.hash_string('(block table)',3))
 struct.pack_into('<I',buf,8,len(buf));struct.pack_into('<II',buf,16,hoff,boff);destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(buf)
 c=w3x.Archive(str(destination));after=inventory(c);assert after==uncompacted and before.keys()==after.keys()
 changed=[before[k][0] for k in before if before[k][1]!=after[k][1]];assert set(changed)<=set(replacement)|{'(attributes)'}
 assert a.read('war3map.j').replace(old_version.encode(),new_version.encode())==c.read('war3map.j')
 ability_changes=[]
 for name in ['war3map.w3a','war3mapSkin.w3a']:
  x=load_objects(a,name);y=load_objects(c,name);assert x.keys()==y.keys()
  for id in x:
   if id not in HELPERS+['A0CV']:assert x[id]==y[id],(name,id)
   else:
    for k in set(x[id])|set(y[id]):
     if x[id].get(k)!=y[id].get(k):
      assert re.fullmatch(r'amcs\d+',k) or (id=='A0CV' and re.fullmatch(r'aare\d+',k)),(name,id,k)
      ability_changes.append(dict(file=name,id=id,field=k,old=x[id].get(k),new=y[id].get(k)))
 attr=c.read('(attributes)')
 for n,d in replacement.items():assert struct.unpack_from('<I',attr,8+4*c.find(n))[0]==zlib.crc32(d)&0xffffffff
 stats=dict(source=str(source.relative_to(ROOT)),output=str(destination.relative_to(ROOT)),source_sha256=hashlib.sha256(a.data).hexdigest(),result_sha256=hashlib.sha256(buf).hexdigest(),source_bytes=len(a.data),result_bytes=len(buf),active_files=len(after),changed_files=changed,runtime_only_version_labels_changed=True,helper_abilities=HELPERS,ability_field_changes=ability_changes,compaction_bytes_saved=len(b.data)-len(buf))
 Path('/workspace/audit195/full/'+new_version.split()[0]+'.j').write_bytes(c.read('war3map.j'))
 print(destination.name,len(buf),stats['result_sha256'])
 return stats
if __name__=='__main__':
 release=build(ROOT/'maps/release/GS2vF_ver195-10.w3x',ROOT/'maps/release/GS2vF_ver195-11.w3x','195-10','195-11')
 comparison=build(ROOT/'maps/reference/GS2vF_ver195-8.w3x',ROOT/'maps/diagnostics/GS2vF_ver195-12_compare1958.w3x','195-8','195-12 비교본')
 (HERE/'verification.json').write_text(json.dumps(dict(release=release,comparison=comparison),ensure_ascii=False,indent=2)+'\n')
