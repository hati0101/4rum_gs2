"""Build 195-9 from the uploaded 195-8; verify all live MPQ entries."""
from pathlib import Path
import sys,struct,hashlib,json,difflib,zlib
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import w3x
from patch import patch,functions,GLOBALS,HELPERS

def inventory(a):
 names=a.read('(listfile)').decode('utf-8-sig').splitlines()+['(listfile)','(attributes)','(signature)']
 # Imported names are retained even if an old listfile omits one.
 imp=a.read('war3map.imp')
 if imp:
  p=8
  for _ in range(struct.unpack_from('<I',imp,4)[0]):
   flag=imp[p];p+=1;e=imp.index(b'\0',p);n=imp[p:e].decode();p=e+1
   names.append(n if flag in (10,13) else 'war3mapImported\\'+n)
 result={}
 for n in names:
  if a.find(n) is not None:result[n.lower().replace('/','\\')]=(n,a.read(n))
 active={x[4] for x in a.hash_table if x[4]<len(a.block_table)}
 mapped={a.find(n) for n,_ in result.values()}
 assert active==mapped,('unmapped entries',active-mapped)
 return result

def build(source,destination):
 a=w3x.Archive(str(source));before=inventory(a)
 assert a.base==0 and '(signature)' not in before
 j0=a.read('war3map.j').decode();j,hits=patch(j0)
 assert 'GS1959_' not in j0
 j=j.replace('endglobals',GLOBALS+'endglobals',1)
 first=j.index('\nfunction ');j=j[:first]+'\n'+HELPERS+j[first:]
 replacement={'war3map.j':j.encode()}
 d=a.read('war3map.w3i');end=d.index(b'\0',28);title=d[28:end].decode();assert '195-8' in title
 replacement['war3map.w3i']=d[:28]+title.replace('195-8','195-9').encode()+d[end:]
 # WCT v4 header: format/game version + comment + independently sized code blocks.
 d=a.read('war3map.wct');p=d.index(b'\0',8)+1;out=bytearray(d[:p]);i=0
 while p<len(d):
  n=struct.unpack_from('<I',d,p)[0];p+=4;chunk=d[p:p+n];p+=n
  if chunk:
   text,_=patch(chunk.rstrip(b'\0').decode())
   if i==0:text='globals\n'+GLOBALS+'endglobals\n'+HELPERS+'\n'+text
   chunk=text.encode()+b'\0'
  out+=struct.pack('<I',len(chunk))+chunk;i+=1
 replacement['war3map.wct']=bytes(out)
 # Do not touch ability/unit/item/upgrade/skin/placement/WTS/gameplay tables.
 temp=destination.with_suffix('.tmp.w3x');a.save_with_replacements(str(temp),replacement)
 b=w3x.Archive(str(temp));uncompacted=inventory(b);buf=bytearray(b.data[:32]);bt=[]
 for off,csize,fsize,flags in b.block_table:
  assert not(flags&w3x.FLAG_ENCRYPTED and flags&w3x.FLAG_FIX_KEY),'offset-dependent encryption'
  blob=b.data[off:off+csize];bt.append([len(buf),csize,fsize,flags]);buf+=blob
 hoff=len(buf);buf+=w3x.encrypt(b''.join(struct.pack('<IIHHI',*x) for x in b.hash_table),w3x.hash_string('(hash table)',3))
 boff=len(buf);buf+=w3x.encrypt(b''.join(struct.pack('<IIII',*x) for x in bt),w3x.hash_string('(block table)',3))
 struct.pack_into('<I',buf,8,len(buf));struct.pack_into('<II',buf,16,hoff,boff)
 destination.write_bytes(buf);temp.unlink();c=w3x.Archive(str(destination));after=inventory(c)
 assert after==uncompacted
 assert before.keys()==after.keys()
 changed=[]
 for k,(n,d) in before.items():
  if d!=after[k][1]:changed.append(n)
 assert set(changed)<=set(replacement)|{'(attributes)'}
 attr=c.read('(attributes)');ver,flags=struct.unpack_from('<II',attr)
 assert ver==100 and flags&1
 for n,d in replacement.items():assert struct.unpack_from('<I',attr,8+4*c.find(n))[0]==zlib.crc32(d)&0xffffffff
 oldfn=functions(j0.replace('\r\n','\n'));newfn=functions(j)
 assert not oldfn.keys()-newfn.keys()
 changedfn=sorted(n for n in oldfn if oldfn[n]!=newfn[n])
 # Essential trading/combat/trait/preview functions are identical except version labels.
 for n in oldfn:
  if any(x in n for x in ['ItemMix','ItemBuy','Item_Buy','Item_Mix','GSTI_','GSRI_','GS2_AuditDamage','GS2PERF_PandaChance','Trig_DamageTaken','DWT_','GS146_']):assert oldfn[n].replace('195-8','195-9')==newfn[n],n
 stats={'source_sha256':hashlib.sha256(a.data).hexdigest(),'result_sha256':hashlib.sha256(buf).hexdigest(),'source_bytes':len(a.data),'result_bytes':len(buf),'active_files':len(after),'changed_files':changed,'changed_functions':changedfn,'added_functions':sorted(newfn.keys()-oldfn.keys()),'fresh_location_calls_fixed':len(hits),'fresh_location_calls':hits,'compaction_bytes_saved':len(b.data)-len(buf)}
 (HERE/'verification.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2)+'\n')
 (HERE/'script.diff').write_text(''.join(difflib.unified_diff(j0.replace('\r\n','\n').splitlines(True),j.splitlines(True),fromfile='195-8/war3map.j',tofile='195-9/war3map.j')))
 (HERE/'war3map-new.j').write_text(j)
 print(json.dumps({k:v for k,v in stats.items() if k!='fresh_location_calls'},ensure_ascii=False,indent=2))
 return a,c
if __name__=='__main__':
 source=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'maps/reference/GS2vF_ver195-8.w3x'
 destination=ROOT/'maps/release/GS2vF_ver195-9.w3x';destination.parent.mkdir(exist_ok=True,parents=True)
 build(source,destination)
