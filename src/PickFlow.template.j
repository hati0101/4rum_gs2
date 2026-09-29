//===========================================================================
// GSPF: 게임 시작 흐름
//   1) 게임을 일시정지하고 1픽(Player 1, 없으면 가디언 첫 유저)에게 모드 선택 팝업
//      - 같이 켤 수 없는 모드는 자동 잠금, 기존 명령어 표기
//      - 확정하면 게임 재개 + 기존 모드 트리거(Mode_AP 등)를 그대로 실행
//      - 잠수 대비: 다른 플레이어 절반 이상이 "진행 투표"하면 모드 없이 진행,
//        1픽이 나가면 바로 진행 (일시정지 중에는 타이머가 멈춰서 시간제한 불가)
//   2) 확정 직후 모두에게 영웅 선택 화면 (왼쪽 가디언 / 오른쪽 다크니스, 힘·민첩·지능)
//      - 클릭 = 기존 상점(정령)에서 구매 (중복/밴/3P2R/올픽 규칙 그대로 적용)
//      - 영웅은 상점 재고 시작 지연(15초) 뒤부터 팔리므로, 그때까지 아이콘에 쿨다운 표시 + 클릭 불가
//      - 선택하면 닫힘, 상점이 사라지는 120초에 모두 닫힘, -보드 로 다시 열기
//
//   사용법: 맵 초기화 트리거에 사용자 지정 스크립트  call GSPF_Init()
//   전역 변수 없음: 공유 상태는 숨긴 TEXT 프레임에 저장 (모든 클라이언트가 동기 코드에서
//   같은 값으로 갱신), 버튼 클릭 이벤트는 네트워크 동기화됨
//===========================================================================

//@@PICK_TABLE@@

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

// 문자열 상태의 k번째 글자를 on/off
function GSPF_Bit takes string name, integer k returns boolean
    return SubString(GSPF_GetState(name), k, k + 1) == "1"
endfunction

function GSPF_SetBit takes string name, integer k, boolean on returns nothing
    local string s = GSPF_GetState(name)
    local string c = "0"
    if on then
        set c = "1"
    endif
    call GSPF_SetState(name, SubString(s, 0, k) + c + SubString(s, k + 1, StringLength(s)))
endfunction

//--- 화면 부품 ---------------------------------------------------------------
function GSPF_Text takes string name, integer ctx, framehandle parent, real w, real h returns framehandle
    local framehandle f = BlzCreateFrameByType("TEXT", name, parent, "", ctx)
    call BlzFrameSetSize(f, w, h)
    call BlzFrameSetEnable(f, false)
    return f
endfunction

// 불투명 검정 배경 + 메뉴 테두리 + 뒤쪽 클릭 차단
function GSPF_Panel takes string name, integer ctx, real w, real h returns framehandle
    local framehandle bg = BlzCreateFrameByType("BACKDROP", name, BlzGetOriginFrame(ORIGIN_FRAME_GAME_UI, 0), "", 0)
    local framehandle f
    call BlzFrameSetSize(bg, w, h)
    call BlzFrameSetTexture(bg, "Textures\\Black32.blp", 0, true)
    set f = BlzCreateFrameByType("GLUEBUTTON", name + "Block", bg, "", 0)
    call BlzFrameSetAllPoints(f, bg)
    set f = BlzCreateFrame("EscMenuBackdrop", bg, 0, ctx)
    call BlzFrameSetAllPoints(f, bg)
    set f = null
    return bg
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

function GSPF_ModeShort takes integer k returns string
    if k == 0 then
        return "올픽"
    elseif k == 1 then
        return "팀 섞기"
    elseif k == 2 then
        return "익명 팀 섞기"
    elseif k == 3 then
        return "올랜덤"
    elseif k == 4 then
        return "3픽 2랜덤"
    endif
    return "데미지 표시"
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

// 켜져 있는지 (채팅 명령어로 켠 경우 포함)
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

function GSPF_ModeBlocked takes integer k returns boolean
    local integer r = GSPF_ModeRival(k)
    if GSPF_ModeActive(k) then
        return true
    endif
    return r >= 0 and (GSPF_Bit("GSPF_Sel", r) or GSPF_ModeActive(r))
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
        elseif GSPF_Bit("GSPF_Sel", k) then
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

