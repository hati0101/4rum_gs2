// GSRI: purely visual, local preview. No orders, damage or ability changes.
globals
    constant real GSRI_PERIOD = 0.015625
    constant real GSRI_TURN_BLEND = 0.30
    hashtable GSRI_Data = null
    constant integer GSRI_RING_LIMIT = 256
    constant integer GSRI_POOL_SIZE = 384
    lightning array GSRI_Effect
    boolean array GSRI_SegmentShown
    boolean array GSRI_SegmentValid
    real array GSRI_X1
    real array GSRI_Y1
    real array GSRI_X2
    real array GSRI_Y2
    integer GSRI_DrawIndex = 0
    integer GSRI_RingCount = 0
    integer GSRI_PathCount = 256
    real GSRI_OriginX = 0.00
    real GSRI_OriginY = 0.00
    real GSRI_Cos = 1.00
    real GSRI_Sin = 0.00
    location GSRI_Ground = null
    integer GSRI_Key = 0
    integer GSRI_LastAbility = 0
    real GSRI_MouseX = 0.00
    real GSRI_MouseY = 0.00
    boolean GSRI_MouseValid = false
    boolean GSRI_Started = false
    boolean GSRI_Visible = false
    unit GSRI_Caster = null
    real GSRI_Age = 0.00
    real GSRI_LastRange = 0.00
    real GSRI_Yaw = 0.00
    boolean GSRI_YawValid = false
    real GSRI_FindAge = 0.00
    integer GSRI_KeyCount = 0
    integer GSRI_ShowCount = 0
    string GSRI_Reason = "init"
endglobals

//@@GSRI_TABLE@@

function GSRI_HideSegment takes integer i returns nothing
    if GSRI_SegmentShown[i] then
        call SetLightningColor(GSRI_Effect[i],0,0,0,0)
        set GSRI_SegmentShown[i] = false
    endif
endfunction

function GSRI_Hide takes nothing returns nothing
    local integer i = 0
    if GSRI_Visible then
        loop
            exitwhen i >= GSRI_POOL_SIZE
            call GSRI_HideSegment(i)
            set GSRI_SegmentValid[i] = false
            set i = i+1
        endloop
        set GSRI_Visible = false
    endif
endfunction

function GSRI_Cancel takes nothing returns nothing
    set GSRI_Key = 0
    set GSRI_LastAbility = 0
    set GSRI_Caster = null
    set GSRI_YawValid = false
    set GSRI_FindAge = 0.00
    call GSRI_Hide()
endfunction

// Shortest angular path, including the -pi/pi seam. Never extrapolate aim.
function GSRI_SmoothYaw takes real target returns real
    local real delta
    if not GSRI_YawValid then
        set GSRI_Yaw = target
        set GSRI_YawValid = true
    else
        set delta = Atan2(Sin(target-GSRI_Yaw), Cos(target-GSRI_Yaw))
        if RAbsBJ(delta) < 0.001 then
            set GSRI_Yaw = target
        else
            set GSRI_Yaw = GSRI_Yaw + delta*GSRI_TURN_BLEND
            set GSRI_Yaw = Atan2(Sin(GSRI_Yaw), Cos(GSRI_Yaw))
        endif
    endif
    return GSRI_Yaw
endfunction

function GSRI_Z takes real x, real y returns real
    call MoveLocation(GSRI_Ground, x, y)
    return GetLocationZ(GSRI_Ground) + 12.00
endfunction

function GSRI_Allowed takes unit u, ability a, integer id returns boolean
    local integer kind = LoadInteger(GSRI_Data, id, 1)
    local integer level = GetUnitAbilityLevel(u, id) - 1
    local real range
    if kind == 0 or level < 0 then
        return false
    endif
    if BlzGetAbilityIntegerField(a, ABILITY_IF_BUTTON_POSITION_NORMAL_X) < 0 or BlzGetAbilityIntegerField(a, ABILITY_IF_BUTTON_POSITION_NORMAL_Y) < 0 then
        return false
    endif
    // Channel: Data B 0 = immediate, 1/2/3 = unit/point/both.
    if kind == 2 and BlzGetAbilityIntegerLevelField(a, ConvertAbilityIntegerLevelField('Ncl2'), level) == 0 then
        return false
    endif
    set range = BlzGetAbilityRealLevelField(a, ABILITY_RLF_CAST_RANGE, level)
    return range > 0.00 and range < 9999.00
endfunction

