function GS1969_HiddenHint takes unit h returns nothing
    local player p=GetOwningPlayer(h)
    local integer pid=GetPlayerId(p)
    local integer id=GetUnitTypeId(h)
    local string text=""
    if pid<0 or pid>=12 or IsUnitIllusion(h) then
        set p=null
        return
    endif
    if id=='Ofar' and not GS1969_HintLizard[pid] then
        set GS1969_HintLizard[pid]=true
        set text="이 영웅은 숨겨진 변신이 있습니다. 조건은 F9에서 확인하세요."
    elseif id=='Npbm' and not GS1969_HintPanda[pid] then
        set GS1969_HintPanda[pid]=true
        set text="이 영웅은 두 가지 숨겨진 변신이 있습니다. 조건은 F9에서 확인하세요."
    elseif id=='Hdgo' and not GS1969_HintWolf[pid] then
        set GS1969_HintWolf[pid]=true
        set text="이 영웅은 숨겨진 변신이 있습니다. 조건은 F9에서 확인하세요."
    endif
    if text!="" then
        call DisplayTimedTextToPlayer(p,0,0,15,text)
    endif
    set p=null
endfunction
function GS1969_HintSold takes nothing returns nothing
    call GS1969_HiddenHint(GetSoldUnit())
endfunction
function GS1969_SelectionWatch takes nothing returns nothing
    local player p=GetTriggerPlayer()
    local unit c=E1966_Controller[GetPlayerId(p)+1]
    if p==GetLocalPlayer() and GetTriggerUnit()==c then
        set GS1969_TraitSelected=GS1969_TraitSelected+1
    endif
    set p=null
    set c=null
endfunction
function GS1969_FireDrunk takes nothing returns nothing
    local unit caster=GetTriggerUnit()
    local real x=GetUnitX(caster)
    local real y=GetUnitY(caster)
    local real tx=GetSpellTargetX()
    local real ty=GetSpellTargetY()
    local real dx=tx-x
    local real dy=ty-y
    local real distance=SquareRoot(dx*dx+dy*dy)
    local unit dummy
    // The payload keeps its original 500 cast range and 550 effect length.
    // Clamp only the dummy's aim point, not its damage/effect dimensions.
    if distance>500.0 then
        set tx=x+dx*500.0/distance
        set ty=y+dy*500.0/distance
    endif
    set dummy=CreateUnit(GetOwningPlayer(caster),'e02N',x,y,Atan2(dy,dx)*bj_RADTODEG)
    set bj_lastCreatedUnit=dummy
    call UnitApplyTimedLife(dummy,'BTLF',0.50)
    call SetUnitAbilityLevel(dummy,'A13J',GetUnitAbilityLevel(caster,'A022'))
    call IssuePointOrder(dummy,"breathoffrost",tx,ty)
    set caster=null
    set dummy=null
endfunction
function GS1969_Init takes nothing returns nothing
    local trigger selected
    local integer i=0
    if GS1969_InitDone then
        return
    endif
    set GS1969_InitDone=true
    set GS1969_WTargets=CreateGroup()
    // Also installs the action after GUI initialization on an editor rebuild.
    call TriggerClearActions(gg_trg_FireDrunk)
    call TriggerAddAction(gg_trg_FireDrunk,function GS1969_FireDrunk)
    set selected=CreateTrigger()
    loop
        exitwhen i>=12
        call TriggerRegisterPlayerUnitEvent(selected,Player(i),EVENT_PLAYER_UNIT_SELECTED,null)
        set i=i+1
    endloop
    call TriggerAddAction(selected,function GS1969_SelectionWatch)
    call TriggerAddAction(gg_trg_Select_Hero,function GS1969_HintSold)
    set selected=null
endfunction
