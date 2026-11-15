"""Repair Flame Burst's real caster path using old-map evidence; preserve current balance."""
from pathlib import Path
import sys,struct,json,hashlib,zlib,re,importlib.util,difflib
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'reviews/ver195-9')]
import w3x
from objdata import iter_mods,load_objects
_spec=importlib.util.spec_from_file_location('prior_build',ROOT/'reviews/ver195-9/build.py');prior=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(prior)
inventory=prior.inventory
FIELDS={('alev',0,0):(0,8),('aher',0,0):(0,0)}
for level in range(1,9):
 base=(level-1)%4+1;trait=level>4
 for field,typ,ptr,val in [('amcs',0,0,0),('aare',2,0,300.0),('adur',2,0,1.5),('ahdu',2,0,1.5),('acdn',2,0,0.0),('acas',2,0,0.0),('atar',3,0,'organic,enemies,ground'),('Htc1',2,1,40.0*base+(100.0 if trait else 0.0)),('Htc3',2,3,.10+.05*base+(.50 if trait else 0.0)),('Htc4',2,4,0.0),('Htc5',2,5,0.0)]:FIELDS[(field,level,ptr)]=(typ,val)
def objects(data):
 ver=struct.unpack_from('<I',data)[0];tables=[[],[]]
 for table,base,new,si,flag,mods in iter_mods(data,True):
  if si==0:tables[table].append([base,new,[]])
  raws=[m['raw'] for m in mods]
  if new=='A0CV':
   assert si==0
   ids={key[0] for key in FIELDS};raws=[m['raw'] for m in mods if m['id'] not in ids]
   for (fid,level,ptr),(typ,val) in FIELDS.items():
    raw=fid.encode()+struct.pack('<III',typ,level,ptr)
    if typ==0:raw+=struct.pack('<i',val)
    elif typ==2:raw+=struct.pack('<f',val)
    else:raw+=val.encode()+b'\0'
    raws.append(raw+b'A0CV')
  tables[table][-1][2].append((flag,raws))
 out=bytearray(struct.pack('<I',ver))
 for rows in tables:
  out+=struct.pack('<I',len(rows))
  for base,new,sets in rows:
   out+=base.encode('latin1')+new.encode('latin1')
   if ver>=3:out+=struct.pack('<I',len(sets))
   for flag,raws in sets:
    if ver>=3:out+=struct.pack('<I',flag)
    out+=struct.pack('<I',len(raws))+b''.join(raws)
 return bytes(out)
def fn(s,name):return re.search(r'^function '+name+r' takes .*?^endfunction',s,re.M|re.S).group()
def build():
 a=w3x.Archive(str(ROOT/'maps/release/GS2vF_ver195-11.w3x'));old=inventory(a);runtime=(HERE/'runtime.j').read_text();replacement={}
 j0=a.read('war3map.j').decode();j=j0.replace(fn(j0,'Trig_Flame_Burst_Actions'),runtime.rstrip())
 j=j.replace('endglobals','    string array GS19513_FlameBurstStatus\n    boolean GS19513_FlameBurstStarted = false\n    boolean GS19513_FlameBurstInstalled = false\nendglobals',1)
 j=j.replace('    call InitTrig_Flame_Burst(  )','    call GS19513_FlameBurstInit()\n    call InitTrig_Flame_Burst(  )',1).replace('195-11','195-13')
 replacement['war3map.j']=j.encode()
 for name in ['war3map.w3a','war3mapSkin.w3a']:replacement[name]=objects(a.read(name))
 d=a.read('war3map.w3i');end=d.index(b'\0',28);replacement['war3map.w3i']=d[:28]+d[28:end].replace(b'195-11',b'195-13')+d[end:]
 d=a.read('war3map.wct');pos=d.index(b'\0',8)+1;out=bytearray(d[:pos]);block=0;has_action=False
 while pos<len(d):
  n=struct.unpack_from('<I',d,pos)[0];pos+=4;raw=d[pos:pos+n];pos+=n
  if n:
   s=raw.rstrip(b'\0').decode().replace('\r\n','\n').replace('195-11','195-13')
   if 'function Trig_Flame_Burst_Actions takes ' in s:
    s=s.replace(fn(s,'Trig_Flame_Burst_Actions'),fn(runtime,'Trig_Flame_Burst_Actions'));has_action=True
   if block==0:
    head=runtime[:runtime.index('function Trig_Flame_Burst_Actions takes ')]
    s+='\nlibrary GS19513FlameBurst initializer GS19513_FlameBurstInit\nglobals\n    string array GS19513_FlameBurstStatus\n    boolean GS19513_FlameBurstStarted = false\n    boolean GS19513_FlameBurstInstalled = false\nendglobals\n'+head+'\nendlibrary\n'
   raw=s.encode()+b'\0'
  out+=struct.pack('<I',len(raw))+raw;block+=1
 # GUI version of the action is replaced after initialization by the WCT library.
 replacement['war3map.wct']=bytes(out)
 tmp=Path('/workspace/fix19513/uncompacted.w3x');a.save_with_replacements(str(tmp),replacement);b=w3x.Archive(str(tmp));contents=inventory(b);assert b.base==0 and '(signature)' not in contents
 buf=bytearray(b.data[:32]);bt=[]
 for off,cs,fs,flags in b.block_table:
  assert not(flags&w3x.FLAG_ENCRYPTED and flags&w3x.FLAG_FIX_KEY)
  bt.append([len(buf),cs,fs,flags]);buf+=b.data[off:off+cs]
 hoff=len(buf);buf+=w3x.encrypt(b''.join(struct.pack('<IIHHI',*r) for r in b.hash_table),w3x.hash_string('(hash table)',3))
 boff=len(buf);buf+=w3x.encrypt(b''.join(struct.pack('<IIII',*r) for r in bt),w3x.hash_string('(block table)',3))
 struct.pack_into('<I',buf,8,len(buf));struct.pack_into('<II',buf,16,hoff,boff)
 dest=ROOT/'maps/release/GS2vF_ver195-13.w3x';dest.write_bytes(buf);c=w3x.Archive(str(dest));after=inventory(c);assert after==contents and after.keys()==old.keys()
 changed=[old[k][0] for k in old if old[k][1]!=after[k][1]];assert set(changed)<=set(replacement)|{'(attributes)'}
 for file in ['war3map.w3a','war3mapSkin.w3a']:
  x=load_objects(a,file);y=load_objects(c,file);assert x.keys()==y.keys()
  for id in x:
   if id!='A0CV':assert x[id]==y[id],(file,id)
 attr=c.read('(attributes)')
 for name,data in replacement.items():assert struct.unpack_from('<I',attr,8+4*c.find(name))[0]==zlib.crc32(data)&0xffffffff
 stats=dict(source_sha256=hashlib.sha256(a.data).hexdigest(),result_sha256=hashlib.sha256(buf).hexdigest(),result_bytes=len(buf),active_files=len(after),changed_files=changed,ability_changed='A0CV',caster_unit='ewsp',visual_unit='h00W',numeric_order=852096,editor_gui_action_replaced_directly=has_action,editor_install_hook_included=True,editor_blocks=block,compaction_bytes_saved=len(b.data)-len(buf))
 (HERE/'verification.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2)+'\n')
 (HERE/'script.diff').write_text(''.join(difflib.unified_diff(j0.splitlines(True),j.splitlines(True),fromfile='195-11/war3map.j',tofile='195-13/war3map.j')))
 Path('/workspace/fix19513/war3map.j').write_text(j);print(json.dumps(stats,ensure_ascii=False,indent=2))
if __name__=='__main__':build()
