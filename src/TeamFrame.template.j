//===========================================================================
// GSTF: 팀원 현황 패널 (LoL 스타일, 화면 오른쪽 벽)
//   팀원 영웅 아이콘 / 레벨 / 체력 / 마나 / 궁극기 준비 여부
//
//   사용법: 맵 초기화 트리거에 사용자 지정 스크립트  call GSTF_Init()
//   전역 변수를 쓰지 않음 (프레임은 이름으로 다시 찾음) -> vJASS 없이 동작
//   udg_HeroPlayer[플레이어 번호] 에 저장된 영웅을 표시
//===========================================================================

// true: 자기 영웅도 목록에 표시 / false: 팀원만 (LoL 방식)
function GSTF_ShowSelf takes nothing returns boolean
    return false
endfunction

// 슬롯 크기 (화면 좌표 0.8 x 0.6 기준)
function GSTF_W takes nothing returns real
    return 0.112
endfunction

function GSTF_H takes nothing returns real
    return 0.046
endfunction

function GSTF_Gap takes nothing returns real
    return 0.005
endfunction

// 패널 윗변 높이: 접힌 스코어보드(오른쪽 끝, y 0.533~0.551) 바로 아래
function GSTF_Top takes nothing returns real
    return 0.525
endfunction

// TEXT 프레임은 기본적으로 마우스를 잡아서 뒤쪽 클릭을 막음 -> 비활성화해서 클릭 통과
// (비활성 글자색이 회색이 될 수 있어 색상 코드로 흰색 고정)
function GSTF_PassText takes framehandle f returns nothing
    call BlzFrameSetEnable(f, false)
endfunction

function GSTF_SetText takes string name, integer i, string s returns nothing
    call BlzFrameSetText(BlzGetFrameByName(name, i), "|cffffffff" + s + "|r")
endfunction

//@@ULT_TABLE@@

function GSTF_Create takes nothing returns nothing
    local framehandle root = BlzCreateFrameByType("FRAME", "GSTF_Root", BlzGetFrameByName("ConsoleUIBackdrop", 0), "", 0)
    local framehandle slot
    local framehandle f
    local framehandle g
    local integer i = 0
    call BlzFrameSetSize(root, GSTF_W(), 5 * (GSTF_H() + GSTF_Gap()))
    loop
        exitwhen i > 4
        set slot = BlzCreateFrameByType("BACKDROP", "GSTF_Slot", root, "", i)
        call BlzFrameSetSize(slot, GSTF_W(), GSTF_H())
        call BlzFrameSetTexture(slot, "Textures\\Black32.blp", 0, true)
        call BlzFrameSetAlpha(slot, 160)

        // 영웅 아이콘 + 레벨
        set f = BlzCreateFrameByType("BACKDROP", "GSTF_Icon", slot, "", i)
        call BlzFrameSetSize(f, 0.036, 0.036)
        call BlzFrameSetPoint(f, FRAMEPOINT_TOPLEFT, slot, FRAMEPOINT_TOPLEFT, 0.005, -0.005)
        set g = BlzCreateFrameByType("BACKDROP", "GSTF_LvlBg", f, "", i)
        call BlzFrameSetSize(g, 0.015, 0.011)
        call BlzFrameSetPoint(g, FRAMEPOINT_BOTTOMRIGHT, f, FRAMEPOINT_BOTTOMRIGHT, 0.0, 0.0)
        call BlzFrameSetTexture(g, "Textures\\Black32.blp", 0, true)
        call BlzFrameSetAlpha(g, 200)
        set g = BlzCreateFrameByType("TEXT", "GSTF_Lvl", f, "", i)
        call BlzFrameSetAllPoints(g, BlzGetFrameByName("GSTF_LvlBg", i))
        call BlzFrameSetTextAlignment(g, TEXT_JUSTIFY_MIDDLE, TEXT_JUSTIFY_CENTER)
        call BlzFrameSetScale(g, 0.8)
        call GSTF_PassText(g)

        // 플레이어 이름 (Scale 0.8이면 크기·오프셋도 0.8배가 되므로 /0.8로 보정)
        set f = BlzCreateFrameByType("TEXT", "GSTF_Name", slot, "", i)
        call BlzFrameSetScale(f, 0.8)
        call BlzFrameSetSize(f, 0.044 / 0.8, 0.012 / 0.8)
        call BlzFrameSetPoint(f, FRAMEPOINT_TOPLEFT, slot, FRAMEPOINT_TOPLEFT, 0.045 / 0.8, -0.006 / 0.8)
        call BlzFrameSetTextAlignment(f, TEXT_JUSTIFY_MIDDLE, TEXT_JUSTIFY_LEFT)
        call GSTF_PassText(f)

        // 궁극기 아이콘 + 쿨다운 숫자 + 준비 표시(초록 점)
        set f = BlzCreateFrameByType("BACKDROP", "GSTF_Ult", slot, "", i)
        call BlzFrameSetSize(f, 0.018, 0.018)
        call BlzFrameSetPoint(f, FRAMEPOINT_TOPRIGHT, slot, FRAMEPOINT_TOPRIGHT, -0.004, -0.004)
        set g = BlzCreateFrameByType("TEXT", "GSTF_UltCd", f, "", i)
        call BlzFrameSetAllPoints(g, f)
        call BlzFrameSetTextAlignment(g, TEXT_JUSTIFY_MIDDLE, TEXT_JUSTIFY_CENTER)
        call GSTF_PassText(g)
        set g = BlzCreateFrameByType("BACKDROP", "GSTF_UltDot", f, "", i)
        call BlzFrameSetSize(g, 0.006, 0.006)
        call BlzFrameSetPoint(g, FRAMEPOINT_BOTTOMRIGHT, f, FRAMEPOINT_BOTTOMRIGHT, 0.0, 0.0)
        call BlzFrameSetTexture(g, "ReplaceableTextures\\TeamColor\\TeamColor06.blp", 0, true)

        // 체력 바
        set f = BlzCreateFrameByType("BACKDROP", "GSTF_HpBg", slot, "", i)
        call BlzFrameSetSize(f, 0.062, 0.0065)
        call BlzFrameSetPoint(f, FRAMEPOINT_TOPLEFT, slot, FRAMEPOINT_TOPLEFT, 0.045, -0.025)
        call BlzFrameSetTexture(f, "Textures\\Black32.blp", 0, true)
        set g = BlzCreateFrameByType("BACKDROP", "GSTF_Hp", f, "", i)
        call BlzFrameSetPoint(g, FRAMEPOINT_TOPLEFT, f, FRAMEPOINT_TOPLEFT, 0.0, 0.0)
        call BlzFrameSetSize(g, 0.062, 0.0065)
        call BlzFrameSetTexture(g, "ReplaceableTextures\\TeamColor\\TeamColor06.blp", 0, true)

        // 마나 바
        set f = BlzCreateFrameByType("BACKDROP", "GSTF_MpBg", slot, "", i)
        call BlzFrameSetSize(f, 0.062, 0.0055)
        call BlzFrameSetPoint(f, FRAMEPOINT_TOPLEFT, slot, FRAMEPOINT_TOPLEFT, 0.045, -0.0345)
        call BlzFrameSetTexture(f, "Textures\\Black32.blp", 0, true)
        set g = BlzCreateFrameByType("BACKDROP", "GSTF_Mp", f, "", i)
        call BlzFrameSetPoint(g, FRAMEPOINT_TOPLEFT, f, FRAMEPOINT_TOPLEFT, 0.0, 0.0)
        call BlzFrameSetSize(g, 0.062, 0.0055)
        call BlzFrameSetTexture(g, "ReplaceableTextures\\TeamColor\\TeamColor01.blp", 0, true)

        call BlzFrameSetVisible(slot, false)
        set i = i + 1
    endloop
    set root = null
    set slot = null
    set f = null
    set g = null
