"""Execute production burst action with injected context/BJ interference and native failures.
These checks do not simulate Warcraft's actual damage/buff application.
"""
from pathlib import Path
import sys,re,collections
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from w3x import Archive
from objdata import load_objects
exec((ROOT/'reviews/ver146/test_sanctuary.py').read_text().split('class Handle:')[0])
a=Archive(str(ROOT/'maps/release/GS2vF_ver195-13.w3x'));s=a.read('war3map.j').decode();base=load_objects(a,'war3map.w3a')['A0CV'];skin=load_objects(a,'war3mapSkin.w3a')['A0CV']
# Both containers explicitly carry the same real payload, not only mana/radius.
for level in range(1,9):
 for d in [base,skin]:
  lv=(level-1)%4+1;talent=level>4
  assert d['alev']==8 and d['aher']==0
  assert d['amcs'+str(level)]==0 and d['aare'+str(level)]==300
  assert d['adur'+str(level)]==d['ahdu'+str(level)]==1.5
  assert d['Htc1'+str(level)]==40*lv+100*talent
  assert abs(d['Htc3'+str(level)]-(.10+.05*lv+.50*talent))<.00001
  assert d['Htc4'+str(level)]==d['Htc5'+str(level)]==0
print('PASS: native damage/slow/duration/targets/rank metadata explicitly pinned in base and skin for all 8 ranks')
for level in range(1,5):
 for trait in [0,1,2]:
  for failure in ['none','add','rank','order','create']:
   hero={'type':fourcc('Odrt'),'level':level,'owner':1,'x':125,'y':250};visual={'type':fourcc('h00W'),'mana':0};dummy={'type':fourcc('ewsp'),'mana':0,'rank':0};intruder={'type':0,'level':0,'owner':2};ctx={'event':hero,'last':intruder};calls=[];status={}
   def create_visual(*args):
    assert args[1]==fourcc('h00W') and args[2]==1 and args[3]==(125,250)
    ctx['event']=intruder;ctx['last']=visual;calls.append('visual')
   def create_caster(owner,kind,x,y,facing):
    assert owner==1 and kind==fourcc('ewsp') and (x,y)==(125,250)
    ctx['last']=intruder;calls.append('caster')
    return None if failure=='create' else dummy
   def add(u,aid):
    assert u is dummy
    calls.append(('add',aid));return not(failure=='add' and aid==fourcc('A0CV'))
   def setrank(u,aid,r):
    assert u is dummy and r==level+(4 if trait else 0)
    u['rank']=0 if failure=='rank' else r
   def order(u,oid):
    assert u is dummy and oid==852096 and dummy['mana']==1000
    calls.append('order');return failure!='order'
   def field(p,f,i):return base[f+str(i+1)]
   ns={'GS19513_FlameBurstStatus':status,'bj_UNIT_FACING':270,'UNIT_RF_CAST_POINT':1,'UNIT_RF_CAST_BACK_SWING':2,'UNIT_STATE_MANA':3,'UNIT_STATE_MAX_MANA':4,'ABILITY_RLF_AOE_DAMAGE':'Htc1','ABILITY_RLF_AREA_OF_EFFECT':'aare','ABILITY_RLF_MOVEMENT_SPEED_REDUCTION_PERCENT_HTC3':'Htc3','GetTriggerUnit':lambda:ctx['event'],'GetOwningPlayer':lambda u:u['owner'],'GetPlayerId':lambda p:p,'GetUnitAbilityLevel':lambda u,aid:u['level'] if aid==fourcc('A0CP') else u.get('rank',0),'GetPlayerTechCount':lambda *x:trait,'GetUnitX':lambda u:u['x'],'GetUnitY':lambda u:u['y'],'Location':lambda x,y:(x,y),'GS2V84_CreateNUnitsAtLoc_3':create_visual,'UnitApplyTimedLife':lambda *x:None,'GetLastCreatedUnit':lambda:ctx['last'],'CreateUnit':create_caster,'UnitAddAbility':add,'BlzSetUnitRealField':lambda *x:None,'GetUnitState':lambda u,f:1000,'SetUnitState':lambda u,f,v:u.update(mana=v),'SetUnitAbilityLevel':setrank,'BlzGetUnitAbility':lambda *x:dummy,'BlzGetAbilityRealLevelField':field,'BlzEndUnitAbilityCooldown':lambda *x:None,'IssueImmediateOrderById':order,'I2S':str,'R2S':lambda x:f'{x:.3f}'}
   for name in ['GS19513_Flag','GS19513_FlameBurstAction']:compile_jass(s,name,ns)
   ns['GS19513_FlameBurstAction']()
   assert calls[:2]==['visual','caster']
   expected_order=failure not in ['add','rank','create'];assert ('order' in calls)==expected_order
   assert ('명령접수=1' in status[1])==(failure=='none')
   if failure=='none':assert f"내부={level+(4 if trait else 0)}/{level+(4 if trait else 0)}" in status[1]