// 진행 투표: 1픽 제외 유저 절반 이상
function GSPF_RefreshVote takes nothing returns boolean
    local integer i = 0
    local integer users = 0
    local integer votes = 0
    local integer host = GSPF_HostId()
    loop
        exitwhen i > 11
        if i != host and GSPF_IsUser(Player(i)) then
            set users = users + 1
            if GSPF_Bit("GSPF_Votes", i) then
                set votes = votes + 1
            endif
        endif
        set i = i + 1
    endloop
    call BlzFrameSetText(BlzGetFrameByName("ScriptDialogButton", 7250), "진행 투표  |cff999999(" + I2S(votes) + " / " + I2S((users + 1) / 2) + ")|r")
    return users > 0 and votes * 2 >= users
endfunction

//--- 영웅 선택 화면 ----------------------------------------------------------
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

// 그룹 g(0~2 가디언, 3~5 다크니스)를 플레이어 p가 고를 수 있는 진영인지
function GSPF_SideAllowed takes integer g, player p returns boolean
    return udg_ModeAllpick or ((g < 3) == IsPlayerAlly(p, udg_Force[1]))
endfunction

// 영웅은 상점 재고 시작 지연(15초, 게임 시간) 이후부터 살 수 있음
function GSPF_StockReady takes nothing returns boolean
    return TimerGetElapsed(udg_MBTime) >= 15.5
endfunction

// 고를 수 있는지 확인 후 기존 상점 구매 주문 (true = 주문 냄)
function GSPF_TryBuy takes player p, integer n returns boolean
    local integer hid = GSPF_HeroAt(n)
    local unit shop = GSPF_Shop(GSPF_GroupOf(n))
    local unit buyer
    if GetUnitTypeId(udg_HeroPlayer[GetPlayerId(p) + 1]) != 0 or not GSPF_ShopsAlive() then
        set shop = null
        return false
    endif
    if not GSPF_SideAllowed(GSPF_GroupOf(n), p) or GetPlayerTechMaxAllowed(p, hid) == 0 then
        call DisplayTimedTextToPlayer(p, 0, 0, 6, "|cffff8080" + GetObjectName(hid) + " 은(는) 선택할 수 없습니다|r (이미 선택됨/밴/모드 제한). 다른 영웅을 골라 주세요.")
        set shop = null
        return false
    endif
    // 상점 옆에 구매용 유닛을 잠깐 만들고 상점 구매 주문 -> Select Hero 트리거가 처리
    set buyer = CreateUnit(p, 'e003', GetUnitX(shop), GetUnitY(shop) - 64.0, 270.0)
    call UnitApplyTimedLife(buyer, 'BTLF', 2.0)
    call IssueNeutralImmediateOrderById(p, shop, hid)
    set shop = null
    set buyer = null
    return true
endfunction