endfunction

// 바 채우기: 비율 0이면 숨김 (크기 0 프레임은 기본 크기로 그려질 수 있음)
function GSTF_SetBar takes string name, integer i, real full, real h, real ratio returns nothing
    local framehandle f = BlzGetFrameByName(name, i)
    if ratio > 0.001 then
        if ratio > 1.0 then
            set ratio = 1.0
        endif
        call BlzFrameSetSize(f, full * ratio, h)
        call BlzFrameSetVisible(f, true)
    else
        call BlzFrameSetVisible(f, false)
    endif
    set f = null
endfunction

function GSTF_FillSlot takes integer i, player p, unit u returns nothing
    local integer ult = GSTF_UltOf(GetUnitTypeId(u))
    local integer lvl
    local real cd
    local real maxv
    local boolean dead = IsUnitType(u, UNIT_TYPE_DEAD) or GetWidgetLife(u) < 0.405
    local framehandle icon = BlzGetFrameByName("GSTF_Icon", i)
    local framehandle uf = BlzGetFrameByName("GSTF_Ult", i)

    call BlzFrameSetTexture(icon, BlzGetAbilityIcon(GetUnitTypeId(u)), 0, true)
    if dead then
        call BlzFrameSetAlpha(icon, 90)
    else
        call BlzFrameSetAlpha(icon, 255)
    endif
    call GSTF_SetText("GSTF_Lvl", i, I2S(GetHeroLevel(u)))
    call GSTF_SetText("GSTF_Name", i, GetPlayerName(p))

    set maxv = GetUnitState(u, UNIT_STATE_MAX_LIFE)
    if dead or maxv <= 0 then
        call GSTF_SetBar("GSTF_Hp", i, 0.062, 0.0065, 0)
    else
        call GSTF_SetBar("GSTF_Hp", i, 0.062, 0.0065, GetUnitState(u, UNIT_STATE_LIFE) / maxv)
    endif
    set maxv = GetUnitState(u, UNIT_STATE_MAX_MANA)
    if dead or maxv <= 0 then
        call GSTF_SetBar("GSTF_Mp", i, 0.062, 0.0055, 0)
    else
        call GSTF_SetBar("GSTF_Mp", i, 0.062, 0.0055, GetUnitState(u, UNIT_STATE_MANA) / maxv)
    endif

    if ult == 0 then
        call BlzFrameSetVisible(uf, false)
    else
        call BlzFrameSetVisible(uf, true)
        call BlzFrameSetTexture(uf, BlzGetAbilityIcon(ult), 0, true)
        set lvl = GetUnitAbilityLevel(u, ult)
        call BlzFrameSetVisible(BlzGetFrameByName("GSTF_UltDot", i), false)
        call BlzFrameSetText(BlzGetFrameByName("GSTF_UltCd", i), "")
        if lvl == 0 then
            // 미습득
            call BlzFrameSetAlpha(uf, 50)
        else
            set cd = BlzGetUnitAbilityCooldownRemaining(u, ult)
            if cd > 0.0 then
                call BlzFrameSetAlpha(uf, 110)
                call GSTF_SetText("GSTF_UltCd", i, I2S(R2I(cd) + 1))
            elseif dead or GetUnitState(u, UNIT_STATE_MANA) < BlzGetUnitAbilityManaCost(u, ult, lvl - 1) then
                // 쿨은 돌았지만 사망/마나 부족
                call BlzFrameSetAlpha(uf, 150)
            else
                call BlzFrameSetAlpha(uf, 255)
                call BlzFrameSetVisible(BlzGetFrameByName("GSTF_UltDot", i), true)
            endif
        endif
    endif
    set icon = null
    set uf = null
