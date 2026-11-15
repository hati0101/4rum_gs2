"""Check production cast/rank selection against decoded objects; mocked natives, no game engine."""
from pathlib import Path
import sys,re,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from w3x import Archive
from objdata import load_objects
exec((ROOT/'reviews/ver146/test_sanctuary.py').read_text().split('class Handle:')[0])
a=Archive(str(ROOT/'maps/release/GS2vF_ver195-9.w3x'));b=Archive(str(ROOT/'maps/release/GS2vF_ver195-10.w3x'))
old=a.read('war3map.j').decode();new=b.read('war3map.j').decode()
assert old.replace('195-9','195-10')==new
for name in ['Trig_Flame_Burst_Actions','Trig_Flame_Burst_Conditions','InitTrig_Flame_Burst','GS195_RangerPoisonTick','GS195_RangerPoisonStart','Trig_Poison_Sniping_Poison_Actions']:
 assert fn(old,name)==fn(new,name)
# Establish whether the reported feature was changed in 195-9.
for file in ['maps/reference/GS2vF_ver195-7.w3x','maps/reference/GS2vF_ver195-8.w3x']:
 base=Archive(str(ROOT/file));assert fn(base.read('war3map.j').decode(),'Trig_Flame_Burst_Actions')==fn(old,'Trig_Flame_Burst_Actions')
 assert load_objects(base,'war3map.w3a')['A0CV']==load_objects(a,'war3map.w3a')['A0CV']
print('PASS: Flame Burst trigger and data identical in 195-7/8/9; ranger runtime unchanged in 195-10')
ability=load_objects(b,'war3map.w3a')['A0CV'];skin=load_objects(b,'war3mapSkin.w3a')['A0CV']
for trait in [0,1]:
 for level in range(1,5):
  calls=[];dummy={'rank':0,'mana':0};hero=object()
  def rank(a,u,r):dummy['rank']=r;calls.append(('rank',r))
  def order(u,cmd):
   r=dummy['rank'];assert cmd=='thunderclap'
   assert ability['amcs'+str(r)]==skin['amcs'+str(r)]==0
   assert ability['aare'+str(r)]==skin['aare'+str(r)]==300
   assert dummy['mana']>=ability['amcs'+str(r)]
   calls.append(('order',cmd))
  ns={'GetTriggerUnit':lambda:hero,'GetOwningPlayer':lambda u:0,'GetUnitLoc':lambda u:None,'bj_UNIT_FACING':270,'GS2V84_CreateNUnitsAtLoc_3':lambda *x:calls.append(('create',x[1])),'UnitApplyTimedLifeBJ':lambda duration,buff,u:calls.append(('life',duration)),'GetLastCreatedUnit':lambda:dummy,'UnitAddAbilityBJ':lambda *x:None,'SetUnitAbilityLevelSwapped':rank,'GetUnitAbilityLevelSwapped':lambda a,u:level,'GetSpellAbilityId':lambda:fourcc('A0CP'),'GetPlayerTechCountSimple':lambda tech,p:trait,'IssueImmediateOrderBJ':order}
  compile_jass(new,'Trig_Flame_Burst_Actions',ns);ns['Trig_Flame_Burst_Actions']()
  r=level+4*trait;assert dummy['rank']==r
  assert calls==[('create',fourcc('h00W')),('life',3.0),('rank',r),('order','thunderclap')]
  assert abs(ability['Htc1'+str(r)]-(40*level+100*trait))<.001
  assert abs(ability['Htc3'+str(r)]-(.10+.05*level+.50*trait))<.001
  assert ability['adur'+str(r)]==ability['ahdu'+str(r)]==1.5
  print('PASS: skill level',level,'trait',trait,'dummy rank',r,'cost 0/radius 300; damage and slow preserved')
# All other object fields and all unit/item/upgrade data remain unchanged.
for f in ['war3map.w3a','war3mapSkin.w3a']:
 x=load_objects(a,f);y=load_objects(b,f)
 for id in x:
  if id!='A0CV':assert x[id]==y[id],(f,id)
for f in ['war3map.w3u','war3mapSkin.w3u','war3map.w3t','war3mapSkin.w3t','war3map.w3q','war3mapSkin.w3q','war3map.wts']:assert a.read(f)==b.read(f),f
print('PASS: other abilities, units, items, upgrades, tooltips, ranger and recipe/purchase runtime preserved')