function GSPF_BoardTick takes nothing returns nothing
    local player lp = GetLocalPlayer()
    local integer lpid = GetPlayerId(lp)
    local framehandle board = BlzGetFrameByName("GSPF_Board", 0)
    local framehandle b
    local framehandle cd
    local integer i = 0
    local integer k = 0
    local integer hid
    local boolean ok
    local real rem
    local string s = ""

    // --- 동기 처리 (모든 클라이언트에서 똑같이 실행) ---
    if not GSPF_ShopsAlive() then
        call BlzFrameSetVisible(board, false)
        call DestroyTimer(GetExpiredTimer())
        set board = null
        set lp = null
        return
    endif

    // --- 로컬 화면 갱신 (프레임만 조작 -> 디싱크 없음) ---
    call BlzFrameSetVisible(board, GSPF_IsUser(lp) and GetUnitTypeId(udg_HeroPlayer[lpid + 1]) == 0 and GSPF_GetState("GSPF_Closed") != "1")
    if not BlzFrameIsVisible(board) then
        set board = null
        set lp = null
        return
    endif

    set rem = 15.5 - TimerGetElapsed(udg_MBTime)
    if rem <= 0.0 then
        call BlzFrameSetText(BlzGetFrameByName("GSPF_BoardTitle", 0), "|cffffcc00영웅 선택|r   |cff999999아이콘 클릭 = 구매 / 마우스를 올리면 이름|r")
    else
        call BlzFrameSetText(BlzGetFrameByName("GSPF_BoardTitle", 0), "|cffffcc00영웅 선택|r   영웅 판매 준비 중 |cffffcc00" + I2S(R2I(rem) + 1) + "초|r")
    endif
    loop
        exitwhen k > 1
        if GSPF_SideAllowed(k * 3, lp) then
            call BlzFrameSetText(BlzGetFrameByName("GSPF_SideLbl", k), GSPF_SideName(k))
        else
            call BlzFrameSetText(BlzGetFrameByName("GSPF_SideLbl", k), GSPF_SideName(k) + "  |cff808080(상대 진영 - 올픽일 때만 선택)|r")
        endif
        set k = k + 1
    endloop
    loop
        exitwhen i >= GSPF_HeroCount()
        set hid = GSPF_HeroAt(i)
        set ok = GSPF_SideAllowed(GSPF_GroupOf(i), lp) and GetPlayerTechMaxAllowed(lp, hid) != 0
        set b = BlzGetFrameByName("ScoreScreenBottomButtonTemplate", 7400 + i)
        call BlzFrameSetEnable(b, ok and rem <= 0.0)
        if ok then
            call BlzFrameSetAlpha(BlzGetFrameByName("ScoreScreenButtonBackdrop", 7400 + i), 255)
        else
            call BlzFrameSetAlpha(BlzGetFrameByName("ScoreScreenButtonBackdrop", 7400 + i), 55)
        endif
        // 쿨다운 막: 남은 비율만큼 위에서부터 덮음
        set cd = BlzGetFrameByName("GSPF_Cd", 7400 + i)
        if ok and rem > 0.05 then
            call BlzFrameSetSize(cd, 0.046, 0.046 * RMinBJ(rem / 15.5, 1.0))
            call BlzFrameSetVisible(cd, true)
            call BlzFrameSetText(BlzGetFrameByName("GSPF_CdText", 7400 + i), "|cffffffff" + I2S(R2I(rem) + 1) + "|r")
        else
            call BlzFrameSetVisible(cd, false)
            call BlzFrameSetText(BlzGetFrameByName("GSPF_CdText", 7400 + i), "")
        endif
        set i = i + 1
    endloop

    set k = 0
    loop
        exitwhen k > 5
        if GSPF_ModeActive(k) then
            if s != "" then
                set s = s + ", "
            endif
            set s = s + GSPF_ModeShort(k)
        endif
        set k = k + 1
    endloop
    if s == "" then
        set s = "기본"
    endif
    set s = "모드: |cffffcc00" + s + "|r     "
    if udg_ModeRandom then
        set s = s + "|cffffcc00-랜덤|r 으로만 선택 가능     "
    elseif udg_Mode3P2R then
        set s = s + "팀당 3명까지 직접 선택, 나머지는 |cffffcc00-랜덤|r     "
    else
        set s = s + "|cffffcc00-랜덤|r 무작위     "
    endif
    set s = s + "|cffffcc00-보드|r 다시 열기     상점 마감까지 |cffffcc00" + I2S(R2I(120.0 - TimerGetElapsed(udg_MBTime))) + "초|r"
    call BlzFrameSetText(BlzGetFrameByName("GSPF_Hint", 0), s)
    set b = null
    set cd = null
    set board = null
    set lp = null
endfunction

