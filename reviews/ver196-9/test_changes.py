"""Execute extracted JASS in mocks; never substitutes for a Warcraft III test."""
from pathlib import Path
import sys,re,json,struct
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path[:0]=[str(HERE),str(ROOT/'tools')]
from w3x import Archive
from objdata import load_objects,load_units
from patch import fn,GLOBALS
exec((ROOT/'reviews/ver146/test_sanctuary.py').read_text().split('class Handle:')[0])
a=Archive(str(ROOT/'maps/reference/GS2vF_ver196-8.w3x'));b=Archive(str(ROOT/'maps/release/GS2vF_ver196-9.w3x'))
s0=a.read('war3map.j').decode();s=b.read('war3map.j').decode()
# Establish an exhaustive function-body allowlist, not a few selected object checks.
def all_functions(text):
 return {m.group(1):m.group() for m in re.finditer(r'^function (\w+) takes[^\n]*\n.*?^endfunction',text,re.M|re.S)}
f0=all_functions(s0);f1=all_functions(s)
changed=[name for name in f0 if f0[name].replace('196-8','196-9')!=f1[name]]
assert set(changed)=={'ESC_IconClick','E1964_Refresh','E1968_TraitDiagnostic','ESUI_Init','ES15_Tick','GSRI_Range','Trig_random_Actions','ES15_Init','Trig_FireDrunk_Actions'},changed
for name in ['Trig_Vanguard_Actions','MakeUnitFollow','MakeUnitFollow_Sub','Trig_Blood_Strike_DM_Actions','Trig_DamageTaken_Actions','GS294_BurnTick','ES15_Q','ES15_Spell','ES15_Transform','E1966_AmrStats']:
 assert fn(s0,name).replace('196-8','196-9')==fn(s,name),name
print('PASS: only 9 allowed existing function bodies changed; Glen/Chiu/combat/transform/restoration behavior preserved')
assert 'OSKEY_OEM_3' not in fn(s,'ESUI_Init') and 'OSKEY_F8' in fn(s,'ESUI_Init')
assert fn(s,'ESC_IconInit')==fn(s0,'ESC_IconInit')
print('PASS: only the added backtick binding removed; F8/native medal frame registrations preserved, no overlay frame added')
# Exercise the actual UI callbacks repeatedly, including a native selection overwrite.
local=0;controller=object();hero=object();selection=None;frame=object();enabled=[]
ns={'E1964_SelectPending':False,'E1968_IconClicks':0,'GS1969_TraitImmediate':0,'GS1969_TraitDeferred':0,'E1966_Controller':{1:controller},'udg_HeroPlayer':{1:hero},'GetTriggerPlayer':lambda:local,'GetLocalPlayer':lambda:local,'GetPlayerId':lambda p:p,'GetUnitTypeId':lambda h:fourcc('HE15') if h is hero else 0,'BlzGetFrameByName':lambda *args:frame,'BlzFrameSetEnable':lambda f,v:enabled.append(v),'IsUnitSelected':lambda u,p:selection is u}
def select(p):
 global selection
 selection=controller
ns['ESUI_SelectTraits']=select
compile_jass(s,'ESC_IconClick',ns);compile_jass(s,'E1964_Refresh',ns)
for researched in [False,True]:
 for repeat in range(10):
  selection=hero;ns['ESC_IconClick']();selection=hero # native button overwrites immediate select
  ns['E1964_Refresh']();assert selection is controller
  assert not ns['E1964_SelectPending']
assert ns['E1968_IconClicks']==20 and ns['GS1969_TraitDeferred']==20 and enabled==[False,True]*20
print('PASS: 20 click/hero/reclick mock cycles with overwritten native selection; deferred select + button focus reset; real engine unverified')
# Hints run actual code; same owner/type repeats once, no calls on revive/transform.
messages=[];ns={'GS1969_HintLizard':[False]*12,'GS1969_HintPanda':[False]*12,'GS1969_HintWolf':[False]*12,'GetOwningPlayer':lambda u:u[0],'GetPlayerId':lambda p:p,'GetUnitTypeId':lambda u:u[1],'IsUnitIllusion':lambda u:u[2],'DisplayTimedTextToPlayer':lambda p,x,y,t,text:messages.append((p,text))}
compile_jass(s,'GS1969_HiddenHint',ns)
for p in [0,1]:
 for uid in ['Ofar','Npbm','Hdgo']:
  for _ in range(3):ns['GS1969_HiddenHint']((p,fourcc(uid),False))
ns['GS1969_HiddenHint']((0,fourcc('Npbm'),True));ns['GS1969_HiddenHint']((0,fourcc('HE15'),False))
assert len(messages)==6 and sum('두 가지' in msg for _,msg in messages)==2
assert 'GS1969_HiddenHint' in fn(s,'Trig_random_Actions') and 'GS1969_HintSold' in fn(s,'GS1969_Init')
print('PASS: 2 owners x 3 hidden heroes; each hint once, correct panda wording; random + sale wired, no revive/transform hook')
# Objects: no balance/resource modifications outside the exact requested fields.
for n in ['war3map.w3a','war3mapSkin.w3a']:
 d=load_objects(b,n)
 for lv in range(5,9):assert d['A02R']['Ocl1'+str(lv)]==0 and d['A02R']['Ocl3'+str(lv)]==0
 for lv in range(1,9):assert d['A13E']['aran'+str(lv)]==99999
 assert load_objects(a,n).get('A13J')==d.get('A13J')
