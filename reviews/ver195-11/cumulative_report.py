"""Generate the cumulative memo from the actual F8FIX and latest map contents.
Requires dclimplode only for the F8 archive's PKWARE-compressed entries.
"""
from pathlib import Path
import sys,json,hashlib,difflib,struct
from zipfile import ZipFile,ZIP_DEFLATED
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import w3x,dclimplode
from objdata import iter_mods
from build import inventory
orig_decompress=w3x._decompress
def decompress(data,size):
 if len(data)!=size and data[0]==8:
  result=dclimplode.decompressobj().decompress(data[1:]);assert len(result)==size;return result
 return orig_decompress(data,size)
w3x._decompress=decompress

def fields(a,name):
 result={}
 for table,base,new,si,flag,mods in iter_mods(a.read(name),name.endswith(('.w3a','.w3d','.w3q'))):
  oid=new if new!='\0'*4 else base
  result[(table,oid,si,'BASE')]=base
  result[(table,oid,si,'SET_FLAG')]=flag
  for m in mods:result[(table,oid,si,m['id'],m['level'],m['data'])]=m['value']
 return result

def report():
 old=w3x.Archive(str(ROOT/'maps/GS2vF_ver19.w3x'));latest=w3x.Archive(str(ROOT/'maps/release/GS2vF_ver195-11.w3x'))
 a=inventory(old);b=inventory(latest);lines=[]
 def emit(s=''):lines.append(str(s))
 emit('가디언 스피리츠 II — 최초 F8FIX 대비 195-11 전체 변경 기록')
 emit('작성일: 2026-10-26 (Asia/Seoul)')
 emit('원본: maps/GS2vF_ver19.w3x (내부 F8FKfix) / SHA256 '+hashlib.sha256(old.data).hexdigest())
 emit('최신: maps/release/GS2vF_ver195-11.w3x / SHA256 '+hashlib.sha256(latest.data).hexdigest())
 emit('중간 버전의 제작 의도는 추측하지 않으며, 실제 파일의 차이를 전부 기록합니다. 코드/모사 검사는 실제 게임 성능·동작 검증이 아닙니다.')
 emit('\n=== 이번 변경 상세 ===\n');emit((HERE/'README.md').read_text())
 emit('\n=== 저장소 변경 이력 ===\n');emit((ROOT/'CHANGELOG.md').read_text())
 emit('\n=== 195-7과 195-8 비교 ===\n');emit((ROOT/'reviews/ver195-9/baseline-comparison.json').read_text())
 emit('\n=== 195-10과 195-11 런타임 버전 표기 diff ===\n');emit((HERE/'script.diff').read_text())
 emit('\n=== 최초 F8FIX 대비 활성 파일 전체 목록과 SHA256 ===\n')
 manifest=[]
 for k in sorted(a.keys()|b.keys()):
  x=a.get(k);y=b.get(k);status='추가' if x is None else '삭제' if y is None else '동일' if x[1]==y[1] else '변경'
  d={'file':(y or x)[0],'status':status}
  for label,value in [('F8',x),('195-11',y)]:
   if value:d[label]={'bytes':len(value[1]),'sha256':hashlib.sha256(value[1]).hexdigest()}
  emit(json.dumps(d,ensure_ascii=False));manifest.append(d)
 emit('\n=== 최초 F8FIX 대비 객체 전체 필드 변경 ===\n')
 count=0
 for k in sorted(a.keys()&b.keys()):
  if k.endswith(('.w3a','.w3b','.w3d','.w3h','.w3q','.w3t','.w3u')):
   x=fields(old,a[k][0]);y=fields(latest,b[k][0]);emit('\n-- '+b[k][0]+' --')
   for field in sorted(x.keys()|y.keys(),key=str):
    if field not in x or field not in y or x[field]!=y[field]:
     emit(json.dumps({'key':field,'F8':x.get(field),'195-11':y.get(field),'added':field not in x,'removed':field not in y},ensure_ascii=False));count+=1
 emit('\n=== 최초 F8FIX 대비 문자열·런타임·에디터·기타 텍스트 전체 diff ===\n')
 for k in sorted(a.keys()|b.keys()):
  if not k.endswith(('.j','.wts','.wct','.txt','.fdf','.toc','.lua','.slk')):continue
  x=a.get(k,('',b''))[1];y=b.get(k,('',b''))[1]
  if x==y:continue
  if k.endswith('.wct'):
   # Length-prefixed binary container: expose every block independently as UTF-8.
   def codeblocks(d):
    if not d:return []
    p=d.index(b'\0',8)+1;out=[];i=0
    while p<len(d):
     n=struct.unpack_from('<I',d,p)[0];p+=4;c=d[p:p+n];p+=n
     out.append('// WCT block '+str(i)+'\n'+c.rstrip(b'\0').decode('utf-8','replace').replace('\r\n','\n')+'\n');i+=1
    return ''.join(out).splitlines(True)
   xx=codeblocks(x);yy=codeblocks(y)
  else:
   xx=x.decode('utf-8','replace').replace('\r\n','\n').splitlines(True);yy=y.decode('utf-8','replace').replace('\r\n','\n').splitlines(True)
  emit(''.join(difflib.unified_diff(xx,yy,fromfile='F8/'+k,tofile='195-11/'+k)))
 emit('\n=== 최신 검증 데이터 ===\n');emit((HERE/'verification.json').read_text())
 emit('객체 변경 필드(원본/세트 정보 포함): '+str(count))
 output=ROOT/'F8_to_latest_all_changes.txt';output.write_text('\r\n'.join(lines).replace('\r\r\n','\r\n'),encoding='utf-8-sig',newline='')
 with ZipFile(ROOT/'F8_to_latest_all_changes.zip','w',ZIP_DEFLATED,compresslevel=9) as z:z.write(output,output.name)
 with ZipFile(ROOT/'F8_to_latest_all_changes.zip') as z:assert z.testzip() is None and z.read(output.name)==output.read_bytes()
 print('Cumulative report:',output.stat().st_size,'bytes,',count,'object field changes,',len(manifest),'file records')
if __name__=='__main__':report()