//--- 확정 --------------------------------------------------------------------
function GSPF_Confirm takes nothing returns nothing
    if GSPF_GetState("GSPF_Done") == "1" then
        return
    endif
    call GSPF_SetState("GSPF_Done", "1")
    call BlzFrameSetVisible(BlzGetFrameByName("GSPF_ModeBox", 0), false)
    call BlzFrameSetVisible(BlzGetFrameByName("GSPF_WaitBox", 0), false)
    call PauseGame(false)

    // 기존 모드 트리거를 그대로 실행 (이미 켜진 모드는 건너뜀)
    if GSPF_Bit("GSPF_Sel", 2) and not udg_ModeSP then
        call TriggerExecute(gg_trg_Mode_HS)
    elseif GSPF_Bit("GSPF_Sel", 1) and not udg_ModeSP then
        call TriggerExecute(gg_trg_Mode_SP)
    endif
    if GSPF_Bit("GSPF_Sel", 0) and not udg_ModeAllpick then
        call TriggerExecute(gg_trg_Mode_AP)
    endif
    if GSPF_Bit("GSPF_Sel", 3) and not udg_ModeRandom and not udg_Mode3P2R then
        call TriggerExecute(gg_trg_Mode_AR)
    elseif GSPF_Bit("GSPF_Sel", 4) and not udg_ModeRandom and not udg_Mode3P2R then
        call TriggerExecute(gg_trg_Mode_PR)
    endif
    if GSPF_Bit("GSPF_Sel", 5) and not IsTriggerEnabled(gg_trg_Damage_Test) then
        call TriggerExecute(gg_trg_Mode_DG)
    endif
    call DisplayTimedTextToPlayer(GetLocalPlayer(), 0, 0, 10, "|cffffcc00게임 모드 확정|r - 게임을 시작합니다.")
    call GSPF_BoardTick()
    call TimerStart(CreateTimer(), 0.1, true, function GSPF_BoardTick)
endfunction

//--- 이벤트 (버튼 클릭은 네트워크 동기화됨) ---------------------------------
function GSPF_DropFocus takes framehandle f returns nothing
    if GetTriggerPlayer() == GetLocalPlayer() then
        call BlzFrameSetEnable(f, false)
        call BlzFrameSetEnable(f, true)
    endif
endfunction

function GSPF_OnModeClick takes nothing returns nothing
    local framehandle f = BlzGetTriggerFrame()
    local integer pid = GetPlayerId(GetTriggerPlayer())
    local integer k = 0
    call GSPF_DropFocus(f)
    if GSPF_GetState("GSPF_Done") == "1" then
        set f = null
        return
    endif
    if f == BlzGetFrameByName("ScriptDialogButton", 7250) then
        // 진행 투표 (1픽 외)
        if pid != GSPF_HostId() then
            call GSPF_SetBit("GSPF_Votes", pid, true)
            if GSPF_RefreshVote() then
                call DisplayTimedTextToPlayer(GetLocalPlayer(), 0, 0, 10, "진행 투표 통과 - 모드 없이 진행합니다.")
                call GSPF_SetState("GSPF_Sel", "000000")
                call GSPF_Confirm()
            endif
        endif
        set f = null
        return
    endif
    if pid != GSPF_HostId() then
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
            call GSPF_SetBit("GSPF_Sel", k, not GSPF_Bit("GSPF_Sel", k))
        endif
        set k = k + 1
    endloop
    call GSPF_RefreshModes()
    set f = null
endfunction

function GSPF_OnLeave takes nothing returns nothing
    if GSPF_GetState("GSPF_Done") == "1" then
        return
    endif
    if GetPlayerId(GetTriggerPlayer()) == GSPF_HostId() then
        call DisplayTimedTextToPlayer(GetLocalPlayer(), 0, 0, 10, "1픽이 나가서 모드 없이 진행합니다.")
        call GSPF_SetState("GSPF_Sel", "000000")
        call GSPF_Confirm()
    else
        call GSPF_RefreshVote()
    endif
endfunction

function GSPF_OnHeroClick takes nothing returns nothing
    local framehandle f = BlzGetTriggerFrame()
    local player p = GetTriggerPlayer()
    local integer pid = GetPlayerId(p)
    local integer i = 0
    local integer n = -1
    call GSPF_DropFocus(f)
    loop
        exitwhen i >= GSPF_HeroCount() or n >= 0
        if f == BlzGetFrameByName("ScoreScreenBottomButtonTemplate", 7400 + i) then
            set n = i
        endif
        set i = i + 1
    endloop
    set f = null
    if n < 0 or GetUnitTypeId(udg_HeroPlayer[pid + 1]) != 0 then
        set p = null
        return
    endif
    // 판매 시작 전(쿨다운 중)에는 버튼이 비활성이지만, 혹시 들어온 클릭은 무시
    if not GSPF_StockReady() then
        set p = null
        return
    endif
    if GSPF_TryBuy(p, n) then
        call TriggerSleepAction(1.0)
        if GetUnitTypeId(udg_HeroPlayer[pid + 1]) == 0 then
            call DisplayTimedTextToPlayer(p, 0, 0, 8, "|cffff8080구매 실패|r - 상점(정령)에서 직접 구매해 주세요.")
        endif
    endif
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
function GSPF_Hidden takes string name, string v returns nothing
    local framehandle f = BlzCreateFrameByType("TEXT", name, BlzGetOriginFrame(ORIGIN_FRAME_GAME_UI, 0), "", 0)
    call BlzFrameSetVisible(f, false)
    call BlzFrameSetText(f, v)
    set f = null
