function GS19514_IsFlameBlader takes unit u returns boolean
    return u != null and GetUnitTypeId(u) == 'Odrt' and not IsUnitIllusion(u)
endfunction
function GS19514_BurnSync takes unit u returns integer
    local integer level = GetUnitAbilityLevel(u,'ANic')
    local integer resist = level
    local boolean learned = GetPlayerTechCount(GetOwningPlayer(u),'R04B',true) > 0
    if level < 1 or level > 4 then
        call UnitRemoveAbility(u,'A0UG')
        call UnitRemoveAbility(u,'A11Q')
        return 0
    endif
    if learned then
        set resist = level+1
    endif
    if GetUnitAbilityLevel(u,'A11Q') == 0 then
        call UnitAddAbility(u,'A11Q')
    endif
    if GetUnitAbilityLevel(u,'A11Q') != resist then
        call SetUnitAbilityLevel(u,'A11Q',resist)
    endif
    if learned then
        if GetUnitAbilityLevel(u,'A0UG') == 0 then
            call UnitAddAbility(u,'A0UG')
        endif
        if GetUnitAbilityLevel(u,'A0UG') != level then
            call SetUnitAbilityLevel(u,'A0UG',level)
        endif
        return level
    endif
    call UnitRemoveAbility(u,'A0UG')
    return 0
endfunction
function GS19514_BurnTrack takes unit u returns nothing
    if GS19514_BurnSources != null and GS19514_IsFlameBlader(u) then
        call GroupAddUnit(GS19514_BurnSources,u)
        call GS19514_BurnSync(u)
    endif
endfunction
function GS19514_BurnEnter takes nothing returns nothing
    call GS19514_BurnTrack(GetEnteringUnit())
endfunction
function GS19514_BurnHeroEvent takes nothing returns nothing
    call GS19514_BurnTrack(GetTriggerUnit())
endfunction
function GS19514_BurnSold takes nothing returns nothing
    call GS19514_BurnTrack(GetSoldUnit())
endfunction
function GS19514_BurnResearch takes nothing returns nothing
    local group scan = CreateGroup()
    local player owner = GetOwningPlayer(GetTriggerUnit())
    local unit u
    call GroupEnumUnitsOfPlayer(scan,owner,null)
    set u = FirstOfGroup(scan)
    loop
        exitwhen u == null
        call GroupRemoveUnit(scan,u)
        call GS19514_BurnTrack(u)
        set u = FirstOfGroup(scan)
    endloop
    call DestroyGroup(scan)
    set scan = null
    set owner = null
    set u = null
endfunction
function GS19514_BurnTick takes nothing returns nothing
    local integer i = BlzGroupGetSize(GS19514_BurnSources)-1
    local integer level
    local integer pid
    local integer hits
    local unit source
    local unit target
    local real before
    local real remaining
    local real drained
    set GS19514_BurnPulses = GS19514_BurnPulses+1
    loop
        exitwhen i < 0
        set source = BlzGroupUnitAt(GS19514_BurnSources,i)
        if not GS19514_IsFlameBlader(source) then
            call GroupRemoveUnit(GS19514_BurnSources,source)
        elseif GetWidgetLife(source) > 0.405 and not IsUnitType(source,UNIT_TYPE_DEAD) then
            set level = GS19514_BurnSync(source)
            set pid = GetPlayerId(GetOwningPlayer(source))
            set hits = 0
            set drained = 0.0
            if level >= 1 and level <= 4 then
                call GroupEnumUnitsInRange(GS19514_BurnTargets,GetUnitX(source),GetUnitY(source),250.0,null)
                set target = FirstOfGroup(GS19514_BurnTargets)
                loop
                    exitwhen target == null
                    call GroupRemoveUnit(GS19514_BurnTargets,target)
                    if IsUnitEnemy(target,GetOwningPlayer(source)) and GetWidgetLife(target) > 0.405 and not IsUnitType(target,UNIT_TYPE_STRUCTURE) and not IsUnitType(target,UNIT_TYPE_MECHANICAL) and not IsUnitType(target,UNIT_TYPE_MAGIC_IMMUNE) and not BlzIsUnitInvulnerable(target) then
                        set before = GetUnitState(target,UNIT_STATE_MANA)
                        set remaining = RMaxBJ(0.0,before-(2.0+2.0*I2R(level)))
                        call SetUnitState(target,UNIT_STATE_MANA,remaining)
                        set drained = drained+before-remaining
                        set hits = hits+1
                    endif
                    set target = FirstOfGroup(GS19514_BurnTargets)
                endloop
            endif
            set GS19514_BurnStatus[pid] = "[업화 진단] 주기="+I2S(GS19514_BurnPulses)+" E="+I2S(GetUnitAbilityLevel(source,'ANic'))+" 특성="+I2S(GetPlayerTechCount(GetOwningPlayer(source),'R04B',true))+" 활성="+I2S(level)+" 주변대상="+I2S(hits)+" 최근차감합="+R2S(drained)
        endif
        set i = i-1
    endloop
    set source = null
    set target = null
