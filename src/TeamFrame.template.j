//===========================================================================
// GSTF: 팀원 현황 패널 (LoL 스타일, 화면 오른쪽 벽)
//   팀원 영웅 아이콘 / 레벨 / Q W E R 스킬 상태 / 체력 / 마나 / 부활 시간
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

// 스킬 아이콘 크기 / 간격, 체력·마나 바 너비 (기존 이름 자리 0.045~0.107 안에 배치)
function GSTF_SkSize takes nothing returns real
    return 0.015
endfunction

function GSTF_SkGap takes nothing returns real
    return 0.0012
endfunction

function GSTF_BarW takes nothing returns real
    return 0.062
endfunction

// 궁극기(R) 아이콘: Q W E보다 크게, 오른쪽에 살짝 떨어뜨려 배치
function GSTF_UltSize takes nothing returns real
    return 0.0185
endfunction

function GSTF_UltX takes nothing returns real
    return 0.0930
endfunction

// TEXT 프레임은 기본적으로 마우스를 잡아서 뒤쪽 클릭을 막음 -> 비활성화해서 클릭 통과
// (비활성 글자색이 회색이 될 수 있어 색상 코드로 흰색 고정)
function GSTF_PassText takes framehandle f returns nothing
    call BlzFrameSetEnable(f, false)
endfunction

function GSTF_SetText takes string name, integer i, string s returns nothing
    call BlzFrameSetText(BlzGetFrameByName(name, i), "|cffffffff" + s + "|r")
endfunction

//@@SKILL_TABLE@@

