//===========================================================================
// GSPF: 게임 시작 흐름
//   1) 1픽(Player 1, 없으면 가디언 첫 유저)에게 게임 모드 선택 팝업
//      - 같이 켤 수 없는 모드는 자동 잠금, 기존 명령어 표기
//      - 확정하면 기존 모드 트리거(Mode_AP 등)를 그대로 실행
//      - 1픽이 확정할 때까지 대기 (잠수 대비: GSPF_ModeTimeout 초 뒤 자동 확정)
//   2) 확정 직후 모두에게 영웅 선택 보드
//      - 아이콘 클릭 = 기존 상점(정령)에서 구매 (중복/밴/3P2R/올픽 규칙 그대로 적용)
//      - 선택하면 보드 닫힘, 상점이 사라지는 120초에 모두 닫힘, -보드 로 다시 열기
//
//   사용법: 맵 초기화 트리거에 사용자 지정 스크립트  call GSPF_Init()
//   전역 변수 없음: 공유 상태는 숨긴 TEXT 프레임에 저장 (모든 클라이언트가 동기 코드에서
//   같은 값으로 갱신), 버튼 클릭 이벤트는 네트워크 동기화됨
//===========================================================================

// 1픽이 확정하지 않을 때 자동 확정까지 걸리는 시간(초)
function GSPF_ModeTimeout takes nothing returns integer
    return 30
endfunction

// 영웅 선택 보드 표 (tools/teamframe.py gen 으로 생성)
function GSPF_HeroCount takes nothing returns integer
    return 67
endfunction

function GSPF_HeroAt takes integer i returns integer
    if i == 0 then
        return 'Nman'
    elseif i == 1 then
        return 'Hamg'
    elseif i == 2 then
        return 'Emfr'
    elseif i == 3 then
        return 'Hjai'
    elseif i == 4 then
        return 'Hpb2'
    elseif i == 5 then
        return 'Ekee'
    elseif i == 6 then
        return 'Hkal'
    elseif i == 7 then
        return 'Hart'
    elseif i == 8 then
        return 'Osam'
    elseif i == 9 then
        return 'Ntin'
    elseif i == 10 then
        return 'Ekgg'
    elseif i == 11 then
        return 'Hpal'
    elseif i == 12 then
        return 'Harf'
    elseif i == 13 then
        return 'Ofar'
    elseif i == 14 then
        return 'Hpb1'
    elseif i == 15 then
        return 'Hmkg'
    elseif i == 16 then
        return 'Hmgd'
    elseif i == 17 then
        return 'Nsjs'
    elseif i == 18 then
        return 'Hmbr'
    elseif i == 19 then
        return 'Ocbh'
    elseif i == 20 then
        return 'Hhkl'
    elseif i == 21 then
        return 'Ocb2'
    elseif i == 22 then
        return 'Orex'
    elseif i == 23 then
        return 'Obla'
    elseif i == 24 then
        return 'Hvwd'
    elseif i == 25 then
        return 'Ewrd'
    elseif i == 26 then
        return 'Emoo'
    elseif i == 27 then
        return 'Hdgo'
    elseif i == 28 then
        return 'Npbm'
    elseif i == 29 then
        return 'Etyr'
    elseif i == 30 then
        return 'Eevi'
    elseif i == 31 then
        return 'Ogrh'
    elseif i == 32 then
        return 'Huth'
    elseif i == 33 then
        return 'Opgh'
    elseif i == 34 then
        return 'Hgam'
    elseif i == 35 then
        return 'Uanb'
    elseif i == 36 then
        return 'Nfir'
    elseif i == 37 then
        return 'Udea'
    elseif i == 38 then
        return 'Nbrn'
    elseif i == 39 then
        return 'Ogld'
    elseif i == 40 then
        return 'Hblm'
    elseif i == 41 then
        return 'Ulic'
    elseif i == 42 then
        return 'Ucrl'
    elseif i == 43 then
        return 'Uclc'
    elseif i == 44 then
        return 'Nklj'
    elseif i == 45 then
        return 'Otch'
    elseif i == 46 then
        return 'Uear'
    elseif i == 47 then
        return 'Ewar'
    elseif i == 48 then
        return 'Udre'
    elseif i == 49 then
        return 'Nbbc'
    elseif i == 50 then
        return 'Nmag'
    elseif i == 51 then
        return 'Ubal'
    elseif i == 52 then
        return 'Eill'
    elseif i == 53 then
        return 'Nplh'
    elseif i == 54 then
        return 'Hapm'
    elseif i == 55 then
        return 'Utic'
    elseif i == 56 then
        return 'Eevm'
    elseif i == 57 then
        return 'Edem'
    elseif i == 58 then
        return 'Uvng'
    elseif i == 59 then
        return 'Usyl'
    elseif i == 60 then
        return 'Hvsh'
    elseif i == 61 then
        return 'Odrt'
    elseif i == 62 then
        return 'Uwar'
    elseif i == 63 then
        return 'Hant'
    elseif i == 64 then
        return 'Umal'
    elseif i == 65 then
        return 'Oshd'
    elseif i == 66 then
        return 'Naka'
    endif
    return 0