function GSRI_Find takes unit u, integer key returns integer
    local integer i = 0
    local integer id
    local integer found = 0
    local ability a
    loop
        set a = BlzGetUnitAbilityByIndex(u, i)
        exitwhen a == null
        set id = BlzGetAbilityId(a)
        if LoadInteger(GSRI_Data, id, 0) == key and GSRI_Allowed(u, a, id) then
            // Ambiguous bindings must not silently preview the wrong ability.
            if found != 0 and found != id then
                set a = null
                return 0
            endif
            set found = id
        endif
        set i = i + 1
    endloop
    set a = null
    return found
endfunction

// Sample both ends and midpoint. Do not draw a diagonal bridge over cliffs.
function GSRI_Segment takes real x1, real y1, real x2, real y2 returns nothing
    local integer i = GSRI_DrawIndex
    local real dx = x2-x1
    local real dy = y2-y1
    local real length = SquareRoot(dx*dx+dy*dy)
    local real z1
    local real z2
    local real zm
    if i >= GSRI_POOL_SIZE then
        return
    endif
    set GSRI_DrawIndex = i+1
    if GSRI_SegmentValid[i] and GSRI_X1[i] == x1 and GSRI_Y1[i] == y1 and GSRI_X2[i] == x2 and GSRI_Y2[i] == y2 then
        return
    endif
    set GSRI_X1[i] = x1
    set GSRI_Y1[i] = y1
    set GSRI_X2[i] = x2
    set GSRI_Y2[i] = y2
    set GSRI_SegmentValid[i] = true
    set z1 = GSRI_Z(x1,y1)
    set z2 = GSRI_Z(x2,y2)
    set zm = GSRI_Z((x1+x2)*0.5,(y1+y2)*0.5)
    if length < 0.01 or RAbsBJ(z2-z1) > 64.00 or RAbsBJ(zm-z1) > 64.00 or RAbsBJ(z2-zm) > 64.00 or RAbsBJ(zm-(z1+z2)*0.5) > 12.00 then
        call GSRI_HideSegment(i)
        return
    endif
    // False bypasses fog visibility checks; it grants no terrain/unit vision.
    call MoveLightningEx(GSRI_Effect[i],false,x1,y1,z1,x2,y2,z2)
    if not GSRI_SegmentShown[i] then
        if i < GSRI_RING_LIMIT then
            call SetLightningColor(GSRI_Effect[i],0.294,0.765,1.00,0.78)
        else
            call SetLightningColor(GSRI_Effect[i],0.275,1.00,0.745,0.78)
        endif
        set GSRI_SegmentShown[i] = true
    endif
endfunction

// At most 48 world units between terrain samples along a straight edge.
function GSRI_Line takes real x1, real y1, real x2, real y2 returns nothing
    local real dx = x2-x1
    local real dy = y2-y1
    local integer n = R2I(SquareRoot(dx*dx+dy*dy)/48.00)+1
    local integer j = 0
    loop
        exitwhen j >= n
        call GSRI_Segment(x1+dx*j/n,y1+dy*j/n,x1+dx*(j+1)/n,y1+dy*(j+1)/n)
        set j = j+1
    endloop
endfunction

function GSRI_PathLine takes real x1, real y1, real x2, real y2 returns nothing
    call GSRI_Line(GSRI_OriginX+x1*GSRI_Cos-y1*GSRI_Sin,GSRI_OriginY+x1*GSRI_Sin+y1*GSRI_Cos,GSRI_OriginX+x2*GSRI_Cos-y2*GSRI_Sin,GSRI_OriginY+x2*GSRI_Sin+y2*GSRI_Cos)
endfunction

function GSRI_Trim takes integer oldEnd returns nothing
    local integer i = GSRI_DrawIndex
    loop
        exitwhen i >= oldEnd
        call GSRI_HideSegment(i)
        set GSRI_SegmentValid[i] = false
        set i = i+1
    endloop
endfunction

