from pathlib import Path
import re
HERE=Path(__file__).resolve().parent
GLOBALS='''    boolean array GS1969_HintLizard
    boolean array GS1969_HintPanda
    boolean array GS1969_HintWolf
    group GS1969_WTargets = null
    integer GS1969_TraitSelected = 0
    integer GS1969_TraitImmediate = 0
    integer GS1969_TraitDeferred = 0
    boolean GS1969_InitDone = false
'''
def fn(s,n):
 m=re.search(r'^function '+re.escape(n)+r' takes .*?^endfunction',s,re.M|re.S)
 return m.group() if m else None
def body(s,n,b):
 old=fn(s,n)
 if old is None:return s
 return s.replace(old,old.split('\n',1)[0]+'\n'+b.rstrip()+'\nendfunction',1)
def patch(s):
 s=s.replace('196-8','196-9')
 s=s.replace('        call BlzTriggerRegisterPlayerKeyEvent(key,Player(i),OSKEY_OEM_3,0,false)\n','')
 n='ESC_IconClick';old=fn(s,n)
 if old:
  new=old.replace('        set E1964_SelectPending=true','''        if IsUnitSelected(E1966_Controller[GetPlayerId(GetTriggerPlayer())+1],GetTriggerPlayer()) then
            set GS1969_TraitImmediate=GS1969_TraitImmediate+1
        endif
        set E1964_SelectPending=true''')
  s=s.replace(old,new,1)
 s=body(s,'E1964_Refresh','''    local framehandle button
    local player p=GetLocalPlayer()
    if E1964_SelectPending then
        set E1964_SelectPending=false
        // Release native button focus after its own click processing has completed.
        set button=BlzGetFrameByName("IdleWorkerButton",0)
        if button!=null and GetUnitTypeId(udg_HeroPlayer[GetPlayerId(p)+1])=='HE15' then
            call BlzFrameSetEnable(button,false)
            call BlzFrameSetEnable(button,true)
        endif
        call ESUI_SelectTraits(p)
        if IsUnitSelected(E1966_Controller[GetPlayerId(p)+1],p) then
            set GS1969_TraitDeferred=GS1969_TraitDeferred+1
        endif
    endif
    set button=null
    set p=null''')
 old=fn(s,'E1968_TraitDiagnostic')
 if old:
  s=s.replace(old,old.replace('    set h=null','''    call DisplayTimedTextToPlayer(p,0,0,30,"[특성 선택 추적] 즉시성공="+I2S(GS1969_TraitImmediate)+" / 지연성공="+I2S(GS1969_TraitDeferred)+" / 실제선택이벤트="+I2S(GS1969_TraitSelected)+" / 선택대기="+ETW_ProbeBool(E1964_SelectPending))
    set h=null'''),1)
 old=fn(s,'ES15_Tick')
 if old:
  s=s.replace(old,old.replace('set g=CreateGroup()','set g=GS1969_WTargets').replace('call DestroyGroup(g)','call GroupClear(g)'),1)
 old=fn(s,'GSRI_Range')
 if old:
  s=s.replace(old,old.replace('    if GSRI_Item==null', '''    if GSRI_Item==null and GetUnitTypeId(u)=='N01L' and (id=='A13E' or id=='A022') then
        return 500.0
    endif
    if GSRI_Item==null''',1),1)
 old=fn(s,'Trig_random_Actions')
 if old:
  needle='set udg_RandHero[RandHero] = true'
  assert needle in old
  s=s.replace(old,old.replace(needle,'call GS1969_HiddenHint(udg_HeroPlayer[GetConvertedPlayerId(RandPlayer)])\n'+needle,1),1)
 s=body(s,'Trig_FireDrunk_Actions','    call GS1969_FireDrunk()')
 old=fn(s,'ES15_Init')
 if old:
  needle='    call ES16_Init()';assert needle in old
  s=s.replace(old,old.replace(needle,needle+'\n    call GS1969_Init()',1),1)
 return s