endfunction

function GSPF_GroupOf takes integer i returns integer
    if i < 11 then
        return 0
    endif
    if i < 23 then
        return 1
    endif
    if i < 35 then
        return 2
    endif
    if i < 45 then
        return 3
    endif
    if i < 56 then
        return 4
    endif
    if i < 67 then
        return 5
    endif
    return 5
endfunction

function GSPF_Shop takes integer g returns unit
    if g == 0 then
        return gg_unit_n015_0040
    elseif g == 1 then
        return gg_unit_n016_0041
    elseif g == 2 then
        return gg_unit_n017_0088
    elseif g == 3 then
        return gg_unit_n018_0091
    elseif g == 4 then
        return gg_unit_n019_0090
    elseif g == 5 then
        return gg_unit_n01A_0089
    endif
    return null
endfunction

function GSPF_GroupLabel takes integer g returns string
    if g == 0 then
        return "|cff70b0ff가디언|r\n|cffffffff지식|r"
    elseif g == 1 then
        return "|cff70b0ff가디언|r\n|cffffffff힘|r"
    elseif g == 2 then
        return "|cff70b0ff가디언|r\n|cffffffff기민|r"
    elseif g == 3 then
        return "|cffff7070다크니스|r\n|cffffffff지식|r"
    elseif g == 4 then
        return "|cffff7070다크니스|r\n|cffffffff힘|r"
    elseif g == 5 then
        return "|cffff7070다크니스|r\n|cffffffff기민|r"
    endif
    return ""
endfunction

//--- 공유 상태 (숨긴 TEXT 프레임) -----------------------------------------
function GSPF_GetState takes string name returns string
    return BlzFrameGetText(BlzGetFrameByName(name, 0))
endfunction

function GSPF_SetState takes string name, string v returns nothing
    call BlzFrameSetText(BlzGetFrameByName(name, 0), v)
endfunction

function GSPF_IsUser takes player p returns boolean
    return GetPlayerSlotState(p) == PLAYER_SLOT_STATE_PLAYING and GetPlayerController(p) == MAP_CONTROL_USER
endfunction

// 1픽: Player 1, 없으면 가디언 첫 유저, 그래도 없으면 첫 유저 (-1 = 없음)
function GSPF_FindHost takes nothing returns integer
    local integer i = 1
    loop
        exitwhen i > 5
        if GSPF_IsUser(Player(i)) then
            return i
        endif
        set i = i + 1
    endloop
    set i = 0
    loop
        exitwhen i > 11
        if GSPF_IsUser(Player(i)) then
            return i
        endif
        set i = i + 1
    endloop
    return -1
endfunction

function GSPF_HostId takes nothing returns integer
    return S2I(GSPF_GetState("GSPF_Host"))
