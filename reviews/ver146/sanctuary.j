function GS146_Expire takes nothing returns nothing
    local timer t = GetExpiredTimer()
    local integer key = GetHandleId(t)
    local group g = LoadGroupHandle(GS146_Data,key,0)
    local unit u = FirstOfGroup(g)
    local integer uid
    local integer count
    loop
        exitwhen u == null
        call GroupRemoveUnit(g,u)
        set uid = GetHandleId(u)
        set count = LoadInteger(GS146_Data,uid,1)-1
        if count <= 0 then
            call UnitRemoveAbility(u,'IV46')
            call RemoveSavedInteger(GS146_Data,uid,1)
        else
            call SaveInteger(GS146_Data,uid,1,count)
        endif
        set u = FirstOfGroup(g)
    endloop
    call DestroyGroup(g)
    call FlushChildHashtable(GS146_Data,key)
    call DestroyTimer(t)
    set u = null
    set g = null
    set t = null
endfunction
function GS146_Protect takes unit caster, integer level returns nothing
    local group scan = CreateGroup()
    local group protected = CreateGroup()
    local timer t = CreateTimer()
    local unit u
    local integer uid
    if GS146_Data == null then
        set GS146_Data = InitHashtable()
    endif
    call GroupEnumUnitsInRange(scan,GetUnitX(caster),GetUnitY(caster),800.00,null)
    set u = FirstOfGroup(scan)
    loop
        exitwhen u == null
        call GroupRemoveUnit(scan,u)
        if IsUnitAlly(u,GetOwningPlayer(caster)) and GetWidgetLife(u) > 0.405 and not IsUnitType(u,UNIT_TYPE_MECHANICAL) and not IsUnitType(u,UNIT_TYPE_STRUCTURE) then
            set uid = GetHandleId(u)
            call UnitAddAbility(u,'IV46')
            call UnitMakeAbilityPermanent(u,true,'IV46')
            call SaveInteger(GS146_Data,uid,1,LoadInteger(GS146_Data,uid,1)+1)
            call GroupAddUnit(protected,u)
        endif
        set u = FirstOfGroup(scan)
    endloop
    call DestroyGroup(scan)
    call SaveGroupHandle(GS146_Data,GetHandleId(t),0,protected)
    call TimerStart(t,I2R(level+1),false,function GS146_Expire)
    set u = null
    set scan = null
    set protected = null
    set t = null
endfunction