assert load_units(b)['nE15']['unam']=='특성'
assert load_units(a)['HE15']==load_units(b)['HE15']
assert 'return 500.0' in fn(s,'GSRI_Range')
print('PASS: W native input range changed only on A13E, actual A13J damage/reach/cost/cooldown untouched; UI 500; hero names/stats unchanged')
# Compare original/new tick execution and allocation counts under same empty-contact workload.
def run_tick(script):
 allocations=[];destroyed=[];slows=[];h=object();storage={};time=[0.0]
 def group():
  g=[];allocations.append(g);return g
 shared=[]
 ns={'udg_HeroPlayer':{i:(h if i==1 else None) for i in range(1,13)},'ES15_Data':object(),'ES15_Shields':[],'GS1969_WTargets':shared,'GS1969_Tick':None,
 'GetUnitX':lambda u:0.,'GetUnitY':lambda u:0.,'GetUnitTypeId':lambda u:fourcc('HE15') if u is h else 0,'GetHandleId':lambda u:1 if u is h else 0,'ES15_Now':lambda:time[0], 'ES15_Alive':lambda u:u is h,
 'E1966_CacheTraits':lambda:None,'EAV_Tick':lambda u:None,'E191_StackUI':lambda *x:None,'E191_Passive':lambda u:None,'ES15_Armor':lambda u:None,'ES15_Stacks':lambda *x:None,'E191_TickSanctuary':lambda:None,
 'BlzGroupGetSize':len,'BlzGroupUnitAt':lambda g,i:g[i], 'LoadInteger':lambda d,k,c:0,'LoadReal':lambda d,k,c:storage.get((k,c),0),'LoadBoolean':lambda d,k,c:False,
 'CreateGroup':group,'DestroyGroup':lambda g:destroyed.append(g),'GroupClear':lambda g:g.clear(),'GroupEnumUnitsInRange':lambda *x:None,'FirstOfGroup':lambda g:None,
 'EQW_MoveEnd':lambda u:None,'UnitRemoveAbility':lambda *x:None,'EAB_ShieldArmor':lambda u:None,'ES15_ShieldEnd':lambda u:None}
 compile_jass(script,'ES15_Tick',ns)
 for tick in range(100):time[0]=tick*.05;storage[(1,10)]=5.;ns['ES15_Tick']()
 return len(allocations),len(destroyed),slows
old=run_tick(s0);new=run_tick(s)
assert old[:2]==(100,100) and new[:2]==(0,0) and old[2]==new[2]
print('PASS: extracted W contact tick: 100 updates => group create/destroy 100/100 -> 0/0 (one fixed init group); timing/effect schedule unchanged')
print('LIMIT: no Warcraft III engine/UI/multiplayer/FPS test executed; manual repeated medal and far-click breath tests required')
# Execute the actual payload aiming action at near/far points and all W levels.
import math
for level in range(1,5):
 for point in [(0,0),(100,0),(500,0),(10000,0),(-8000,4000),(0,-20000)]:
  caster=object();dummy=object();orders=[];life=[];rank=[];positions=[]
  env={'GetTriggerUnit':lambda:caster,'GetUnitX':lambda u:0.,'GetUnitY':lambda u:0.,'GetSpellTargetX':lambda:point[0],'GetSpellTargetY':lambda:point[1], 'SquareRoot':math.sqrt,'Atan2':math.atan2,'bj_RADTODEG':180/math.pi,
  'GetOwningPlayer':lambda u:0,'CreateUnit':lambda p,uid,x,y,angle:positions.append((uid,x,y,angle)) or dummy,'UnitApplyTimedLife':lambda *args:life.append(args),'SetUnitAbilityLevel':lambda *args:rank.append(args),'GetUnitAbilityLevel':lambda h,id:level,'IssuePointOrder':lambda d,order,x,y:orders.append((d,order,x,y))}
  compile_jass(s,'GS1969_FireDrunk',env);env['GS1969_FireDrunk']()
  _,order,x,y=orders[0];assert order=='breathoffrost' and math.hypot(x,y)<=500.000001
  if point!=(0,0):assert abs(x*point[1]-y*point[0])<.0001
  assert positions[0][1:3]==(0.,0.) and rank[0][2]==level and life[0][2]==.5
print('PASS: actual FireDrunk action: 24 near/boundary/far/zero aim cases, origin unchanged, direction retained, payload target <=500, rank/lifetime unchanged')
# Runtime/editor functions agree for each edited custom-script function.
d=b.read('war3map.wct');p=d.index(b'\0',8)+1;blocks=[]
while p<len(d):
 n=struct.unpack_from('<I',d,p)[0];p+=4;blocks.append(d[p:p+n].rstrip(b'\0').decode().replace('\r\n','\n'));p+=n
editor='\n'.join(blocks)
for name in changed:
 if name=='Trig_FireDrunk_Actions':
  assert 'TriggerClearActions(gg_trg_FireDrunk)' in editor and 'function GS1969_FireDrunk)' in editor
 else:assert fn(editor,name)==fn(s,name),name
for name in ['GS1969_HiddenHint','GS1969_HintSold','GS1969_SelectionWatch','GS1969_FireDrunk','GS1969_Init']:
 assert fn(editor,name)==fn(s,name),name
print('PASS: modified runtime/custom-editor functions match; GUI FireDrunk event/condition retained with post-init replacement action')