endfunction

//--- 모드: 0 AP, 1 SP, 2 HS, 3 AR, 4 PR, 5 DG ------------------------------
function GSPF_ModeLabel takes integer k returns string
    if k == 0 then
        return "올픽 All Pick  |cff999999(-ap)|r"
    elseif k == 1 then
        return "팀 섞기 Shuffle  |cff999999(-sp)|r"
    elseif k == 2 then
        return "익명 팀 섞기 Hide Shuffle  |cff999999(-hs)|r"
    elseif k == 3 then
        return "올랜덤 All Random  |cff999999(-ar)|r"
    elseif k == 4 then
        return "3픽 2랜덤  |cff999999(-pr)|r"
    endif
    return "데미지 표시  |cff999999(-dmg)|r"
endfunction

// 같이 켤 수 없는 모드 (없으면 -1)
function GSPF_ModeRival takes integer k returns integer
    if k == 1 then
        return 2
    elseif k == 2 then
        return 1
    elseif k == 3 then
        return 4
    elseif k == 4 then
        return 3
    endif
    return -1
endfunction

// 이미 켜져 있는지 (채팅 명령어로 켠 경우 포함)
function GSPF_ModeActive takes integer k returns boolean
    if k == 0 then
        return udg_ModeAllpick
    elseif k == 1 then
        return udg_ModeSP and udg_SP_Level != 1
    elseif k == 2 then
        return udg_ModeSP and udg_SP_Level == 1
    elseif k == 3 then
        return udg_ModeRandom
    elseif k == 4 then
        return udg_Mode3P2R
    endif
    return IsTriggerEnabled(gg_trg_Damage_Test)
endfunction

function GSPF_Sel takes integer k returns boolean
    return SubString(GSPF_GetState("GSPF_Sel"), k, k + 1) == "1"
endfunction

function GSPF_SetSel takes integer k, boolean on returns nothing
    local string s = GSPF_GetState("GSPF_Sel")
    local string c = "0"
    if on then
        set c = "1"
    endif
    call GSPF_SetState("GSPF_Sel", SubString(s, 0, k) + c + SubString(s, k + 1, 6))
endfunction

function GSPF_ModeBlocked takes integer k returns boolean
    local integer r = GSPF_ModeRival(k)
    if GSPF_ModeActive(k) then
        return true
    endif
    if r >= 0 and (GSPF_Sel(r) or GSPF_ModeActive(r)) then
        return true
    endif
    return false
endfunction

function GSPF_RefreshModes takes nothing returns nothing
    local integer k = 0
    local framehandle b
    local string t
    loop
        exitwhen k > 5
        set b = BlzGetFrameByName("ScriptDialogButton", 7100 + k)
        if GSPF_ModeActive(k) then
            set t = "|cff80ff80[켜짐]|r " + GSPF_ModeLabel(k)
        elseif GSPF_ModeBlocked(k) then
            set t = "|cff808080[  ] " + GSPF_ModeLabel(k) + "|r |cffff6060(중복 불가)|r"
        elseif GSPF_Sel(k) then
            set t = "|cffffcc00[V]|r " + GSPF_ModeLabel(k)
        else
            set t = "[  ] " + GSPF_ModeLabel(k)
        endif
        call BlzFrameSetText(b, t)
        call BlzFrameSetEnable(b, not GSPF_ModeBlocked(k))
        set k = k + 1
    endloop
    set b = null
endfunction

//--- 영웅 보드 --------------------------------------------------------------
function GSPF_ShopsAlive takes nothing returns boolean
    local integer g = 0
    loop
        exitwhen g > 5
        if GetUnitTypeId(GSPF_Shop(g)) == 0 then
            return false
        endif
        set g = g + 1
    endloop
    return TimerGetElapsed(udg_MBTime) <= 120.0
endfunction

function GSPF_RowVisible takes integer g, player p returns boolean
    return udg_ModeAllpick or ((g < 3) == IsPlayerAlly(p, udg_Force[1]))