function GSTF_Create takes nothing returns nothing
    local framehandle root = BlzCreateFrameByType("FRAME", "GSTF_Root", BlzGetFrameByName("ConsoleUIBackdrop", 0), "", 0)
    local framehandle slot
    local framehandle f
    local framehandle g
    local integer i = 0
    local integer s
    local integer c
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

        // 궁극기 준비 표시: R 아이콘 뒤 금색 테두리 (깜빡임은 GSTF_FillSkill)
        set f = BlzCreateFrameByType("BACKDROP", "GSTF_UltGlow", slot, "", i)
        call BlzFrameSetSize(f, GSTF_UltSize() + 0.005, GSTF_UltSize() + 0.005)
        call BlzFrameSetPoint(f, FRAMEPOINT_TOPLEFT, slot, FRAMEPOINT_TOPLEFT, GSTF_UltX() - 0.0025, -0.0015)
        call BlzFrameSetTexture(f, "UI\\Widgets\\Console\\Human\\CommandButton\\human-activebutton.blp", 0, true)
        call BlzFrameSetVisible(f, false)

        // Q W E 스킬 아이콘 (작게) + R 궁극기 (크게, 오른쪽) + 쿨다운 숫자
        set s = 0
        loop
            exitwhen s > 3
            set c = i * 4 + s
            set f = BlzCreateFrameByType("BACKDROP", "GSTF_Sk", slot, "", c)
            if s < 3 then
                call BlzFrameSetSize(f, GSTF_SkSize(), GSTF_SkSize())
                call BlzFrameSetPoint(f, FRAMEPOINT_TOPLEFT, slot, FRAMEPOINT_TOPLEFT, 0.045 + s * (GSTF_SkSize() + GSTF_SkGap()), -0.006)
            else
                call BlzFrameSetSize(f, GSTF_UltSize(), GSTF_UltSize())
                call BlzFrameSetPoint(f, FRAMEPOINT_TOPLEFT, slot, FRAMEPOINT_TOPLEFT, GSTF_UltX(), -0.004)
            endif
            set g = BlzCreateFrameByType("TEXT", "GSTF_SkCd", f, "", c)
            call BlzFrameSetAllPoints(g, f)
            call BlzFrameSetTextAlignment(g, TEXT_JUSTIFY_MIDDLE, TEXT_JUSTIFY_CENTER)
            call BlzFrameSetScale(g, 0.85)
            call GSTF_PassText(g)
            set s = s + 1
        endloop

        // 체력 바
        set f = BlzCreateFrameByType("BACKDROP", "GSTF_HpBg", slot, "", i)
        call BlzFrameSetSize(f, GSTF_BarW(), 0.0065)
        call BlzFrameSetPoint(f, FRAMEPOINT_TOPLEFT, slot, FRAMEPOINT_TOPLEFT, 0.045, -0.025)
        call BlzFrameSetTexture(f, "Textures\\Black32.blp", 0, true)
        set g = BlzCreateFrameByType("BACKDROP", "GSTF_Hp", f, "", i)
        call BlzFrameSetPoint(g, FRAMEPOINT_TOPLEFT, f, FRAMEPOINT_TOPLEFT, 0.0, 0.0)
        call BlzFrameSetSize(g, GSTF_BarW(), 0.0065)
        call BlzFrameSetTexture(g, "ReplaceableTextures\\TeamColor\\TeamColor06.blp", 0, true)

        // 마나 바
        set f = BlzCreateFrameByType("BACKDROP", "GSTF_MpBg", slot, "", i)
        call BlzFrameSetSize(f, GSTF_BarW(), 0.0055)
        call BlzFrameSetPoint(f, FRAMEPOINT_TOPLEFT, slot, FRAMEPOINT_TOPLEFT, 0.045, -0.0345)
        call BlzFrameSetTexture(f, "Textures\\Black32.blp", 0, true)
        set g = BlzCreateFrameByType("BACKDROP", "GSTF_Mp", f, "", i)
        call BlzFrameSetPoint(g, FRAMEPOINT_TOPLEFT, f, FRAMEPOINT_TOPLEFT, 0.0, 0.0)
        call BlzFrameSetSize(g, GSTF_BarW(), 0.0055)
        call BlzFrameSetTexture(g, "ReplaceableTextures\\TeamColor\\TeamColor01.blp", 0, true)

        // 사망(부활 대기): 슬롯 전체를 어둡게 덮고 아이콘 위에 남은 부활 시간
        set f = BlzCreateFrameByType("BACKDROP", "GSTF_Dead", slot, "", i)
        call BlzFrameSetAllPoints(f, slot)
        call BlzFrameSetTexture(f, "Textures\\Black32.blp", 0, true)
        call BlzFrameSetAlpha(f, 150)
        set g = BlzCreateFrameByType("TEXT", "GSTF_DeadTime", f, "", i)
        call BlzFrameSetAllPoints(g, BlzGetFrameByName("GSTF_Icon", i))
        call BlzFrameSetTextAlignment(g, TEXT_JUSTIFY_MIDDLE, TEXT_JUSTIFY_CENTER)
        call BlzFrameSetScale(g, 1.5)
        call GSTF_PassText(g)
        set g = BlzCreateFrameByType("TEXT", "GSTF_DeadLbl", f, "", i)
        call BlzFrameSetPoint(g, FRAMEPOINT_LEFT, f, FRAMEPOINT_LEFT, 0.047, 0.0)
        call BlzFrameSetSize(g, 0.066, 0.02)
        call BlzFrameSetTextAlignment(g, TEXT_JUSTIFY_MIDDLE, TEXT_JUSTIFY_LEFT)
        call GSTF_PassText(g)
        call BlzFrameSetText(g, "|cffff8080부활 대기 중|r")
        call BlzFrameSetVisible(f, false)

        call BlzFrameSetVisible(slot, false)
        set i = i + 1
    endloop
    set root = null
    set slot = null
    set f = null
    set g = null
endfunction

// 바 채우기: 비율 0이면 숨김 (크기 0 프레임은 기본 크기로 그려질 수 있음)
function GSTF_SetBar takes string name, integer i, real h, real ratio returns nothing
    local framehandle f = BlzGetFrameByName(name, i)
    if ratio > 0.001 then
        if ratio > 1.0 then
            set ratio = 1.0
        endif
        call BlzFrameSetSize(f, GSTF_BarW() * ratio, h)
        call BlzFrameSetVisible(f, true)
    else
        call BlzFrameSetVisible(f, false)
    endif
    set f = null
endfunction