print('PASS: 60 cases: 4 skill levels x 3 research counts x 5 native success/failure modes; locals survive poisoned event/BJ state and failed orders never report acceptance')
# Startup hook is bounded and idempotent; it replaces only this trigger's actions.
callbacks=[];registered=[];cleared=[];destroyed=[];gg=object()
ns={'GS19513_FlameBurstStarted':False,'GS19513_FlameBurstInstalled':False,'gg_trg_Flame_Burst':gg,'GS19513_FlameBurstAction':lambda:None,'GS19513_FlameBurstChat':lambda:None,'CreateTrigger':lambda:object(),'Player':lambda i:i,'TriggerRegisterPlayerChatEvent':lambda *args:registered.append(args),'TriggerAddAction':lambda t,f:callbacks.append((t,f)),'CreateTimer':lambda:object(),'TimerStart':lambda t,d,p,f:callbacks.append(('timer',f)),'GetExpiredTimer':lambda:None,'DestroyTimer':lambda t:destroyed.append(t),'TriggerClearActions':lambda t:cleared.append(t)}
ss=re.sub(r'\bfunction (\w+)(?=[,)])',r'\1',s)
for name in ['GS19513_FlameBurstInstall','GS19513_FlameBurstInit']:compile_jass(ss,name,ns)
ns['GS19513_FlameBurstInit']();ns['GS19513_FlameBurstInit']();assert len(registered)==12
assert sum(t=='timer' for t,f in callbacks)==1
ns['GS19513_FlameBurstInstall']();assert cleared==[gg] and len(destroyed)==1 and ns['GS19513_FlameBurstInstalled']
assert callbacks[-1]==(gg,ns['GS19513_FlameBurstAction'])
print('PASS: one-time initialization and post-GUI action replacement; no per-cast timer or new global damage listener')
# Other gameplay objects and functions stay as before.
old=Archive(str(ROOT/'maps/release/GS2vF_ver195-11.w3x'));oldj=old.read('war3map.j').decode()
funcs=lambda text:{m[1]:m[0] for m in re.finditer(r'^function (\w+) takes .*?^endfunction',text,re.M|re.S)}
x=funcs(oldj);y=funcs(s)
for n in x:
 if n not in ['Trig_Flame_Burst_Actions','InitCustomTriggers']:
  assert x[n].replace('195-11','195-13')==y[n],n
for filename in ['war3map.w3u','war3mapSkin.w3u','war3map.w3q','war3mapSkin.w3q','war3map.w3t','war3mapSkin.w3t','war3map.wts']:assert old.read(filename)==a.read(filename),filename
for filename in ['war3map.w3a','war3mapSkin.w3a']:
 x=load_objects(old,filename);y=load_objects(a,filename)
 for aid in x:
  if aid!='A0CV':assert x[aid]==y[aid],(filename,aid)
print('PASS: all other skills/traits/items/recipes/range preview preserved; only burst runtime, initialization and version text differ')
print('LIMIT: actual damage and slow application in Warcraft require an engine test; this suite cannot certify that outcome')
