"""Narrow script-only performance patch, preserving gameplay parameters and RNG order."""
import re
GLOBALS='''    string array GS1959_Text
    boolean array GS1959_TextValid
    real array GS1959_BarRatio
    real array GS1959_BarHeight
    boolean array GS1959_BarValid
    boolean GS1959_LayoutValid = false
    real GS1959_LayoutRight = 0.0
'''
HELPERS='''function GS1959_PickRandomOwned takes group g returns unit
    local boolean alreadyOwned = bj_wantDestroyGroup
    local unit result = GroupPickRandomUnit(g)
    if not alreadyOwned then
        call DestroyGroup(g)
    endif
    set g = null
    return result
endfunction
function GS1959_ResetUI takes nothing returns nothing
    local integer i = 0
    loop
        exitwhen i >= 40
        set GS1959_TextValid[i] = false
        set GS1959_BarValid[i] = false
        set i = i+1
    endloop
    set GS1959_LayoutValid = false
endfunction
'''
def functions(s):
 return {m[1]:m[0] for m in re.finditer(r'^function (\w+) takes .*?^endfunction',s,re.M|re.S)}
def args_at(s,start):
 depth=1;quoted=False;args=[];a=start+1;i=a
 while i<len(s):
  c=s[i]
  if c=='"' and (i==0 or s[i-1]!='\\'):quoted=not quoted
  if not quoted:
   if c=='(':depth+=1
   elif c==')':
    depth-=1
    if depth==0:return args+[s[a:i].strip()]
   elif c==',' and depth==1:args.append(s[a:i].strip());a=i+1
  i+=1
 raise ValueError('unterminated call')