// 스킬 아이콘 하나: 미습득 = 흐림 / 패시브 = 배우면 밝게 / 쿨다운 = 남은 초 / 마나 부족 = 반투명 / 준비 = 밝게
function GSTF_FillSkill takes integer i, integer s, unit u returns nothing
    local integer c = i * 4 + s
    local integer a = GSTF_SkillOf(GetUnitTypeId(u), s)
    local integer lvl
    local real cd
    local framehandle f = BlzGetFrameByName("GSTF_Sk", c)
    local boolean ready = false
    if a == 0 then
        call BlzFrameSetVisible(f, false)
        set f = null
        return
    endif
    call BlzFrameSetVisible(f, true)
    call BlzFrameSetTexture(f, BlzGetAbilityIcon(a), 0, true)
    call BlzFrameSetText(BlzGetFrameByName("GSTF_SkCd", c), "")
    set lvl = GetUnitAbilityLevel(u, a)
    if lvl == 0 then
        call BlzFrameSetAlpha(f, 45)
    elseif GSTF_IsPassive(a) then
        call BlzFrameSetAlpha(f, 255)
    else
        set cd = BlzGetUnitAbilityCooldownRemaining(u, a)
        if cd > 0.0 then
            call BlzFrameSetAlpha(f, 110)
            call GSTF_SetText("GSTF_SkCd", c, I2S(R2I(cd) + 1))
        elseif GetUnitState(u, UNIT_STATE_MANA) < BlzGetUnitAbilityManaCost(u, a, lvl - 1) then
            call BlzFrameSetAlpha(f, 150)
        else
            call BlzFrameSetAlpha(f, 255)
            set ready = true
        endif
    endif
    // 궁극기 준비: 금색 테두리가 은은하게 깜빡임 (패시브 궁극기는 표시 안 함)
    if s == 3 then
        set f = BlzGetFrameByName("GSTF_UltGlow", i)
        call BlzFrameSetVisible(f, ready)
        if ready then
            call BlzFrameSetAlpha(f, 120 + R2I(135.0 * RAbsBJ(Sin(TimerGetElapsed(udg_MBTime) * 3.0))))
        endif
    endif
    set f = null
endfunction

function GSTF_FillSlot takes integer i, player p, unit u returns nothing
    local integer revive = udg_RevivalTimer[udg_SP_Number[GetPlayerId(p) + 1]]
    local boolean dead = IsUnitType(u, UNIT_TYPE_DEAD) or GetWidgetLife(u) < 0.405 or revive >= 1
    local integer s = 0
    local real maxv

    call BlzFrameSetTexture(BlzGetFrameByName("GSTF_Icon", i), BlzGetAbilityIcon(GetUnitTypeId(u)), 0, true)
    call GSTF_SetText("GSTF_Lvl", i, I2S(GetHeroLevel(u)))
    loop
        exitwhen s > 3
        call GSTF_FillSkill(i, s, u)
        set s = s + 1
    endloop

    // 사망 / 부활 대기 (맵이 부활 대기 중인 영웅을 반투명 무적 상태로 살려 두므로 부활 타이머로 판단)
    call BlzFrameSetVisible(BlzGetFrameByName("GSTF_Dead", i), dead)
    if dead then
        call BlzFrameSetVisible(BlzGetFrameByName("GSTF_UltGlow", i), false)
        if revive >= 1 then
            call BlzFrameSetText(BlzGetFrameByName("GSTF_DeadTime", i), "|cffff6060" + I2S(revive) + "|r")
        else
            call BlzFrameSetText(BlzGetFrameByName("GSTF_DeadTime", i), "")
        endif
        call GSTF_SetBar("GSTF_Hp", i, 0.0065, 0)
        call GSTF_SetBar("GSTF_Mp", i, 0.0055, 0)
        return
    endif

    set maxv = GetUnitState(u, UNIT_STATE_MAX_LIFE)
    if maxv > 0 then
        call GSTF_SetBar("GSTF_Hp", i, 0.0065, GetUnitState(u, UNIT_STATE_LIFE) / maxv)
    else
        call GSTF_SetBar("GSTF_Hp", i, 0.0065, 0)
    endif
    set maxv = GetUnitState(u, UNIT_STATE_MAX_MANA)
    if maxv > 0 then
        call GSTF_SetBar("GSTF_Mp", i, 0.0055, GetUnitState(u, UNIT_STATE_MANA) / maxv)
    else
        call GSTF_SetBar("GSTF_Mp", i, 0.0055, 0)
    endif
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