endfunction

function GSPF_CreateModeBox takes integer host returns nothing
    local framehandle box = GSPF_Panel("GSPF_ModeBox", 7001, 0.36, 0.35)
    local framehandle f
    local trigger t = CreateTrigger()
    local integer k = 0
    call BlzFrameSetAbsPoint(box, FRAMEPOINT_CENTER, 0.4, 0.36)
    set f = GSPF_Text("GSPF_ModeTitle", 0, box, 0.32, 0.02)
    call BlzFrameSetPoint(f, FRAMEPOINT_TOP, box, FRAMEPOINT_TOP, 0.0, -0.024)
    call BlzFrameSetTextAlignment(f, TEXT_JUSTIFY_MIDDLE, TEXT_JUSTIFY_CENTER)
    call BlzFrameSetText(f, "|cffffcc00게임 모드 선택|r  |cff999999(게임 일시정지 중)|r")
    set f = GSPF_Text("GSPF_ModeSub", 0, box, 0.32, 0.014)
    call BlzFrameSetPoint(f, FRAMEPOINT_TOP, box, FRAMEPOINT_TOP, 0.0, -0.046)
    call BlzFrameSetTextAlignment(f, TEXT_JUSTIFY_MIDDLE, TEXT_JUSTIFY_CENTER)
    call BlzFrameSetText(f, "|cff999999여러 개 선택 가능 / 같이 켤 수 없는 모드는 자동 잠금|r")
    loop
        exitwhen k > 5
        set f = BlzCreateFrame("ScriptDialogButton", box, 0, 7100 + k)
        call BlzFrameSetSize(f, 0.31, 0.032)
        call BlzFrameSetPoint(f, FRAMEPOINT_TOP, box, FRAMEPOINT_TOP, 0.0, -0.068 - k * 0.035)
        call BlzTriggerRegisterFrameEvent(t, f, FRAMEEVENT_CONTROL_CLICK)
        set k = k + 1
    endloop
    set f = BlzCreateFrame("ScriptDialogButton", box, 0, 7200)
    call BlzFrameSetSize(f, 0.16, 0.036)
    call BlzFrameSetPoint(f, FRAMEPOINT_BOTTOM, box, FRAMEPOINT_BOTTOM, 0.0, 0.022)
    call BlzFrameSetText(f, "|cffffcc00확정하고 게임 시작|r")
    call BlzTriggerRegisterFrameEvent(t, f, FRAMEEVENT_CONTROL_CLICK)
    call BlzFrameSetVisible(box, GetPlayerId(GetLocalPlayer()) == host)

    // 다른 플레이어: 안내 + 진행 투표
    set box = GSPF_Panel("GSPF_WaitBox", 7003, 0.42, 0.1)
    call BlzFrameSetAbsPoint(box, FRAMEPOINT_CENTER, 0.4, 0.4)
    set f = GSPF_Text("GSPF_Wait", 0, box, 0.38, 0.02)
    call BlzFrameSetPoint(f, FRAMEPOINT_TOP, box, FRAMEPOINT_TOP, 0.0, -0.022)
    call BlzFrameSetTextAlignment(f, TEXT_JUSTIFY_MIDDLE, TEXT_JUSTIFY_CENTER)
    call BlzFrameSetText(f, "|cffffcc00" + GetPlayerName(Player(host)) + "|r 님이 게임 모드를 선택하고 있습니다  |cff999999(일시정지)|r")
    set f = BlzCreateFrame("ScriptDialogButton", box, 0, 7250)
    call BlzFrameSetSize(f, 0.2, 0.032)
    call BlzFrameSetPoint(f, FRAMEPOINT_BOTTOM, box, FRAMEPOINT_BOTTOM, 0.0, 0.018)
    call BlzTriggerRegisterFrameEvent(t, f, FRAMEEVENT_CONTROL_CLICK)
    call BlzFrameSetVisible(box, GetPlayerId(GetLocalPlayer()) != host)
    call TriggerAddAction(t, function GSPF_OnModeClick)

    set t = CreateTrigger()
    set k = 0
    loop
        exitwhen k > 11
        call TriggerRegisterPlayerEvent(t, Player(k), EVENT_PLAYER_LEAVE)
        set k = k + 1
    endloop
    call TriggerAddAction(t, function GSPF_OnLeave)
    set box = null
    set f = null
    set t = null