# Consume only fresh, unshared locations; never consume a stored global/array location.
RULES={
 'CreateNUnitsAtLoc':(3,'GS2V84_CreateNUnitsAtLoc_3'),
 'CreateUnitAtLoc':(2,'GS2V84_CreateUnitAtLoc_2'),
 'IssuePointOrderByIdLoc':(2,'GS2V84_IssuePointOrderByIdLoc_2'),
 'GS2V84_DistanceBetweenPoints_0':(1,'GS2V84_DistanceBetweenPoints_01'),
 'GS2V84_AngleBetweenPoints_0':(1,'GS2V84_AngleBetweenPoints_01'),
}
def patch(s):
 s=s.replace('\r\n','\n');hits=[]
 for old,(index,new) in RULES.items():
  edits=[]
  for m in re.finditer(r'\b'+old+r'\s*\(',s):
   args=args_at(s,s.index('(',m.start()))
   if len(args)>index and re.match(r'^(GetUnitLoc|GetItemLoc|GetSpellTargetLoc|GetPlayerStartLocationLoc|GetRectCenter|Location)\s*\(',args[index]):edits.append((m.start(),m.start()+len(old)));hits.append((old,args[index]))
  for a,b in reversed(edits):s=s[:a]+new+s[b:]
 s=s.replace('IsUnitInGroup(GetTriggerUnit(), GetUnitsOfPlayerAll(Player(PLAYER_NEUTRAL_AGGRESSIVE))) == true','GetOwningPlayer(GetTriggerUnit()) == Player(PLAYER_NEUTRAL_AGGRESSIVE)')
 s=s.replace('GroupPickRandomUnit(GetUnitsOfPlayerAll(', 'GS1959_PickRandomOwned(GetUnitsOfPlayerAll(')
 f=functions(s)
 def change(name,transform):
  nonlocal s
  if name in f:s=s.replace(f[name],transform(f[name]))
 change('Trig_Change_Actions',lambda x:x.replace('endfunction','    call RemoveLocation(casterloc)\n    call RemoveLocation(targetloc)\n    set casterloc = null\n    set targetloc = null\n    set caster = null\n    set target = null\nendfunction'))
 change('Trig_AbW_Special_1_Actions',lambda x:x.replace('endfunction','    call RemoveLocation(Loc)\n    set Loc = null\nendfunction'))
 change('Trig_Dark_Summoning_Actions',lambda x:x.replace('endfunction','    set u = null\nendfunction'))
 # Both timer and hashtable must be released on the null-caster branch as well.
 change('GS181_RainProc',lambda x:x.replace('    if caster==null then','    call FlushChildHashtable(GS181_Rain,k)\n    call PauseTimer(t)\n    call DestroyTimer(t)\n    if caster==null then').replace('    endif\n    call FlushChildHashtable(GS181_Rain,k)\n    call PauseTimer(t)\n    call DestroyTimer(t)','    endif',1))
 change('GS181_FxEnd',lambda x:x.replace('    if e==null then\n        set t=null\n        return\n    endif\n',''))
 change('GS181_FlakExpire',lambda x:x.replace('    if source==null then','    if source==null then\n        call FlushChildHashtable(GS181_Flak,k)\n        call PauseTimer(t)\n        call DestroyTimer(t)'))
 change('GSTF_SetText',lambda x:'''function GSTF_SetText takes string name, integer i, string s returns nothing
    local integer key = i
    if name == "GSTF_SkCd" then
        set key = 20+i
    elseif name != "GSTF_Lvl" then
        call BlzFrameSetText(BlzGetFrameByName(name,i),"|cffffffff"+s+"|r")
        return
    endif
    if not GS1959_TextValid[key] or GS1959_Text[key] != s then
        if name == "GSTF_SkCd" and s == "" then
            call BlzFrameSetText(BlzGetFrameByName(name,i),"")
        else
            call BlzFrameSetText(BlzGetFrameByName(name,i),"|cffffffff"+s+"|r")
        endif
        set GS1959_Text[key] = s
        set GS1959_TextValid[key] = true
    endif
endfunction''')
 change('GSTF_FillSkill',lambda x:x.replace('    local string texture','    local string cooldownText = ""\n    local string texture').replace('    call BlzFrameSetText(BlzGetFrameByName("GSTF_SkCd", c), "")\n','').replace('call GSTF_SetText("GSTF_SkCd", c, I2S(R2I(cd) + 1))','set cooldownText = I2S(R2I(cd) + 1)').replace('    if s == 3 then','    call GSTF_SetText("GSTF_SkCd", c, cooldownText)\n    if s == 3 then'))
 change('GSTF_SetBar',lambda x:'''function GSTF_SetBar takes string name, integer i, real h, real ratio returns nothing
    local integer key = i
    local framehandle f
    if name == "GSTF_Mp" then
        set key = 5+i
    endif
    if ratio > 1.0 then
        set ratio = 1.0
    elseif ratio <= 0.001 then
        set ratio = 0.0
    endif
    if GS1959_BarValid[key] and GS1959_BarRatio[key] == ratio and GS1959_BarHeight[key] == h then
        return
    endif
    set f = BlzGetFrameByName(name,i)
    if ratio > 0.001 then
        call BlzFrameSetSize(f,GSTF_BarW()*ratio,h)
        call BlzFrameSetVisible(f,true)
    else
        call BlzFrameSetVisible(f,false)
    endif
    set GS1959_BarRatio[key] = ratio
    set GS1959_BarHeight[key] = h
    set GS1959_BarValid[key] = true
    set f = null
endfunction''')
 change('GSTF_Create',lambda x:x.replace('    call BlzFrameSetSize(root,','    call GS1959_ResetUI()\n    call BlzFrameSetSize(root,',1).replace('        call BlzFrameSetSize(slot,','        call BlzFrameSetPoint(slot,FRAMEPOINT_TOPRIGHT,root,FRAMEPOINT_TOPRIGHT,0.0,-i*(GSTF_H()+GSTF_Gap()))\n        call BlzFrameSetSize(slot,',1))
 change('GSTF_Update',lambda x:x.replace('    call BlzFrameClearAllPoints(root)\n    call BlzFrameSetAbsPoint(root, FRAMEPOINT_TOPRIGHT, right - 0.004, GSTF_Top())','    if not GS1959_LayoutValid or GS1959_LayoutRight != right then\n        call BlzFrameClearAllPoints(root)\n        call BlzFrameSetAbsPoint(root, FRAMEPOINT_TOPRIGHT, right - 0.004, GSTF_Top())\n        set GS1959_LayoutRight = right\n        set GS1959_LayoutValid = true\n    endif').replace('            call BlzFrameClearAllPoints(slot)\n','').replace('            call BlzFrameSetPoint(slot, FRAMEPOINT_TOPRIGHT, root, FRAMEPOINT_TOPRIGHT, 0.0, -k * (GSTF_H() + GSTF_Gap()))\n',''))
 return s.replace('195-8','195-9'),hits