endfunction

// 로컬 화면 갱신 (프레임만 조작 -> 디싱크 없음)
function GSPF_BoardTick takes nothing returns nothing
    local player lp = GetLocalPlayer()
    local framehandle board = BlzGetFrameByName("EscMenuBackdrop", 7002)
    local framehandle b
    local integer i = 0
    local integer g
    local integer row = -1
    local integer lastg = -1
    local integer col = 0
    local integer hid
    local boolean open
    local boolean ok
    local string hint = ""

    if not GSPF_ShopsAlive() then
        call BlzFrameSetVisible(board, false)
        call DestroyTimer(GetExpiredTimer())
        set board = null
        set lp = null
        return
    endif
    set open = GSPF_IsUser(lp) and GetUnitTypeId(udg_HeroPlayer[GetPlayerId(lp) + 1]) == 0 and GSPF_GetState("GSPF_Closed") != "1"
    call BlzFrameSetVisible(board, open)
    if not open then
        set board = null
        set lp = null
        return
    endif

    // 줄 단위 배치: 보이는 진영 줄만 위에서부터
    set g = 0
    loop
        exitwhen g > 5
        call BlzFrameSetVisible(BlzGetFrameByName("GSPF_RowLbl", g), GSPF_RowVisible(g, lp))
        set g = g + 1
    endloop
    loop
        exitwhen i >= GSPF_HeroCount()
        set g = GSPF_GroupOf(i)
        set b = BlzGetFrameByName("ScoreScreenBottomButtonTemplate", 7400 + i)
        if GSPF_RowVisible(g, lp) then
            if g != lastg then
                set row = row + 1
                set lastg = g
                set col = 0
                call BlzFrameSetPoint(BlzGetFrameByName("GSPF_RowLbl", g), FRAMEPOINT_TOPLEFT, board, FRAMEPOINT_TOPLEFT, 0.022, -0.048 - row * 0.042)
            endif
            call BlzFrameClearAllPoints(b)
            call BlzFrameSetPoint(b, FRAMEPOINT_TOPLEFT, board, FRAMEPOINT_TOPLEFT, 0.092 + col * 0.037, -0.048 - row * 0.042)
            set hid = GSPF_HeroAt(i)
            set ok = GetPlayerTechMaxAllowed(lp, hid) != 0
            call BlzFrameSetVisible(b, true)
            call BlzFrameSetEnable(b, ok)
            if ok then
                call BlzFrameSetAlpha(BlzGetFrameByName("ScoreScreenButtonBackdrop", 7400 + i), 255)
            else
                call BlzFrameSetAlpha(BlzGetFrameByName("ScoreScreenButtonBackdrop", 7400 + i), 60)
            endif
            set col = col + 1
        else
            call BlzFrameSetVisible(b, false)
        endif
        set i = i + 1
    endloop
    call BlzFrameSetSize(board, 0.56, 0.11 + (row + 1) * 0.042)

    if udg_ModeRandom then
        set hint = "|cffffcc00올랜덤|r: |cffffcc00-랜덤|r 으로만 선택할 수 있습니다.  "
    elseif udg_Mode3P2R then
        set hint = "|cffffcc003픽 2랜덤|r: 팀당 3명까지 직접 선택, 나머지는 |cffffcc00-랜덤|r  "
    endif
    set hint = hint + "흐린 영웅은 선택 불가(선택됨/밴/모드 제한).  |cffffcc00-랜덤|r 무작위  |cffffcc00-보드|r 다시 열기  |cff999999상점 마감 " + I2S(R2I(120.0 - TimerGetElapsed(udg_MBTime))) + "초|r"
    call BlzFrameSetText(BlzGetFrameByName("GSPF_Hint", 0), hint)
    set b = null
    set board = null
    set lp = null
endfunction

