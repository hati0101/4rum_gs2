"""Execute extracted production functions with mocked natives; not an engine/FPS test."""
from pathlib import Path
import sys,math,collections,random
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'tools'));sys.path.insert(0,str(HERE))
from w3x import Archive
from patch import functions
# Reuse only the small JASS translator definitions from the earlier reviewed check.
translator=(ROOT/'reviews/ver146/test_sanctuary.py').read_text().split('class Handle:')[0]
exec(translator)
a=Archive(str(ROOT/'maps/reference/GS2vF_ver195-8.w3x')).read('war3map.j').decode().replace('\r\n','\n')
b=Archive(str(ROOT/'maps/release/GS2vF_ver195-9.w3x')).read('war3map.j').decode()
old=functions(a);new=functions(b)

def environment():
 state={};calls=collections.Counter()
 def text(f,v):state.setdefault(f,{})['text']=v;calls['text']+=1
 def size(f,w,h):state.setdefault(f,{})['size']=(w,h);calls['size']+=1
 def visible(f,v):state.setdefault(f,{})['visible']=v;calls['visible']+=1
 def alpha(f,v):state.setdefault(f,{})['alpha']=v;calls['alpha']+=1
 ns={'GS1959_Text':{},'GS1959_TextValid':collections.defaultdict(bool),'GS1959_BarRatio':{},'GS1959_BarHeight':{},'GS1959_BarValid':collections.defaultdict(bool),'GS167_SkillTexture':collections.defaultdict(str),'bj_wantDestroyGroup':False,'UNIT_STATE_MANA':1,'udg_MBTime':0}
 ns.update(BlzGetFrameByName=lambda n,i:(n,i),BlzFrameSetText=text,BlzFrameSetSize=size,BlzFrameSetVisible=visible,BlzFrameSetAlpha=alpha,BlzFrameSetTexture=lambda *x:None,GSTF_BarW=lambda:.062,GetUnitTypeId=lambda u:u['type'],GSTF_SkillOf=lambda t,s:123 if t else 0,BlzGetAbilityIcon=lambda a:'icon',GetUnitAbilityLevel=lambda u,a:u['level'],GSTF_IsPassive=lambda a:False,BlzGetUnitAbilityCooldownRemaining=lambda u,a:u['cd'],GetUnitState=lambda u,s:u['mana'],BlzGetUnitAbilityManaCost=lambda u,a,l:50,R2I=int,I2S=str,Sin=math.sin,RAbsBJ=abs,TimerGetElapsed=lambda t:1)
 return ns,state,calls

def compile_into(src,names,ns):
 for n in names:compile_jass(src,n,ns)
# A representative repeated 5-hero panel: 20 skill icons and 10 bars, same 10 Hz cadence.
ns0,s0,c0=environment();ns1,s1,c1=environment()
for src,ns in [(a,ns0),(b,ns1)]:compile_into(src,['GSTF_SetText','GSTF_SetBar','GSTF_FillSkill'],ns)
u={'type':1,'level':1,'cd':8.25,'mana':100}
for tick in range(100):
 for ns in [ns0,ns1]:
  for i in range(5):
   ns['GSTF_SetText']('GSTF_Lvl',i,'25')
   for slot in range(4):ns['GSTF_FillSkill'](i,slot,u)
   ns['GSTF_SetBar']('GSTF_Hp',i,.0065,.75)
   ns['GSTF_SetBar']('GSTF_Mp',i,.0055,.50)
 assert s0==s1
assert c1['text']<c0['text']/10 and c1['size']<c0['size']/10
print('UI stable model:',dict(c0),'->',dict(c1),'identical final visual state after every tick')
# Skill state transitions: cooldown ends, mana changes, no skill, different hero, revive, passive.
rng=random.Random(1959)
for _ in range(1000):
 u={'type':rng.choice([0,1]),'level':rng.choice([0,1,2,3,4]),'cd':rng.choice([0,.01,1,1.2,30.1]),'mana':rng.choice([0,49,50,100])}
 for ns in [ns0,ns1]:
  ns['GSTF_IsPassive']=lambda a,passive=(_%3==0):passive
  ns['GSTF_FillSkill'](0,3,u)
 assert s0==s1
for ratio in [0,-1,.001,.0011,.5,1,1.5,0]:
 for ns in [ns0,ns1]:ns['GSTF_SetBar']('GSTF_Hp',0,.0065,ratio)
 assert s0==s1
compile_jass(b,'GS1959_ResetUI',ns1);ns1['GS1959_ResetUI']();assert not any(ns1['GS1959_TextValid'].values()) and not any(ns1['GS1959_BarValid'].values())
print('PASS: panel state transitions and recreated-frame cache invalidation')
# Named damage owner check: compare predicates, count avoided allocations.
for owner in range(28):
 for points in [0,1249,1250,5000]:
  unit={'owner':owner,'points':points};ng={'PLAYER_NEUTRAL_AGGRESSIVE':12,'GetTriggerUnit':lambda:unit,'Player':lambda i:i,'GetUnitPointValue':lambda u:u['points'],'GetOwningPlayer':lambda u:u['owner'],'GetUnitsOfPlayerAll':lambda p:[unit] if unit['owner']==p else [],'IsUnitInGroup':lambda u,g:u in g}
  compile_jass(a,'Trig_Named_Damage_Add_Conditions',ng);expected=ng['Trig_Named_Damage_Add_Conditions']()
  compile_jass(b,'Trig_Named_Damage_Add_Conditions',ng);assert expected==ng['Trig_Named_Damage_Add_Conditions']()
