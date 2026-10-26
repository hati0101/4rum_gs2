"""Run production passive logic with no attack API and no udg_HeroPlayer in scope."""
from pathlib import Path
import sys,math,collections,re
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];sys.path.insert(0,str(ROOT/'tools'))
from w3x import Archive
exec((ROOT/'reviews/ver146/test_sanctuary.py').read_text().split('class Handle:')[0])
s=Archive(str(ROOT/'maps/release/GS2vF_ver195-14.w3x')).read('war3map.j').decode()
class Unit:
 def __init__(self,owner=1,level=0,trait=0,x=0,mana=100,**kw):
  self.owner=owner;self.trait=trait;self.x=x;self.y=0;self.mana=mana;self.life=100;self.type=fourcc('Odrt') if level>=0 else 1;self.abilities={fourcc('ANic'):max(0,level)};self.illusion=False;self.structure=False;self.mechanical=False;self.immune=False;self.invulnerable=False;self.dead=False;self.__dict__.update(kw)
def setup(units):
 ns={'GS19514_BurnSources':[],'GS19514_BurnTargets':[],'GS19514_BurnPulses':0,'GS19514_BurnStatus':{},'UNIT_TYPE_DEAD':'dead','UNIT_TYPE_STRUCTURE':'structure','UNIT_TYPE_MECHANICAL':'mechanical','UNIT_TYPE_MAGIC_IMMUNE':'immune','UNIT_STATE_MANA':'mana'}
 def enum(g,x,y,r,f):g[:]=[u for u in units if math.hypot(u.x-x,u.y-y)<=r]
 def add(g,u):
  if u not in g:g.append(u)
 ns.update(GetUnitTypeId=lambda u:u.type if u else 0,IsUnitIllusion=lambda u:u.illusion,GetUnitAbilityLevel=lambda u,a:u.abilities.get(a,0),GetPlayerTechCount=lambda p,t,b:next((u.trait for u in units if u.owner==p and u.type==fourcc('Odrt')),0),GetOwningPlayer=lambda u:u.owner,UnitRemoveAbility=lambda u,a:u.abilities.pop(a,None),UnitAddAbility=lambda u,a:u.abilities.__setitem__(a,1),SetUnitAbilityLevel=lambda u,a,l:u.abilities.__setitem__(a,l),GroupAddUnit=add,GroupRemoveUnit=lambda g,u:g.remove(u),BlzGroupGetSize=len,BlzGroupUnitAt=lambda g,i:g[i],GetWidgetLife=lambda u:u.life,IsUnitType=lambda u,t:getattr(u,t),GetPlayerId=lambda p:p,GetUnitX=lambda u:u.x,GetUnitY=lambda u:u.y,GroupEnumUnitsInRange=enum,FirstOfGroup=lambda g:g[0] if g else None,IsUnitEnemy=lambda t,p:t.owner!=p,BlzIsUnitInvulnerable=lambda u:u.invulnerable,GetUnitState=lambda u,s:getattr(u,s),SetUnitState=lambda u,s,v:setattr(u,s,v),RMaxBJ=max,I2R=float,I2S=str,R2S=lambda x:f'{x:.2f}')
 for name in ['GS19514_IsFlameBlader','GS19514_BurnSync','GS19514_BurnTrack','GS19514_BurnTick']:compile_jass(s,name,ns)
 return ns
for level in range(1,5):
 source=Unit(level=level,trait=1);enemy=Unit(owner=2,level=-1,x=100,mana=100);ns=setup([source,enemy]);ns['GS19514_BurnTrack'](source)
 for _ in range(5):ns['GS19514_BurnTick']()
 assert enemy.mana==100-5*(2+2*level)
 assert source.abilities[fourcc('A11Q')]==level+1
 assert source.abilities[fourcc('A0UG')]==level
 assert not ns['GS19514_BurnTargets']
 print('PASS: idle E level',level,'drains',2+2*level,'per tick; no attack/native damage callback and no player-hero array in namespace')
