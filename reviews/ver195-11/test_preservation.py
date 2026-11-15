"""Data and rollback-isolation checks. These do not reproduce a Warcraft client hang."""
from pathlib import Path
import sys,re,json,math,importlib.util
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import w3x
from objdata import load_objects
spec=importlib.util.spec_from_file_location('trait_build',HERE/'build.py');build=importlib.util.module_from_spec(spec);spec.loader.exec_module(build)
normal=w3x.Archive(str(ROOT/'maps/release/GS2vF_ver195-11.w3x'));compare=w3x.Archive(str(ROOT/'maps/diagnostics/GS2vF_ver195-12_compare1958.w3x'));old=w3x.Archive(str(ROOT/'maps/release/GS2vF_ver195-10.w3x'));baseline=w3x.Archive(str(ROOT/'maps/reference/GS2vF_ver195-8.w3x'))
assert old.read('war3map.j').replace(b'195-10',b'195-11')==normal.read('war3map.j')
assert baseline.read('war3map.j').replace(b'195-8','195-12 비교본'.encode())==compare.read('war3map.j')
assert b'GS1959_' not in compare.read('war3map.j')
print('PASS: normal runtime changes only version labels; comparison runtime is exactly 195-8 plus its distinct version labels')
for name in ['war3map.w3a','war3mapSkin.w3a']:
 assert normal.read(name)==compare.read(name),name
 a=load_objects(old,name);b=load_objects(normal,name)
 for id in a:
  if id not in build.HELPERS:assert a[id]==b[id],(name,id)
  else:
   for key in set(a[id])|set(b[id]):
    if not re.fullmatch(r'amcs\d+',key):assert a[id].get(key)==b[id].get(key),(name,id,key)
   for level in range(1,load_objects(normal,'war3map.w3a')[id]['alev']+1):assert b[id]['amcs'+str(level)]==0
print('PASS: 13 whitelisted helper costs pinned; all damage/target/range/cooldown/buff fields and every other ability preserved')
for name in ['war3map.w3u','war3mapSkin.w3u','war3map.w3q','war3mapSkin.w3q','war3map.w3t','war3mapSkin.w3t','war3map.wts']:
 assert old.read(name)==normal.read(name)==compare.read(name),name
print('PASS: unit/hero/trait/item objects, recipe/purchase data and strings unchanged and equal between normal/comparison builds')
# Explicitly protect the already-fixed Shinta and user-confirmed Ranger.
for file in ['war3map.w3a','war3mapSkin.w3a']:
 x=load_objects(old,file);y=load_objects(normal,file)
 for id in ['A13V','A12D','A0VR','A0VQ','A13R','A13Q','A13S','A00Q','A0O8','A11R']:
  assert x.get(id)==y.get(id),(file,id)
print('PASS: Shinta and Ranger ability records unchanged')
# Validate every live file can be decoded in both builds, not just known script paths.
for a in [normal,compare]:
 files=build.inventory(a);assert len(files)==1069
 data=a.read('war3map.wct');p=data.index(b'\0',8)+1;blocks=0
 while p<len(data):
  import struct
  n=struct.unpack_from('<I',data,p)[0];p+=4
  if n:assert data[p+n-1]==0
  p+=n;blocks+=1
 assert p==len(data) and blocks==903
print('PASS: 1,069 decoded live entries and 903 WCT block lengths in each map')