//--- 확정 --------------------------------------------------------------------
function GSPF_Confirm takes nothing returns nothing
    local string msg = ""
    if GSPF_GetState("GSPF_Done") == "1" then
        return
    endif
    call GSPF_SetState("GSPF_Done", "1")
    call BlzFrameSetVisible(BlzGetFrameByName("EscMenuBackdrop", 7001), false)
    call BlzFrameSetVisible(BlzGetFrameByName("GSPF_Wait", 0), false)

    // 기존 모드 트리거를 그대로 실행 (이미 켜진 모드는 건너뜀)
    if GSPF_Sel(2) and not udg_ModeSP then
        call TriggerExecute(gg_trg_Mode_HS)
    elseif GSPF_Sel(1) and not udg_ModeSP then
        call TriggerExecute(gg_trg_Mode_SP)
    endif
    if GSPF_Sel(0) and not udg_ModeAllpick then
        call TriggerExecute(gg_trg_Mode_AP)
    endif
    if GSPF_Sel(3) and not udg_ModeRandom and not udg_Mode3P2R then
        call TriggerExecute(gg_trg_Mode_AR)
    elseif GSPF_Sel(4) and not udg_ModeRandom and not udg_Mode3P2R then
        call TriggerExecute(gg_trg_Mode_PR)
    endif
    if GSPF_Sel(5) and not IsTriggerEnabled(gg_trg_Damage_Test) then
        call TriggerExecute(gg_trg_Mode_DG)
    endif
    call DisplayTimedTextToPlayer(GetLocalPlayer(), 0, 0, 10, "|cffffcc00게임 모드 확정|r - 영웅 선택 보드가 열립니다.")
    call TimerStart(CreateTimer(), 0.25, true, function GSPF_BoardTick)
endfunction

function GSPF_ModeTick takes nothing returns nothing
    local integer left = S2I(GSPF_GetState("GSPF_Left")) - 1
    local integer host = GSPF_HostId()
    if GSPF_GetState("GSPF_Done") == "1" then
        call DestroyTimer(GetExpiredTimer())
        return
    endif
    call GSPF_SetState("GSPF_Left", I2S(left))
    if host < 0 or not GSPF_IsUser(Player(host)) or left <= 0 then
        call DestroyTimer(GetExpiredTimer())
        call GSPF_Confirm()
        return
    endif
    call GSPF_RefreshModes()
    call BlzFrameSetText(BlzGetFrameByName("ScriptDialogButton", 7200), "확정  |cff999999(" + I2S(left) + ")|r")
    call BlzFrameSetText(BlzGetFrameByName("GSPF_Wait", 0), "|cffffcc00" + GetPlayerName(Player(host)) + "|r 님이 게임 모드를 선택하고 있습니다...  |cff999999" + I2S(left) + "초|r")
endfunction

//--- 클릭 처리 (네트워크 동기 이벤트) ----------------------------------------
function GSPF_DropFocus takes framehandle f returns nothing
    if GetTriggerPlayer() == GetLocalPlayer() then
        call BlzFrameSetEnable(f, false)
        call BlzFrameSetEnable(f, true)
    endif
endfunction

function GSPF_OnModeClick takes nothing returns nothing
    local framehandle f = BlzGetTriggerFrame()
    local integer k = 0
    call GSPF_DropFocus(f)
    if GetPlayerId(GetTriggerPlayer()) != GSPF_HostId() or GSPF_GetState("GSPF_Done") == "1" then
        set f = null
        return
    endif
    if f == BlzGetFrameByName("ScriptDialogButton", 7200) then
        set f = null
        call GSPF_Confirm()
        return
    endif
    loop
        exitwhen k > 5
        if f == BlzGetFrameByName("ScriptDialogButton", 7100 + k) and not GSPF_ModeBlocked(k) then
            call GSPF_SetSel(k, not GSPF_Sel(k))
        endif
        set k = k + 1
    endloop
    call GSPF_RefreshModes()
    set f = null
endfunction