# Exact boundary and old target eligibility remain intact.
source=Unit(level=4,trait=1);edge=Unit(owner=2,level=-1,x=250);outside=Unit(owner=2,level=-1,x=250.01)
excluded=[Unit(owner=2,level=-1,x=1,**flag) for flag in [{'dead':True,'life':0},{'structure':True},{'mechanical':True},{'immune':True},{'invulnerable':True}]]+[Unit(owner=1,level=-1,x=1)]
ns=setup([source,edge,outside]+excluded);ns['GS19514_BurnTrack'](source);ns['GS19514_BurnTick']()
assert edge.mana==90 and outside.mana==100 and all(u.mana==100 for u in excluded)
print('PASS: 250 boundary, enemy/living/organic/immunity filters and no friendly drain')
# Trait order, E unlearned, insufficient mana, death/revival, changed ownership and removed unit cleanup.
source=Unit(level=0,trait=1);target=Unit(owner=2,level=-1,x=100,mana=2);ns=setup([source,target]);ns['GS19514_BurnTrack'](source);ns['GS19514_BurnTick']();assert target.mana==2
source.abilities[fourcc('ANic')]=1;ns['GS19514_BurnTrack'](source);ns['GS19514_BurnTick']();assert target.mana==0 and source.abilities[fourcc('A11Q')]==2
source.trait=0;target.mana=100;ns['GS19514_BurnTick']();assert target.mana==100 and source.abilities[fourcc('A11Q')]==1 and fourcc('A0UG') not in source.abilities
source.trait=1;source.life=0;ns['GS19514_BurnTick']();assert target.mana==100
source.life=100;ns['GS19514_BurnTick']();assert target.mana==96
source.illusion=True;ns['GS19514_BurnTick']();assert not ns['GS19514_BurnSources']
source.illusion=False;ns['GS19514_BurnTrack'](source);source.type=0;ns['GS19514_BurnTick']();assert not ns['GS19514_BurnSources']
print('PASS: research before E, low-mana floor, trait loss/base resistance, death/revival, illusion and removed-unit cleanup')
# Prove registration does not depend on the old global caster or any attack.
source=Unit(level=2,trait=1);ns=setup([source]);ns.update(CreateGroup=lambda:[],GetTriggerUnit=lambda:source,GroupEnumUnitsOfPlayer=lambda g,p,f:g.extend([source]),DestroyGroup=lambda g:g.clear())
compile_jass(s,'GS19514_BurnResearch',ns);ns['GS19514_BurnResearch']();assert ns['GS19514_BurnSources']==[source]
print('PASS: research discovers actual owned hero without udg_Hero_FlB or udg_HeroPlayer')
# Structural proof: exactly one owned timer, no old timer remains, W and every unrelated function/object preserved.
old=Archive(str(ROOT/'maps/release/GS2vF_ver195-13.w3x'));new=Archive(str(ROOT/'maps/release/GS2vF_ver195-14.w3x'))
funcs=lambda text:{m[1]:m[0] for m in re.finditer(r'^function (\w+) takes .*?^endfunction',text,re.M|re.S)}
a=funcs(old.read('war3map.j').decode());b=funcs(s)
for name in a:
 if name not in ['GS294_Init','GS294_BurnTick','Trig_FlB_Special_1_Actions']:assert a[name].replace('195-13','195-14')==b[name],name
assert 'CreateTimer' not in b['GS294_Init'] and 'udg_HeroPlayer' not in b['GS19514_BurnTick'] and 'GetAttacker' not in b['GS19514_BurnTick']
for f in ['war3map.w3a','war3mapSkin.w3a','war3map.w3u','war3mapSkin.w3u','war3map.w3q','war3mapSkin.w3q','war3map.w3t','war3mapSkin.w3t','war3map.wts']:assert old.read(f)==new.read(f),f
print('PASS: one replacement passive timer; W/other skills/item/recipe/trait/resource objects untouched')
# Both main and the editor initializer may request initialization; allocate one periodic clock.
source=Unit(level=3,trait=1);ns=setup([source]);timers=[];groups=[];starts=[];clears=[]
def group():
 g=[];groups.append(g);return g
def timer():
 t=object();timers.append(t);return t
ns.update(GS19514_BurnStarted=False,GS19514_BurnClock=None,CreateGroup=group,CreateTimer=timer,CreateTrigger=lambda:object(),CreateRegion=lambda:object(),RegionAddRect=lambda *x:None,TriggerRegisterEnterRegion=lambda *x:None,TriggerAddAction=lambda *x:None,TriggerRegisterAnyUnitEventBJ=lambda *x:None,TriggerRegisterPlayerChatEvent=lambda *x:None,Player=lambda i:i,TimerStart=lambda *x:starts.append(x),bj_mapInitialPlayableArea=object(),EVENT_PLAYER_HERO_SKILL=1,EVENT_PLAYER_HERO_REVIVE_FINISH=2,EVENT_PLAYER_UNIT_SELL=3,GetExpiredTimer=lambda:timers[-1],DestroyTimer=lambda t:clears.append(t),GroupEnumUnitsInRect=lambda g,r,f:g.extend([source]),DestroyGroup=lambda g:g.clear(),gg_trg_FlB_Special_1=None)
ss=re.sub(r'\bfunction (\w+)(?=[,)])',r'\1',s)
for name in ['GS19514_BurnEnter','GS19514_BurnHeroEvent','GS19514_BurnSold','GS19514_BurnResearch','GS19514_BurnChat','GS19514_BurnBootstrap','GS19514_BurnInit']:compile_jass(ss,name,ns)
ns['GS19514_BurnInit']();ns['GS19514_BurnInit']();assert len(groups)==2 and len(timers)==2
assert [(x[1],x[2]) for x in starts]==[(1.0,True),(0.0,False)]
ns['GS19514_BurnBootstrap']();assert ns['GS19514_BurnSources']==[source] and len(clears)==1
print('PASS: duplicate initialization creates exactly one 1-second clock and one destroyed startup timer; pre-existing hero seeded without attacking')
print('LIMIT: stationary aura logic is mocked; actual engine registration, mana regeneration and multiplayer need in-game validation')
