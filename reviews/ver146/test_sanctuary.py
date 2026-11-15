from pathlib import Path
import re
def fourcc(s):return int.from_bytes(s.encode('ascii'),'big')
def expr(s):
 s=re.sub(r"'(.{4})'",lambda m:str(fourcc(m.group(1))),s)
 for a,b in [('null','None'),('true','True'),('false','False')]:s=re.sub(r'\b'+a+r'\b',b,s)
 return s

def fn(s,n):return re.search(r'^function '+n+r' takes .*?^endfunction',s,re.M|re.S).group()
def compile_jass(s,n,ns):
 text=fn(s,n);lines=text.splitlines()
 args=lines[0].split(' takes ')[1].split(' returns ')[0]
 args=[] if args=='nothing' else [p.strip().split()[-1] for p in args.split(',')]
 locals_=set(args)
 for line in lines[1:]:
  m=re.match(r'\s*local \w+ (\w+)',line)
  if m:locals_.add(m.group(1))
 assigned=set(re.findall(r'^\s*set (\w+)',text,re.M))-locals_
 out=['def '+n+'('+','.join(args)+'):']
 if assigned:out.append('    global '+','.join(sorted(assigned)))
 indent=1
 for raw in lines[1:-1]:
  line=raw.split('//')[0].strip()
  if not line:continue
  if line in ['endif','endloop']:indent-=1;continue
  if line.startswith('elseif '):
   indent-=1;out.append('    '*indent+'elif '+expr(line[7:-5])+':');indent+=1
  elif line=='else':
   indent-=1;out.append('    '*indent+'else:');indent+=1
  elif line.startswith('if '):
   out.append('    '*indent+'if '+expr(line[3:-5])+':');indent+=1
  elif line=='loop':out.append('    '*indent+'while True:');indent+=1
  elif line.startswith('exitwhen '):out.append('    '*indent+'if '+expr(line[9:])+': break')
  elif line.startswith('local '):
   m=re.match(r'local (\w+) (\w+)(?:\s*=\s*(.*))?',line)
   default={'integer':'0','real':'0.0','boolean':'False'}.get(m[1],'None')
   out.append('    '*indent+m[2]+' = '+expr(m[3] or default))
  elif line.startswith('set '):out.append('    '*indent+expr(line[4:]))
  elif line.startswith('call '):out.append('    '*indent+expr(line[5:]))
  elif line.startswith('return'):out.append('    '*indent+expr(line))
  else:raise AssertionError(line)
 exec('\n'.join(out),ns)

class Handle:
 counter=0
 def __init__(self,items=None):
  Handle.counter+=1;self.id=Handle.counter;self.items=list(items or []);self.dead=False
class Unit(Handle):
 def __init__(self,ally=True,mechanical=False,life=100):
  super().__init__();self.ally=ally;self.mechanical=mechanical;self.life=life;self.abilities={fourcc('Avul')}
ns={'GS146_Data':None,'UNIT_TYPE_MECHANICAL':1,'UNIT_TYPE_STRUCTURE':2}
units=[Unit(),Unit(),Unit(False),Unit(True,True),Unit(life=0)]
timers=[];expired=None
ns.update(InitHashtable=lambda:{},CreateGroup=lambda:Handle(),CreateTimer=lambda:timers.append(Handle()) or timers[-1],GetHandleId=lambda h:h.id,GetUnitX=lambda u:0,GetUnitY=lambda u:0,GetOwningPlayer=lambda u:0,GroupEnumUnitsInRange=lambda g,x,y,r,f:g.items.extend(units),FirstOfGroup=lambda g:g.items[0] if g.items else None,GroupRemoveUnit=lambda g,u:g.items.remove(u),IsUnitAlly=lambda u,p:u.ally,GetWidgetLife=lambda u:u.life,IsUnitType=lambda u,t:u.mechanical if t==1 else False,UnitAddAbility=lambda u,a:u.abilities.add(a),UnitMakeAbilityPermanent=lambda *args:None,GroupAddUnit=lambda g,u:g.items.append(u),DestroyGroup=lambda g:setattr(g,'dead',True),DestroyTimer=lambda t:setattr(t,'dead',True),I2R=float,TimerStart=lambda t,d,p,f:(setattr(t,'duration',d),setattr(t,'callback',f)),GetExpiredTimer=lambda:expired)
for kind in ['Integer','GroupHandle']:
 ns['Load'+kind]=lambda h,p,c:h.get((p,c),0)
 ns['Save'+kind]=lambda h,p,c,v:h.__setitem__((p,c),v)
ns['RemoveSavedInteger']=lambda h,p,c:h.pop((p,c),None)
ns['FlushChildHashtable']=lambda h,p:[h.pop(k) for k in list(h) if k[0]==p]
ns['UnitRemoveAbility']=lambda u,a:u.abilities.discard(a)
runtime=Path(__file__).with_name('sanctuary.j').read_text()
for name in ['GS146_Expire','GS146_Protect']:compile_jass(runtime.replace('function GS146_Expire)','GS146_Expire)'),name,ns)
for level in [1,2,3]:
 ns['GS146_Protect'](units[0],level);t=timers[-1];assert t.duration==level+1
 assert all((fourcc('IV46') in u.abilities)==(i<2) for i,u in enumerate(units))
 expired=t;g=ns['GS146_Data'][(t.id,0)];t.callback()
 assert t.dead and g.dead and not ns['GS146_Data']
 assert all(fourcc('IV46') not in u.abilities and fourcc('Avul') in u.abilities for u in units)
ns['GS146_Protect'](units[0],1);a=timers[-1]
ns['GS146_Protect'](units[0],3);b=timers[-1]
expired=a;a.callback();assert fourcc('IV46') in units[0].abilities
units[1].life=0
expired=b;b.callback();assert not ns['GS146_Data'] and all(fourcc('IV46') not in u.abilities for u in units)
print('PASS: 2/3/4 seconds, allied/organic/living filters, overlapping casts, death cleanup, pre-existing Avul retained, all groups/timers/storage freed (mocked natives only)')