endfunction

function GSPF_CreateBoard takes nothing returns nothing
    local framehandle box = GSPF_Panel("GSPF_Board", 7002, 0.78, 0.43)
    local framehandle f
    local framehandle g
    local trigger th = CreateTrigger()
    local trigger tb = CreateTrigger()
    local integer k = 0
    local integer i
    local integer grp
    local integer j = 0
    local integer last = -1
    local real x
    call BlzFrameSetAbsPoint(box, FRAMEPOINT_CENTER, 0.4, 0.36)
    set f = GSPF_Text("GSPF_BoardTitle", 0, box, 0.6, 0.02)
    call BlzFrameSetPoint(f, FRAMEPOINT_TOP, box, FRAMEPOINT_TOP, 0.0, -0.02)
    call BlzFrameSetTextAlignment(f, TEXT_JUSTIFY_MIDDLE, TEXT_JUSTIFY_CENTER)
    set f = BlzCreateFrame("ScriptDialogButton", box, 0, 7300)
    call BlzFrameSetSize(f, 0.07, 0.028)
    call BlzFrameSetPoint(f, FRAMEPOINT_TOPRIGHT, box, FRAMEPOINT_TOPRIGHT, -0.016, -0.014)
    call BlzFrameSetText(f, "닫기")
    call BlzTriggerRegisterFrameEvent(tb, f, FRAMEEVENT_CONTROL_CLICK)

    // 진영 제목 (왼쪽 가디언 / 오른쪽 다크니스), 그룹 제목 (힘 / 민첩 / 지능)
    loop
        exitwhen k > 1
        set f = GSPF_Text("GSPF_SideLbl", k, box, 0.37, 0.018)
        call BlzFrameSetPoint(f, FRAMEPOINT_TOPLEFT, box, FRAMEPOINT_TOPLEFT, 0.024 + k * 0.385, -0.044)
        call BlzFrameSetTextAlignment(f, TEXT_JUSTIFY_MIDDLE, TEXT_JUSTIFY_LEFT)
        set k = k + 1
    endloop
    set k = 0
    loop
        exitwhen k > 5
        set f = GSPF_Text("GSPF_GrpLbl", k, box, 0.11, 0.016)
        call BlzFrameSetPoint(f, FRAMEPOINT_TOPLEFT, box, FRAMEPOINT_TOPLEFT, 0.026 + (k / 3) * 0.385 + ModuloInteger(k, 3) * 0.123, -0.064)
        call BlzFrameSetTextAlignment(f, TEXT_JUSTIFY_MIDDLE, TEXT_JUSTIFY_LEFT)
        call BlzFrameSetText(f, GSPF_GroupLabel(k))
        set k = k + 1
    endloop

    // 영웅 아이콘 버튼: 그룹마다 2열, 위에서 아래로
    set i = 0
    loop
        exitwhen i >= GSPF_HeroCount()
        set grp = GSPF_GroupOf(i)
        if grp != last then
            set j = 0
            set last = grp
        endif
        set x = 0.024 + (grp / 3) * 0.385 + ModuloInteger(grp, 3) * 0.123 + ModuloInteger(j, 2) * 0.056
        set f = BlzCreateFrame("ScoreScreenBottomButtonTemplate", box, 0, 7400 + i)
        call BlzFrameSetSize(f, 0.046, 0.046)
        call BlzFrameSetPoint(f, FRAMEPOINT_TOPLEFT, box, FRAMEPOINT_TOPLEFT, x, -0.082 - (j / 2) * 0.052)
        call BlzFrameSetTexture(BlzGetFrameByName("ScoreScreenButtonBackdrop", 7400 + i), BlzGetAbilityIcon(GSPF_HeroAt(i)), 0, true)
        call BlzTriggerRegisterFrameEvent(th, f, FRAMEEVENT_CONTROL_CLICK)
        // 판매 시작 전 쿨다운: 위에서 아래로 걷히는 어두운 막 + 남은 초
        set g = BlzCreateFrameByType("BACKDROP", "GSPF_Cd", f, "", 7400 + i)
        call BlzFrameSetPoint(g, FRAMEPOINT_TOPLEFT, f, FRAMEPOINT_TOPLEFT, 0.0, 0.0)
        call BlzFrameSetSize(g, 0.046, 0.046)
        call BlzFrameSetTexture(g, "Textures\\Black32.blp", 0, true)
        call BlzFrameSetAlpha(g, 175)
        set g = GSPF_Text("GSPF_CdText", 7400 + i, f, 0.046, 0.046)
        call BlzFrameSetAllPoints(g, f)
        call BlzFrameSetTextAlignment(g, TEXT_JUSTIFY_MIDDLE, TEXT_JUSTIFY_CENTER)
        call BlzFrameSetScale(g, 1.3)
        // 툴팁: 영웅 이름
        set g = BlzCreateFrameByType("BACKDROP", "GSPF_Tip", f, "", 7400 + i)
        call BlzFrameSetTexture(g, "Textures\\Black32.blp", 0, true)
        call BlzFrameSetAlpha(g, 230)
        call BlzFrameSetSize(g, 0.14, 0.024)
        call BlzFrameSetPoint(g, FRAMEPOINT_BOTTOM, f, FRAMEPOINT_TOP, 0.0, 0.004)
        call BlzFrameSetTooltip(f, g)
        set g = GSPF_Text("GSPF_TipText", 7400 + i, g, 0.14, 0.024)
        call BlzFrameSetPoint(g, FRAMEPOINT_CENTER, BlzGetFrameByName("GSPF_Tip", 7400 + i), FRAMEPOINT_CENTER, 0.0, 0.0)
        call BlzFrameSetTextAlignment(g, TEXT_JUSTIFY_MIDDLE, TEXT_JUSTIFY_CENTER)
        call BlzFrameSetText(g, "|cffffffff" + GetObjectName(GSPF_HeroAt(i)) + "|r")
        set j = j + 1
        set i = i + 1
    endloop
    call TriggerAddAction(th, function GSPF_OnHeroClick)

    set f = GSPF_Text("GSPF_Hint", 0, box, 0.74, 0.018)
    call BlzFrameSetPoint(f, FRAMEPOINT_BOTTOM, box, FRAMEPOINT_BOTTOM, 0.0, 0.014)
    call BlzFrameSetTextAlignment(f, TEXT_JUSTIFY_MIDDLE, TEXT_JUSTIFY_CENTER)
    call BlzFrameSetVisible(box, false)

    // 닫기 버튼 / -보드 (다시 열기)
    set k = 0
    loop
        exitwhen k > 11
        call TriggerRegisterPlayerChatEvent(tb, Player(k), "-보드", true)
        call TriggerRegisterPlayerChatEvent(tb, Player(k), "-board", true)
        set k = k + 1
    endloop
    call TriggerAddAction(tb, function GSPF_OnBoardCmd)
    set box = null
    set f = null
    set g = null
    set th = null
    set tb = null
endfunction

function GSPF_Create takes nothing returns nothing
    local integer host = GSPF_FindHost()
    call DestroyTimer(GetExpiredTimer())
    call GSPF_Hidden("GSPF_Host", I2S(host))
    call GSPF_Hidden("GSPF_Sel", "000000")
    call GSPF_Hidden("GSPF_Votes", "000000000000")
    call GSPF_Hidden("GSPF_Done", "0")
    call GSPF_Hidden("GSPF_Closed", "0")
    call GSPF_CreateBoard()
    if host < 0 then
        call GSPF_Confirm()
        return
    endif
    call GSPF_CreateModeBox(host)
    call GSPF_RefreshModes()
    call GSPF_RefreshVote()
    call PauseGame(true)
endfunction

function GSPF_Init takes nothing returns nothing
    // 영웅 목록(Set Variable Hero, 1초)과 위습 지급(Initialize, 1초) 이후에 시작
    call TimerStart(CreateTimer(), 2.5, false, function GSPF_Create)
endfunction