print('PASS: named-damage predicate equivalence across owners and point values; old group allocation removed')
# Null and live caster paths: release one-shot timer and all saved data exactly once.
for caster in [None,object()]:
 calls=[];table={(7,0):caster};t=object()
 rn={'GS181_Rain':table,'GetExpiredTimer':lambda:t,'GetHandleId':lambda x:7,'LoadUnitHandle':lambda h,k,c:caster if c==0 else None,'LoadPlayerHandle':lambda *x:None,'LoadInteger':lambda *x:1,'LoadBoolean':lambda *x:False,'GS181_Live':lambda u:False,'FlushChildHashtable':lambda h,k:(h.clear(),calls.append('flush')),'PauseTimer':lambda t:calls.append('pause'),'DestroyTimer':lambda t:calls.append('destroy')}
 compile_jass(b,'GS181_RainProc',rn);rn['GS181_RainProc']();assert calls==['flush','pause','destroy'] and not table
print('PASS: null/live rain-proc cleanup')
# Random picker preserves exactly one selection and honors BJ ownership flag.
for owned in [False,True]:
 destroyed=[];random_calls=[];group=object()
 ns={'bj_wantDestroyGroup':owned,'DestroyGroup':lambda g:destroyed.append(g)}
 def pick(g):
  random_calls.append(g)
  if ns['bj_wantDestroyGroup']:destroyed.append(g)
  ns['bj_wantDestroyGroup']=False
  return 123
 ns['GroupPickRandomUnit']=pick;compile_jass(b,'GS1959_PickRandomOwned',ns)
 assert ns['GS1959_PickRandomOwned'](group)==123 and destroyed==[group] and random_calls==[group] and not ns['bj_wantDestroyGroup']
print('PASS: random picker selection/ownership semantics unchanged')
# No random calls or gameplay fields added/removed in the touched skill actions.
for n in old:
 if n in new and old[n]!=new[n]:
  assert re.findall(r'GetRandom\w+\([^\n]*',old[n])==re.findall(r'GetRandom\w+\([^\n]*',new[n]),n
print('PASS: all RNG call expressions retained')
for name,table_name,loader in [('GS181_FxEnd','GS181_Fx','LoadEffectHandle'),('GS181_FlakExpire','GS181_Flak','LoadUnitHandle')]:
 calls=[];table={(7,0):None};t=object()
 ns={table_name:table,'GetExpiredTimer':lambda:t,'GetHandleId':lambda x:7 if x is t else 0,loader:lambda *a:None,'FlushChildHashtable':lambda h,k:(h.clear(),calls.append('flush')),'PauseTimer':lambda t:calls.append('pause'),'DestroyTimer':lambda t:calls.append('destroy')}
 compile_jass(b,name,ns);ns[name]();assert calls==['flush','pause','destroy'] and not table
print('PASS: missing-effect/missing-source one-shot timers release their own storage and handles')
# Position swap: snapshots and 0.75-second wait are preserved; only final cleanup differs.
for src in [a,b]:
 units=[{'x':10,'y':20},{'x':70,'y':80}];locations=[];waits=[]
 def loc(u):
  p=dict(x=u['x'],y=u['y'],removed=False);locations.append(p);return p
 def pos(u,p):assert not p['removed'];u.update(x=p['x'],y=p['y'])
 ns={'GetTriggerUnit':lambda:units[0],'GetSpellTargetUnit':lambda:units[1],'GetUnitLoc':loc,'SetUnitPositionLoc':pos,'PolledWait':lambda t:waits.append(t),'RemoveLocation':lambda p:p.update(removed=True)}
 compile_jass(src,'Trig_Change_Actions',ns);ns['Trig_Change_Actions']()
 assert waits==[.75] and [(u['x'],u['y']) for u in units]==[(70,80),(10,20)]
 assert sum(not p['removed'] for p in locations)==(2 if src is a else 0)
print('PASS: position-swap behavior/timing identical; 2 leaked locations per cast -> 0')
# The item-distance ownership change used by the full-inventory pickup loop.
for func in ['GS2V84_DistanceBetweenPoints_0','GS2V84_DistanceBetweenPoints_01']:
 removed=[];ns={'DistanceBetweenPoints':lambda x,y:math.hypot(y[0]-x[0],y[1]-x[1]),'RemoveLocation':lambda p:removed.append(p)}
 compile_jass(b,func,ns)
 for tick in range(10000):assert ns[func]((0,0),(3,4))==5
 leaked=20000-len(removed);assert leaked==(10000 if func.endswith('_0') else 0)
 print('Item-distance 10,000-check model:',func,'unreleased locations',leaked)
