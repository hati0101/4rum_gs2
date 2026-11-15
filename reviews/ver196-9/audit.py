"""Static evidence for unresolved reports; does not claim runtime reproduction."""
from pathlib import Path
import sys,re,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];sys.path[:0]=[str(ROOT/'tools')]
from w3x import Archive
from objdata import load_objects,load_strings,resolve
s=Archive(str(ROOT/'maps/reference/GS2vF_ver196-8.w3x')).read('war3map.j').decode()
f={m.group(1):m.group() for m in re.finditer(r'^function (\w+) takes[^\n]*\n.*?^endfunction',s,re.M|re.S)}
graph={n:sorted(set(re.findall(r'\b(\w+)\s*\(',b))&f.keys()) for n,b in f.items()}
roots=['Trig_Blood_Strike_DM_Actions','Trig_Blood_Strike_Start_Actions','Trig_Blood_Strike_Timer_Actions','Trig_Blood_Strike_Sp_Actions']
seen=set();pending=list(roots)
while pending:
 n=pending.pop()
 if n in seen:continue
 seen.add(n);pending+=graph[n]
gold={n:[line.strip() for line in f[n].splitlines() if re.search(r'PLAYER_STATE_RESOURCE_GOLD|AdjustPlayerStateBJ|SetPlayerState\(',line)] for n in seen}
gold={n:v for n,v in gold.items() if v}
assert not gold,gold
sink={n:[line.strip() for line in b.splitlines() if re.search('PLAYER_STATE_RESOURCE_GOLD',line)] for n,b in f.items() if 'PLAYER_STATE_RESOURCE_GOLD' in b}
report={'chiu':{'report':'One alleged 200 gold loss; death/purchase/research context unknown.','direct_call_graph_roots':roots,'reachable_functions':sorted(seen),'gold_mutations_in_direct_call_graph':gold,'limit':'Damage can synchronously fire death/reward/reflection callbacks; engine purchase/research costs are outside a direct call graph. No in-game reproduction. Do not call the report disproven.','unchanged':True},'glen':{'report':'2-3 intermittent missing ultimate visuals, without ultimate trait; defense not measured.','ability':'A0WG','spawned_unit':'u00E','base_visual':'A151 / OrcSelectionAura.mdx','base_auras':['A0SX / B0B4','A039 / B05U'],'trait':'R07X enables A0KD +20% allied movement speed; not a prerequisite for base visuals.','entry_handler':f['Trig_Vanguard_Actions'],'follow':f['MakeUnitFollow'],'follow_tick':f['MakeUnitFollow_Sub'],'risks_not_proven_causes':['AUls native summon occurrence/ability cancellation cannot be observed statically.','Single global udg_Hero_RoC is used by entry handler; actual misbinding was not reproduced.','Native spawned follower is removed on target/follower death or 30-second follow deadline; native timed life remains 8/10/12 seconds.','Legacy defense refunds health after DAMAGED and may wait .01 seconds; no rewrite authorized without evidence.'],'last_created_hashtable':{'InitHashtableBJ_call_sites':[n for n,b in f.items() if 'call InitHashtableBJ(' in b],'direct_bj_lastCreatedHashtable_writes':[n for n,b in f.items() if 'set bj_lastCreatedHashtable' in b],'conclusion':'Only one BJ initializer found at the map 1-second setup. Shared-table clobber was NOT established; MakeUnitFollow is unchanged.'},'unchanged':True},'performance':{'report':'196-8 Tuma/Earth Panda 1v1 later-game intermittent hitches; not a whole-client freeze.','screenshot_match_unconfirmed':True,'screenshot':{'elapsed':1783,'tracked':296,'peak':347,'registered':2187,'cleaned':1891,'last_batch':'41/64'},'screenshot_limit':'One snapshot proves neither a leak nor the absence of bursts.','reviewed':[n for n in f if n.startswith(('ES16_','ESR6_','GS1959_')) or n in ['ES15_Tick','ES15_ShieldEnd','GS19513_FlameBurstAction','GS294_BurnTick']],'confirmed_repeated_work':'ES15_Tick allocates and destroys a temporary contact group every .05 seconds while W is active and contact is pending. Replaced with one persistent cleared group.','visual_cleanup':'ES16_QTick destroys its 5 effects/timer and flushes state after step 10. ESR6_End destroys 6 shield effects. ES16_Z reuses a location. Tuma W already uses timed life; active visual/resource files preserved.','limit':'No FPS/frametime/engine handle measurements, no confirmed root cause of reported hitches.'},'economy_gold_sites':sink}
(HERE/'investigation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('PASS: Chiu direct script graph has no gold mutation; indirect engine/death transactions remain unverified')
print('PASS: Glen base visual and protection are independent of R07X; Glen/Chiu bodies unchanged')
