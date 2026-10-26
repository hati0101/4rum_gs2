function GS19513_Flag takes boolean flag returns string
    if flag then
        return "1"
    endif
    return "0"
endfunction
function GS19513_FlameBurstAction takes nothing returns nothing
    local unit caster = GetTriggerUnit()
    local player owner = GetOwningPlayer(caster)
    local integer pid = GetPlayerId(owner)
    local integer level = GetUnitAbilityLevel(caster,'A0CP')
    local integer trait = GetPlayerTechCount(owner,'R048',true)
    local integer rank = level
    local integer actual = 0
    local real x = GetUnitX(caster)
    local real y = GetUnitY(caster)
    local real damage = 0.0
    local real radius = 0.0
    local real slow = 0.0
    local unit dummy = null
    local ability payload = null
    local boolean added = false
    local boolean ordered = false
    if level >= 1 and level <= 4 then
        if trait > 0 then
            set rank = level+4
        endif
        // Preserve the existing explosion visual, without asking its model to cast.
        call GS2V84_CreateNUnitsAtLoc_3(1,'h00W',owner,Location(x,y),bj_UNIT_FACING)
        call UnitApplyTimedLife(GetLastCreatedUnit(),'BTLF',3.00)
        // 1.07/1.5005 used ewsp as the actual A0CV caster as well.
        set dummy = CreateUnit(owner,'ewsp',x,y,bj_UNIT_FACING)
        if dummy != null then
            call UnitApplyTimedLife(dummy,'BTLF',3.00)
            call UnitAddAbility(dummy,'Aloc')
            call BlzSetUnitRealField(dummy,UNIT_RF_CAST_POINT,0.0)
            call BlzSetUnitRealField(dummy,UNIT_RF_CAST_BACK_SWING,0.0)
            call SetUnitState(dummy,UNIT_STATE_MANA,GetUnitState(dummy,UNIT_STATE_MAX_MANA))
            set added = UnitAddAbility(dummy,'A0CV')
            if added then
                call SetUnitAbilityLevel(dummy,'A0CV',rank)
                set actual = GetUnitAbilityLevel(dummy,'A0CV')
                set payload = BlzGetUnitAbility(dummy,'A0CV')
                if actual == rank and payload != null then
                    set damage = BlzGetAbilityRealLevelField(payload,ABILITY_RLF_AOE_DAMAGE,actual-1)
                    set radius = BlzGetAbilityRealLevelField(payload,ABILITY_RLF_AREA_OF_EFFECT,actual-1)
                    set slow = BlzGetAbilityRealLevelField(payload,ABILITY_RLF_MOVEMENT_SPEED_REDUCTION_PERCENT_HTC3,actual-1)
                    call BlzEndUnitAbilityCooldown(dummy,'A0CV')
                    set ordered = IssueImmediateOrderById(dummy,852096)
                endif
            endif
        endif
        set GS19513_FlameBurstStatus[pid] = "[투마 W 진단] 스킬="+I2S(level)+" 특성="+I2S(trait)+" 내부="+I2S(actual)+"/"+I2S(rank)+" 부여="+GS19513_Flag(added)+" 명령접수="+GS19513_Flag(ordered)+" 피해설정="+R2S(damage)+" 범위="+R2S(radius)+" 감속설정="+R2S(slow)
    else
        set GS19513_FlameBurstStatus[pid] = "[투마 W 진단] 잘못된 시전자/스킬 레벨: "+I2S(level)
    endif
    set payload = null
    set dummy = null
    set caster = null
    set owner = null
endfunction

function GS19513_FlameBurstChat takes nothing returns nothing
    local player p = GetTriggerPlayer()
    local string status = GS19513_FlameBurstStatus[GetPlayerId(p)]
    if not GS19513_FlameBurstInstalled then
        call DisplayTimedTextToPlayer(p,0,0,20,"[투마 W 진단] 발동 처리 설치가 확인되지 않았습니다.")
    elseif status == null or status == "" then
        call DisplayTimedTextToPlayer(p,0,0,15,"[투마 W 진단] 아직 시전 기록이 없습니다.")
    else
        call DisplayTimedTextToPlayer(p,0,0,20,status)
    endif
    set p = null
endfunction
function GS19513_FlameBurstInstall takes nothing returns nothing
    call DestroyTimer(GetExpiredTimer())
    if gg_trg_Flame_Burst != null then
        call TriggerClearActions(gg_trg_Flame_Burst)
        call TriggerAddAction(gg_trg_Flame_Burst,function GS19513_FlameBurstAction)
        set GS19513_FlameBurstInstalled = true
    endif
endfunction
function GS19513_FlameBurstInit takes nothing returns nothing
    local trigger t
    local integer i = 0
    if GS19513_FlameBurstStarted then
        return
    endif
    set GS19513_FlameBurstStarted = true
    set t = CreateTrigger()
    loop
        exitwhen i >= 12
        call TriggerRegisterPlayerChatEvent(t,Player(i),"-투마진단",true)
        set i = i+1
    endloop
    call TriggerAddAction(t,function GS19513_FlameBurstChat)
    call TimerStart(CreateTimer(),0.0,false,function GS19513_FlameBurstInstall)
    set t = null
endfunction
function Trig_Flame_Burst_Actions takes nothing returns nothing
    call GS19513_FlameBurstAction()
endfunction