endfunction

// 로컬 플레이어의 팀원인지: 슬롯 번호가 아니라 실제 동맹 상태로 판단
// (-sp 팀 섞기, -동맹 등으로 동맹이 바뀌어도 그대로 따라감)
function GSTF_IsTeammate takes player p, player lp returns boolean
    if p == lp then
        return GSTF_ShowSelf()
    endif
    return IsPlayerAlly(p, lp) and IsPlayerAlly(lp, p)
endfunction

function GSTF_Update takes nothing returns nothing
    local player lp = GetLocalPlayer()
    local player p
    local integer pid = 0
    local integer k = 0
    local unit u
    local real w = I2R(BlzGetLocalClientWidth())
    local real h = I2R(BlzGetLocalClientHeight())
    local real right = 0.8
    local framehandle root = BlzGetFrameByName("GSTF_Root", 0)
    local framehandle slot

    // 표시는 로컬 플레이어 기준 (프레임 조작만 하므로 디싱크 없음)

    // 스코어보드(udg_MB)를 펼치면 같은 자리를 덮으므로 패널을 숨김, 접으면 다시 표시
    // (펼침/접힘은 플레이어마다 각자 화면 상태)
    if udg_MB != null and IsMultiboardDisplayed(udg_MB) and not IsMultiboardMinimized(udg_MB) then
        call BlzFrameSetVisible(root, false)
        set lp = null
        set root = null
        return
    endif
    call BlzFrameSetVisible(root, true)

    // 와이드 화면에서도 실제 오른쪽 끝에 붙임 (스코어보드도 화면 끝 기준)
    if h > 0 then
        set right = 0.4 + 0.3 * w / h
    endif
    call BlzFrameClearAllPoints(root)
    call BlzFrameSetAbsPoint(root, FRAMEPOINT_TOPRIGHT, right - 0.004, GSTF_Top())

    // 모든 플레이어 슬롯(0~11)을 훑어서, 영웅이 있고 동맹인 플레이어만 슬롯 순서대로 표시
    // 영웅: udg_HeroPlayer[플레이어 번호] (선택/랜덤/-ap/스왑/교체 시 맵 트리거가 갱신)
    loop
        exitwhen pid > 11 or k > 4
        set p = Player(pid)
        set u = udg_HeroPlayer[pid + 1]
        if u != null and IsUnitType(u, UNIT_TYPE_HERO) and GSTF_IsTeammate(p, lp) then
            set slot = BlzGetFrameByName("GSTF_Slot", k)
            call BlzFrameClearAllPoints(slot)
            call BlzFrameSetPoint(slot, FRAMEPOINT_TOPRIGHT, root, FRAMEPOINT_TOPRIGHT, 0.0, -k * (GSTF_H() + GSTF_Gap()))
            call BlzFrameSetVisible(slot, true)
            call GSTF_FillSlot(k, p, u)
            set k = k + 1
        endif
        set pid = pid + 1
    endloop
    loop
        exitwhen k > 4
        call BlzFrameSetVisible(BlzGetFrameByName("GSTF_Slot", k), false)
        set k = k + 1
    endloop
    set lp = null
    set p = null
    set u = null
    set root = null
    set slot = null
endfunction

function GSTF_Start takes nothing returns nothing
    call DestroyTimer(GetExpiredTimer())
    call GSTF_Create()
    call TimerStart(CreateTimer(), 0.1, true, function GSTF_Update)
endfunction

function GSTF_Init takes nothing returns nothing
    // 게임 UI가 준비된 뒤 생성
    call TimerStart(CreateTimer(), 0.0, false, function GSTF_Start)
endfunction