function GSPF_OnHeroClick takes nothing returns nothing
    local framehandle f = BlzGetTriggerFrame()
    local player p = GetTriggerPlayer()
    local integer i = 0
    local integer n = -1
    local integer hid
    local unit shop
    local unit buyer
    call GSPF_DropFocus(f)
    loop
        exitwhen i >= GSPF_HeroCount() or n >= 0
        if f == BlzGetFrameByName("ScoreScreenBottomButtonTemplate", 7400 + i) then
            set n = i
        endif
        set i = i + 1
    endloop
    set f = null
    if n < 0 then
        set p = null
        return
    endif
    set hid = GSPF_HeroAt(n)
    set shop = GSPF_Shop(GSPF_GroupOf(n))
    if GetUnitTypeId(udg_HeroPlayer[GetPlayerId(p) + 1]) != 0 or not GSPF_ShopsAlive() then
        set shop = null
        set p = null
        return
    endif
    if not GSPF_RowVisible(GSPF_GroupOf(n), p) or GetPlayerTechMaxAllowed(p, hid) == 0 then
        call DisplayTimedTextToPlayer(p, 0, 0, 5, "|cffff8080선택할 수 없는 영웅입니다.|r")
        set shop = null
        set p = null
        return
    endif
    // 상점 옆에 구매용 유닛을 잠깐 만들고, 기존 상점 구매 주문을 냄 -> Select Hero 트리거가 처리
    set buyer = CreateUnit(p, 'e003', GetUnitX(shop), GetUnitY(shop) - 64.0, 270.0)
    call UnitApplyTimedLife(buyer, 'BTLF', 2.0)
    call IssueNeutralImmediateOrderById(p, shop, hid)
    call TriggerSleepAction(1.0)
    if GetUnitTypeId(udg_HeroPlayer[GetPlayerId(p) + 1]) == 0 then
        call DisplayTimedTextToPlayer(p, 0, 0, 8, "|cffff8080보드 구매 실패|r - 상점(정령)에서 직접 구매해 주세요.")
    endif
    set shop = null
    set buyer = null
    set p = null
endfunction

function GSPF_OnBoardCmd takes nothing returns nothing
    local framehandle f = BlzGetTriggerFrame()
    if GetTriggerPlayer() == GetLocalPlayer() then
        if GetTriggerEventId() == EVENT_PLAYER_CHAT then
            call GSPF_SetState("GSPF_Closed", "0")
        else
            call BlzFrameSetEnable(f, false)
            call BlzFrameSetEnable(f, true)
            call GSPF_SetState("GSPF_Closed", "1")
        endif
    endif
    set f = null
endfunction

//--- 생성 --------------------------------------------------------------------
function GSPF_Hidden takes string name, framehandle parent, string v returns nothing
    local framehandle f = BlzCreateFrameByType("TEXT", name, parent, "", 0)
    call BlzFrameSetVisible(f, false)
    call BlzFrameSetText(f, v)
    set f = null
endfunction

function GSPF_Text takes string name, integer ctx, framehandle parent, real w, real h returns framehandle
    local framehandle f = BlzCreateFrameByType("TEXT", name, parent, "", ctx)
    call BlzFrameSetSize(f, w, h)
    call BlzFrameSetEnable(f, false)
    return f
endfunction