endfunction
function GS19514_BurnChat takes nothing returns nothing
    local player p = GetTriggerPlayer()
    local string status = GS19514_BurnStatus[GetPlayerId(p)]
    if status == null or status == "" then
        call DisplayTimedTextToPlayer(p,0,0,20,"[업화 진단] 주기="+I2S(GS19514_BurnPulses)+" 추적투마="+I2S(BlzGroupGetSize(GS19514_BurnSources))+" 본인 기록 없음")
    else
        call DisplayTimedTextToPlayer(p,0,0,20,"현재주기="+I2S(GS19514_BurnPulses)+" "+status)
    endif
    set p = null
endfunction
function GS19514_BurnBootstrap takes nothing returns nothing
    local group scan = CreateGroup()
    local unit u
    call DestroyTimer(GetExpiredTimer())
    call GroupEnumUnitsInRect(scan,bj_mapInitialPlayableArea,null)
    set u = FirstOfGroup(scan)
    loop
        exitwhen u == null
        call GroupRemoveUnit(scan,u)
        call GS19514_BurnTrack(u)
        set u = FirstOfGroup(scan)
    endloop
    call DestroyGroup(scan)
    if gg_trg_FlB_Special_1 != null then
        call TriggerClearActions(gg_trg_FlB_Special_1)
        call TriggerAddAction(gg_trg_FlB_Special_1,function GS19514_BurnResearch)
    endif
    set scan = null
    set u = null
endfunction
function GS19514_BurnInit takes nothing returns nothing
    local trigger enter
    local trigger hero
    local trigger sold
    local trigger chat
    local region area
    local integer i = 0
    if GS19514_BurnStarted then
        return
    endif
    set GS19514_BurnStarted = true
    set GS19514_BurnSources = CreateGroup()
    set GS19514_BurnTargets = CreateGroup()
    set GS19514_BurnClock = CreateTimer()
    set enter = CreateTrigger()
    set area = CreateRegion()
    call RegionAddRect(area,bj_mapInitialPlayableArea)
    call TriggerRegisterEnterRegion(enter,area,null)
    call TriggerAddAction(enter,function GS19514_BurnEnter)
    set hero = CreateTrigger()
    call TriggerRegisterAnyUnitEventBJ(hero,EVENT_PLAYER_HERO_SKILL)
    call TriggerRegisterAnyUnitEventBJ(hero,EVENT_PLAYER_HERO_REVIVE_FINISH)
    call TriggerAddAction(hero,function GS19514_BurnHeroEvent)
    set sold = CreateTrigger()
    call TriggerRegisterAnyUnitEventBJ(sold,EVENT_PLAYER_UNIT_SELL)
    call TriggerAddAction(sold,function GS19514_BurnSold)
    set chat = CreateTrigger()
    loop
        exitwhen i >= 12
        call TriggerRegisterPlayerChatEvent(chat,Player(i),"-업화진단",true)
        set i = i+1
    endloop
    call TriggerAddAction(chat,function GS19514_BurnChat)
    call TimerStart(GS19514_BurnClock,1.0,true,function GS19514_BurnTick)
    call TimerStart(CreateTimer(),0.0,false,function GS19514_BurnBootstrap)
    set enter = null
    set hero = null
    set sold = null
    set chat = null
    set area = null
endfunction
