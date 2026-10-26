from pathlib import Path
import sys,re,struct,json,hashlib,zlib,importlib.util,difflib
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'reviews/ver195-9')]
import w3x
_spec=importlib.util.spec_from_file_location('previous_build',ROOT/'reviews/ver195-9/build.py');_previous=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(_previous)
inventory=_previous.inventory
GLOBALS='''    group GS19514_BurnSources = null
    group GS19514_BurnTargets = null
    timer GS19514_BurnClock = null
    boolean GS19514_BurnStarted = false
    integer GS19514_BurnPulses = 0
    string array GS19514_BurnStatus
'''
def fn(s,n):return re.search(r'^function '+n+r' takes .*?^endfunction',s,re.M|re.S).group()
OVERRIDES={
 'GS294_BurnTick':'    call GS19514_BurnTick()',
 'GS294_Init':'    call GS19514_BurnInit()',
 'Trig_FlB_Special_1_Actions':'    call GS19514_BurnResearch()',
}
def patch(s):
 for n,body in OVERRIDES.items():
  if 'function '+n+' takes ' in s:s=s.replace(fn(s,n),'function '+n+' takes nothing returns nothing\n'+body+'\nendfunction')
 return s.replace('195-13','195-14')
def build():
 a=w3x.Archive(str(ROOT/'maps/release/GS2vF_ver195-13.w3x'));old=inventory(a);runtime=(HERE/'runtime.j').read_text()
 j0=a.read('war3map.j').decode();j=patch(j0).replace('endglobals',GLOBALS+'endglobals',1);p=j.index('\nfunction ');j=j[:p]+'\n'+runtime+j[p:]
 replacement={'war3map.j':j.encode()};d=a.read('war3map.w3i');end=d.index(b'\0',28);replacement['war3map.w3i']=d[:28]+d[28:end].replace(b'195-13',b'195-14')+d[end:]
 d=a.read('war3map.wct');pos=d.index(b'\0',8)+1;out=bytearray(d[:pos]);blocks=0
 while pos<len(d):
  n=struct.unpack_from('<I',d,pos)[0];pos+=4;chunk=d[pos:pos+n];pos+=n
  if n:
   s=patch(chunk.rstrip(b'\0').decode().replace('\r\n','\n'))
   if blocks==0:s+='\nlibrary GS19514Burn initializer GS19514_BurnInit\nglobals\n'+GLOBALS+'endglobals\n'+runtime+'\nendlibrary\n'
   chunk=s.encode()+b'\0'
  out+=struct.pack('<I',len(chunk))+chunk;blocks+=1
 replacement['war3map.wct']=bytes(out)
 tmp=Path('/workspace/fix19514/uncompacted.w3x');tmp.parent.mkdir(parents=True,exist_ok=True);a.save_with_replacements(str(tmp),replacement)
 b=w3x.Archive(str(tmp));contents=inventory(b);assert b.base==0 and '(signature)' not in contents
 buf=bytearray(b.data[:32]);bt=[]
 for off,cs,fs,flags in b.block_table:
  assert not(flags&w3x.FLAG_ENCRYPTED and flags&w3x.FLAG_FIX_KEY)
  bt.append([len(buf),cs,fs,flags]);buf+=b.data[off:off+cs]
 hoff=len(buf);buf+=w3x.encrypt(b''.join(struct.pack('<IIHHI',*r) for r in b.hash_table),w3x.hash_string('(hash table)',3))
 boff=len(buf);buf+=w3x.encrypt(b''.join(struct.pack('<IIII',*r) for r in bt),w3x.hash_string('(block table)',3))
 struct.pack_into('<I',buf,8,len(buf));struct.pack_into('<II',buf,16,hoff,boff)
 dest=ROOT/'maps/release/GS2vF_ver195-14.w3x';dest.write_bytes(buf);c=w3x.Archive(str(dest));after=inventory(c);assert after==contents and after.keys()==old.keys()
 changed=[old[k][0] for k in old if old[k][1]!=after[k][1]];assert set(changed)<=set(replacement)|{'(attributes)'}
 for name in old:
  if old[name][0] not in replacement and name!='(attributes)':assert old[name][1]==after[name][1],name
 attr=c.read('(attributes)')
 for name,data in replacement.items():assert struct.unpack_from('<I',attr,8+4*c.find(name))[0]==zlib.crc32(data)&0xffffffff
 stats=dict(source_sha256=hashlib.sha256(a.data).hexdigest(),result_sha256=hashlib.sha256(buf).hexdigest(),result_bytes=len(buf),active_files=len(after),changed_files=changed,object_data_unchanged=True,period_seconds=1,radius=250,per_level_mana_burn=[4,6,8,10],magic_reduction_bonus_percentage_points=7,editor_blocks=blocks,compaction_bytes_saved=len(b.data)-len(buf))
 (HERE/'verification.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2)+'\n');(HERE/'script.diff').write_text(''.join(difflib.unified_diff(j0.splitlines(True),j.splitlines(True),fromfile='195-13/war3map.j',tofile='195-14/war3map.j')))
 Path('/workspace/fix19514/war3map.j').write_text(j);print(json.dumps(stats,ensure_ascii=False,indent=2))
if __name__=='__main__':build()