function GSPF_Create takes nothing returns nothing
    local framehandle ui = BlzGetOriginFrame(ORIGIN_FRAME_GAME_UI, 0)
    local framehandle box
    local framehandle f
    local framehandle g
    local trigger tm = CreateTrigger()
    local trigger th = CreateTrigger()
    local trigger tb = CreateTrigger()
    local integer k = 0
    local integer host = GSPF_FindHost()
    call DestroyTimer(GetExpiredTimer())

    // 공유 상태
    call GSPF_Hidden("GSPF_Host", ui, I2S(host))
    call GSPF_Hidden("GSPF_Sel", ui, "000000")
    call GSPF_Hidden("GSPF_Done", ui, "0")
    call GSPF_Hidden("GSPF_Left", ui, I2S(GSPF_ModeTimeout() + 1))
    call GSPF_Hidden("GSPF_Closed", ui, "0")

    // 모드 팝업 (1픽에게만 보임)
    set box = BlzCreateFrame("EscMenuBackdrop", ui, 0, 7001)
    call BlzFrameSetSize(box, 0.34, 0.33)
    call BlzFrameSetAbsPoint(box, FRAMEPOINT_CENTER, 0.4, 0.36)
    set f = GSPF_Text("GSPF_ModeTitle", 0, box, 0.30, 0.02)
    call BlzFrameSetPoint(f, FRAMEPOINT_TOP, box, FRAMEPOINT_TOP, 0.0, -0.022)
    call BlzFrameSetTextAlignment(f, TEXT_JUSTIFY_MIDDLE, TEXT_JUSTIFY_CENTER)
    call BlzFrameSetText(f, "|cffffcc00게임 모드 선택|r")
    set f = GSPF_Text("GSPF_ModeSub", 0, box, 0.30, 0.014)
    call BlzFrameSetPoint(f, FRAMEPOINT_TOP, box, FRAMEPOINT_TOP, 0.0, -0.044)
    call BlzFrameSetTextAlignment(f, TEXT_JUSTIFY_MIDDLE, TEXT_JUSTIFY_CENTER)
    call BlzFrameSetText(f, "|cff999999여러 개 선택 가능 / 같이 켤 수 없는 모드는 자동 잠금|r")
    loop
        exitwhen k > 5
        set f = BlzCreateFrame("ScriptDialogButton", box, 0, 7100 + k)
        call BlzFrameSetSize(f, 0.30, 0.031)
        call BlzFrameSetPoint(f, FRAMEPOINT_TOP, box, FRAMEPOINT_TOP, 0.0, -0.064 - k * 0.034)
        call BlzTriggerRegisterFrameEvent(tm, f, FRAMEEVENT_CONTROL_CLICK)
        set k = k + 1
    endloop
    set f = BlzCreateFrame("ScriptDialogButton", box, 0, 7200)
    call BlzFrameSetSize(f, 0.15, 0.034)
    call BlzFrameSetPoint(f, FRAMEPOINT_BOTTOM, box, FRAMEPOINT_BOTTOM, 0.0, 0.02)
    call BlzTriggerRegisterFrameEvent(tm, f, FRAMEEVENT_CONTROL_CLICK)
    call TriggerAddAction(tm, function GSPF_OnModeClick)
    call BlzFrameSetVisible(box, GetPlayerId(GetLocalPlayer()) == host)

    // 다른 플레이어 안내 문구
    set f = GSPF_Text("GSPF_Wait", 0, ui, 0.5, 0.02)
    call BlzFrameSetAbsPoint(f, FRAMEPOINT_TOP, 0.4, 0.5)
    call BlzFrameSetTextAlignment(f, TEXT_JUSTIFY_MIDDLE, TEXT_JUSTIFY_CENTER)
    call BlzFrameSetVisible(f, GetPlayerId(GetLocalPlayer()) != host)

    // 영웅 보드 (확정 전까지 숨김)
    set box = BlzCreateFrame("EscMenuBackdrop", ui, 0, 7002)
    call BlzFrameSetSize(box, 0.56, 0.24)
    call BlzFrameSetAbsPoint(box, FRAMEPOINT_TOP, 0.4, 0.555)
    set f = GSPF_Text("GSPF_BoardTitle", 0, box, 0.4, 0.02)
    call BlzFrameSetPoint(f, FRAMEPOINT_TOPLEFT, box, FRAMEPOINT_TOPLEFT, 0.022, -0.022)
    call BlzFrameSetText(f, "|cffffcc00영웅 선택|r  |cff999999아이콘 클릭 = 상점에서 구매|r")
    set f = GSPF_Text("GSPF_Hint", 0, box, 0.52, 0.03)
    call BlzFrameSetPoint(f, FRAMEPOINT_BOTTOMLEFT, box, FRAMEPOINT_BOTTOMLEFT, 0.022, 0.018)
    call BlzFrameSetScale(f, 0.9)
    set f = BlzCreateFrame("ScriptDialogButton", box, 0, 7300)
    call BlzFrameSetSize(f, 0.07, 0.028)
    call BlzFrameSetPoint(f, FRAMEPOINT_TOPRIGHT, box, FRAMEPOINT_TOPRIGHT, -0.018, -0.016)
    call BlzFrameSetText(f, "닫기")
    call BlzTriggerRegisterFrameEvent(tb, f, FRAMEEVENT_CONTROL_CLICK)
    set k = 0
    loop
        exitwhen k > 5
        set f = GSPF_Text("GSPF_RowLbl", k, box, 0.066, 0.034)
        call BlzFrameSetTextAlignment(f, TEXT_JUSTIFY_MIDDLE, TEXT_JUSTIFY_LEFT)
        call BlzFrameSetText(f, GSPF_GroupLabel(k))
        set k = k + 1
    endloop
    set k = 0
    loop
        exitwhen k >= GSPF_HeroCount()
        set f = BlzCreateFrame("ScoreScreenBottomButtonTemplate", box, 0, 7400 + k)
        call BlzFrameSetSize(f, 0.034, 0.034)
        call BlzFrameSetTexture(BlzGetFrameByName("ScoreScreenButtonBackdrop", 7400 + k), BlzGetAbilityIcon(GSPF_HeroAt(k)), 0, true)
        call BlzTriggerRegisterFrameEvent(th, f, FRAMEEVENT_CONTROL_CLICK)
        // 툴팁: 영웅 이름
        set g = BlzCreateFrameByType("BACKDROP", "GSPF_Tip", f, "", 7400 + k)
        call BlzFrameSetTexture(g, "Textures\\Black32.blp", 0, true)
        call BlzFrameSetAlpha(g, 220)
        call BlzFrameSetSize(g, 0.12, 0.022)
        call BlzFrameSetPoint(g, FRAMEPOINT_BOTTOM, f, FRAMEPOINT_TOP, 0.0, 0.004)
        call BlzFrameSetTooltip(f, g)
        set g = GSPF_Text("GSPF_TipText", 7400 + k, g, 0.12, 0.022)
        call BlzFrameSetPoint(g, FRAMEPOINT_CENTER, BlzGetFrameByName("GSPF_Tip", 7400 + k), FRAMEPOINT_CENTER, 0.0, 0.0)
        call BlzFrameSetTextAlignment(g, TEXT_JUSTIFY_MIDDLE, TEXT_JUSTIFY_CENTER)
        call BlzFrameSetText(g, GetObjectName(GSPF_HeroAt(k)))
        set k = k + 1
    endloop
    call TriggerAddAction(th, function GSPF_OnHeroClick)
    call BlzFrameSetVisible(box, false)

    // -보드 : 보드 다시 열기 / 닫기 버튼
    set k = 0
    loop
        exitwhen k > 11
        call TriggerRegisterPlayerChatEvent(tb, Player(k), "-보드", true)
        call TriggerRegisterPlayerChatEvent(tb, Player(k), "-board", true)
        set k = k + 1
    endloop
    call TriggerAddAction(tb, function GSPF_OnBoardCmd)

    call GSPF_RefreshModes()
    if host < 0 then
        call GSPF_Confirm()
    else
        call GSPF_ModeTick()
        call TimerStart(CreateTimer(), 1.0, true, function GSPF_ModeTick)
    endif
    set ui = null
    set box = null
    set f = null
    set g = null
    set tm = null
    set th = null
    set tb = null
endfunction

function GSPF_Init takes nothing returns nothing
    // 영웅 목록(Set Variable Hero, 1초)과 위습 지급(Initialize, 1초) 이후에 시작
    call TimerStart(CreateTimer(), 2.5, false, function GSPF_Create)
endfunction