function GSRI_Draw takes unit u, integer id returns nothing
    local ability a = BlzGetUnitAbility(u, id)
    local integer lv = GetUnitAbilityLevel(u, id)-1
    local real radius = BlzGetAbilityRealLevelField(a,ABILITY_RLF_CAST_RANGE,lv)
    local real x = GetUnitX(u)
    local real y = GetUnitY(u)
    local real dx = GSRI_MouseX-x
    local real dy = GSRI_MouseY-y
    local real yaw
    local real angle1
    local real angle2
    local real startWidth = 125.00
    local integer n = R2I(2.00*bj_PI*radius/48.00)+1
    local integer j = 0
    if not GSRI_Visible then
        set GSRI_ShowCount = GSRI_ShowCount+1
        set GSRI_Visible = true
    endif
    if n > GSRI_RING_LIMIT then
        set n = GSRI_RING_LIMIT
    endif
    set GSRI_LastRange = radius
    set GSRI_DrawIndex = 0
    loop
        exitwhen j >= n
        set angle1 = 2.00*bj_PI*j/n
        set angle2 = 2.00*bj_PI*(j+1)/n
        call GSRI_Segment(x+radius*Cos(angle1),y+radius*Sin(angle1),x+radius*Cos(angle2),y+radius*Sin(angle2))
        set j = j+1
    endloop
    call GSRI_Trim(GSRI_RingCount)
    set GSRI_RingCount = GSRI_DrawIndex
    set GSRI_DrawIndex = GSRI_RING_LIMIT
    if (id == 'A0O8' or id == 'A08G') and GSRI_MouseValid and dx*dx+dy*dy > 0.01 then
        set yaw = GSRI_SmoothYaw(Atan2(dy,dx))
        set GSRI_OriginX = x
        set GSRI_OriginY = y
        set GSRI_Cos = Cos(yaw)
        set GSRI_Sin = Sin(yaw)
        if id == 'A0O8' then
            call GSRI_PathLine(0,-120,1170,-120)
            call GSRI_PathLine(0,120,1170,120)
            call GSRI_PathLine(0,0,1170,0)
            set j = 0
            loop
                exitwhen j >= 12
                set angle1 = bj_PI*0.5+bj_PI*j/12
                set angle2 = bj_PI*0.5+bj_PI*(j+1)/12
                call GSRI_PathLine(120*Cos(angle1),120*Sin(angle1),120*Cos(angle2),120*Sin(angle2))
                call GSRI_PathLine(1170-120*Cos(angle1),-120*Sin(angle1),1170-120*Cos(angle2),-120*Sin(angle2))
                set j = j+1
            endloop
        else
            if lv > 0 then
                set startWidth = 150.00
            endif
            call GSRI_PathLine(0,-startWidth,825,-200)
            call GSRI_PathLine(0,startWidth,825,200)
            call GSRI_PathLine(0,-startWidth,0,startWidth)
            call GSRI_PathLine(825,-200,825,200)
            call GSRI_PathLine(0,0,825,0)
        endif
    endif
    call GSRI_Trim(GSRI_PathCount)
    set GSRI_PathCount = GSRI_DrawIndex
    set a = null
endfunction

function GSRI_Tick takes nothing returns nothing
    local unit u
    local integer id
    local ability a
    if GSRI_Key == 0 then
        return
    endif
    set GSRI_Age = GSRI_Age + GSRI_PERIOD
    set GSRI_FindAge = GSRI_FindAge + GSRI_PERIOD
    set u = udg_HeroPlayer[GetPlayerId(GetLocalPlayer())+1]
    if not BlzIsLocalClientActive() or GSRI_Age > 30.00 or u == null or (GetUnitTypeId(u) != 'Hvwd' and GetUnitTypeId(u) != 'Hkal') or GetWidgetLife(u) <= 0.405 or not IsUnitSelected(u, GetLocalPlayer()) or (GSRI_Caster != null and GSRI_Caster != u) then
        set GSRI_Reason = "hero/selection/focus/timeout"
        call GSRI_Cancel()
        set u = null
        return
    endif
    // Resolve immediately on key press; refresh bindings at 8 Hz, render at 64 Hz.
    set id = GSRI_LastAbility
    if id == 0 or GSRI_FindAge >= 0.125 then
        set id = GSRI_Find(u, GSRI_Key)
        set GSRI_FindAge = 0.00
    endif
    if id != 0 then
        set a = BlzGetUnitAbility(u,id)
        if a == null then
            set id = 0
        elseif not GSRI_Allowed(u,a,id) then
            set id = 0
        endif
        set a = null
    endif
    if id == 0 then
        set GSRI_Reason = "ability unavailable or ambiguous"
        call GSRI_Cancel()
    else
        set GSRI_Reason = "display"
        set GSRI_Caster = u
        set GSRI_LastAbility = id
        call GSRI_Draw(u,id)
    endif
    set u = null
endfunction

function GSRI_OnKey takes nothing returns nothing
    local integer key = GetHandleId(BlzGetTriggerPlayerKey())
    if GetTriggerPlayer() != GetLocalPlayer() then
        return
    endif
    set GSRI_KeyCount = GSRI_KeyCount+1
    set GSRI_Reason = "key " + I2S(key)
    // Native oskey events are suppressed while chat owns focus. Never infer
    // chat state by toggling Enter: the closing Enter/Escape can be absent.
    if key == 13 then
        call GSRI_Cancel()
    elseif key == 27 then
        call GSRI_Cancel()
    elseif key == 112 or key == 119 or key == 79 then
        // Selection/talent/learn screens must not retain the previous preview.
        call GSRI_Cancel()
    else
        call GSRI_Cancel()
        set GSRI_Key = key
        set GSRI_Age = 0.00
        call GSRI_Tick()
    endif
