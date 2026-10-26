"""Exercise existing reentry guards for the reported heroes, with mocked damage events."""
from pathlib import Path
import sys,collections
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from w3x import Archive
exec((ROOT/'reviews/ver146/test_sanctuary.py').read_text().split('class Handle:')[0])
s=Archive(str(ROOT/'maps/release/GS2vF_ver195-11.w3x')).read('war3map.j').decode()
# Worst-case nested attack damage reenters Flame Beast's passive immediately.
hero=object();dummy=object();table={};calls=[]
ns={'GS2FB_Data':table,'udg_MBTime':object(),'GetTriggerUnit':lambda:hero,'GetUnitAbilityLevel':lambda u,a:4,'GetHandleId':lambda u:1,'TimerGetElapsed':lambda t:100.0,'GetUnitTypeId':lambda u:fourcc('OFl1'),'GetEventDamage':lambda:100.0,'BlzGetEventIsAttack':lambda:True,'GetOwningPlayer':lambda u:1,'GetPlayerTechCount':lambda *args:1,'LoadReal':lambda h,p,c:h.get((p,c),0),'SaveReal':lambda h,p,c,v:h.__setitem__((p,c),v),'GetRandomInt':lambda a,b:calls.append('rng') or 1,'CreateUnit':lambda *x:dummy,'GetUnitX':lambda u:0,'GetUnitY':lambda u:0,'UnitAddAbility':lambda *x:None,'SetUnitAbilityLevel':lambda *x:None,'IssueImmediateOrder':lambda *x:None,'UnitApplyTimedLife':lambda *x:None,'I2R':float,'TextTag':lambda *x:None}
def area(*args):
 calls.append('area')
 ns['GS2FB_Damaged']()
ns['GS2FB_Area']=area;compile_jass(s,'GS2FB_Damaged',ns);ns['GS2FB_Damaged']()
assert calls==['rng','area'] and table[(1,1)]==104.0
print('PASS: existing Flame Beast passive cooldown is set before area damage; nested callback cannot proc again')
# Existing Backstab clears its armed state before its additional damage.
unit=object();ns={'udg_Hero_DrA_Backstab':True,'udg_Hero_DrA':unit,'udg_Hero_DrA_BaskStabAngle':0,'GetEventDamageSource':lambda:unit,'GetTriggerUnit':lambda:unit,'UnitRemoveBuffBJ':lambda *x:None,'GetUnitAbilityLevelSwapped':lambda *x:4,'GetPlayerTechCountSimple':lambda *x:1,'GetOwningPlayer':lambda u:1,'GetUnitLoc':lambda u:object(),'CreateNUnitsAtLoc':lambda *x:None,'GetLastCreatedUnit':lambda:object(),'RemoveLocation':lambda p:None,'UnitApplyTimedLifeBJ':lambda *x:None,'UNIT_STATE_LIFE':1,'GetUnitStateSwap':lambda *x:1000.0,'I2R':float,'R2I':int,'Trig_Backstab_Atk_Func005C':lambda:True,'TextTagForce':lambda *x:None,'GetPlayersAll':lambda:None,'AddSpecialEffectTargetUnitBJ':lambda *x:None,'GetLastCreatedEffectBJ':lambda:None,'DestroyEffectBJ':lambda *x:None,'PolledWait':lambda d:None}
hits=[]
def damage(*args):
 assert ns['udg_Hero_DrA_Backstab'] is False
 hits.append(args[2])
ns['bj_UNIT_FACING']=270;ns['UnitDamageTargetBJ']=damage;ns['ATTACK_TYPE_HERO']=1;ns['DAMAGE_TYPE_DIVINE']=1
compile_jass(s,'Trig_Backstab_Atk_Actions',ns);ns['Trig_Backstab_Atk_Actions']();assert hits==[300.0] and ns['udg_Hero_DrA_BackstabTarget'] is None
print('PASS: existing Soen backstab armed flag is cleared before bonus damage and pending target is cleared after the wait')
print('LIMIT: native engine callbacks/other heroes/items/resources and the reported client freeze are not reproduced by these mocks')