endfunction

function GSRI_OnMouse takes nothing returns nothing
    if GetTriggerPlayer() != GetLocalPlayer() then
        return
    endif
    if GetTriggerEventId() == EVENT_PLAYER_MOUSE_MOVE then
        set GSRI_MouseX = BlzGetTriggerPlayerMouseX()
        set GSRI_MouseY = BlzGetTriggerPlayerMouseY()
        set GSRI_MouseValid = true
    else
        set GSRI_Reason = "mouse click"
        call GSRI_Cancel()
    endif
endfunction

function GSRI_OnSpell takes nothing returns nothing
    if GetTriggerUnit() == GSRI_Caster then
        set GSRI_Reason = "cast or deselect"
        call GSRI_Cancel()
    endif
endfunction

function GSRI_OnChat takes nothing returns nothing
    if GetTriggerPlayer() == GetLocalPlayer() then
        if GetEventPlayerChatString() == "-range" then
            call DisplayTimedTextToPlayer(GetLocalPlayer(),0,0,20,"GSRI v9 fog keys="+I2S(GSRI_KeyCount)+" shows="+I2S(GSRI_ShowCount)+" range="+R2S(GSRI_LastRange)+" last="+GSRI_Reason)
        endif
        call GSRI_Cancel()
    endif
endfunction

function GSRI_Init takes nothing returns nothing
    local trigger keys
    local trigger mouse
    local trigger spell
    local trigger chat
    local integer p = 0
    local integer k
    local integer meta
    local integer i = 0
    if GSRI_Started then
        return
    endif
    set GSRI_Started = true
    set GSRI_Data = InitHashtable()
    set GSRI_Ground = Location(0,0)
    call GSRI_LoadData()
    // Identical handle allocation on every client; rendering state is local.
    set i = 0
    loop
        exitwhen i >= GSRI_POOL_SIZE
        set GSRI_Effect[i] = AddLightningEx("GSRL",false,0,0,0,1,0,0)
        call SetLightningColor(GSRI_Effect[i],0,0,0,0)
        set i = i+1
    endloop
    set keys = CreateTrigger()
    set mouse = CreateTrigger()
    set spell = CreateTrigger()
    set chat = CreateTrigger()
    loop
        exitwhen p >= bj_MAX_PLAYERS
        set k = 65
        loop
            exitwhen k > 90
            call BlzTriggerRegisterPlayerKeyEvent(keys,Player(p),ConvertOsKeyType(k),0,true)
            set k = k+1
        endloop
        // Enter/escape with Shift/Ctrl are also chat/cancel actions.
        set meta = 0
        loop
            exitwhen meta >= 4
            call BlzTriggerRegisterPlayerKeyEvent(keys,Player(p),OSKEY_RETURN,meta,true)
            call BlzTriggerRegisterPlayerKeyEvent(keys,Player(p),OSKEY_ESCAPE,meta,true)
            set meta = meta+1
        endloop
        call BlzTriggerRegisterPlayerKeyEvent(keys,Player(p),OSKEY_F1,0,true)
        call BlzTriggerRegisterPlayerKeyEvent(keys,Player(p),OSKEY_F8,0,true)
        call TriggerRegisterPlayerEvent(mouse,Player(p),EVENT_PLAYER_MOUSE_MOVE)
        call TriggerRegisterPlayerEvent(mouse,Player(p),EVENT_PLAYER_MOUSE_DOWN)
        call TriggerRegisterPlayerChatEvent(chat,Player(p),"",false)
        set p = p+1
    endloop
    call TriggerAddAction(keys,function GSRI_OnKey)
    call TriggerAddAction(mouse,function GSRI_OnMouse)
    call TriggerAddAction(chat,function GSRI_OnChat)
    call TriggerRegisterAnyUnitEventBJ(spell,EVENT_PLAYER_UNIT_SPELL_CHANNEL)
    call TriggerRegisterAnyUnitEventBJ(spell,EVENT_PLAYER_UNIT_DESELECTED)
    call TriggerAddAction(spell,function GSRI_OnSpell)
    call TimerStart(CreateTimer(),GSRI_PERIOD,true,function GSRI_Tick)
    set keys = null
    set mouse = null
    set spell = null
    set chat = null
endfunction
