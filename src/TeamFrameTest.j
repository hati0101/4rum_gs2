//===========================================================================
// GSTF 테스트 명령어 (테스트 빌드 전용 - 배포 맵에 넣지 말 것)
//   -gstest : 내 팀 빈 슬롯 4곳에 같은 진영 영웅을 무작위로 생성
//             봇1 Lv2 궁 미습득 / 봇2 Lv4 궁 미습득, 체력40% 마나20%
//             봇3 Lv6 궁 습득(준비) / 봇4 Lv6 궁 습득 + 쿨다운 30초
//   -gskill : 봇1 처치 (사망 표시 확인)
// 사람이 있는 슬롯은 건드리지 않음. 다시 입력하면 봇을 새로 뽑음.
//===========================================================================

function GSTF_TestTypeUsed takes integer t returns boolean
    local integer i = 1
    loop
        exitwhen i > 12
        if udg_HeroPlayer[i] != null and GetUnitTypeId(udg_HeroPlayer[i]) == t then
            return true
        endif
        set i = i + 1
    endloop
    return false
endfunction

// 테스터 진영(가디언/다크니스) 영웅 중 아직 안 쓰인 것 하나
function GSTF_TestPickHero takes player tester returns integer
    local integer lo = 1
    local integer hi = udg_HeroMax[1]
    local integer t = 0
    local integer tries = 0
    if IsPlayerAlly(tester, udg_Force[2]) then
        set lo = udg_HeroMax[1] + 1
        set hi = udg_HeroMax[3]
    endif
    loop
        set t = udg_Hero[GetRandomInt(lo, hi)]
        exitwhen tries > 50 or not GSTF_TestTypeUsed(t)
        set tries = tries + 1
    endloop
    return t
endfunction

// 테스터와 같은 쪽(1~5 / 7~11)의 빈 슬롯 번호를 n번째로 찾음, 없으면 -1
function GSTF_TestSlot takes player tester, integer n returns integer
    local integer tid = GetPlayerId(tester)
    local integer first = 1
    local integer pid
    local integer found = 0
    if tid >= 6 then
        set first = 7
    endif
    set pid = first
    loop
        exitwhen pid > first + 4
        if pid != tid and GetPlayerSlotState(Player(pid)) != PLAYER_SLOT_STATE_PLAYING then
            if found == n then
                return pid
            endif
            set found = found + 1
        endif
        set pid = pid + 1
    endloop
    return -1
endfunction

function GSTF_TestSpawn takes player tester, integer n, integer lvl, integer mode returns nothing
    local integer pid = GSTF_TestSlot(tester, n)
    local player p
    local unit h = udg_HeroPlayer[GetPlayerId(tester) + 1]
    local unit u
    local integer t
    local integer ult
    local real x
    local real y
    local string st
    if pid < 0 then
        call DisplayTextToPlayer(tester, 0, 0, "|cffff8080GSTF 테스트: 빈 팀 슬롯이 부족함|r")
        return
    endif
    set p = Player(pid)
    // 이전 테스트 봇 제거 (빈 슬롯 소유 영웅만)
    if udg_HeroPlayer[pid + 1] != null then
        call RemoveUnit(udg_HeroPlayer[pid + 1])
        set udg_HeroPlayer[pid + 1] = null
    endif
    set t = GSTF_TestPickHero(tester)
    if h != null then
        set x = GetUnitX(h) + 150.0 * (n - 1.5)
        set y = GetUnitY(h) - 250.0
    else
        set x = GetStartLocationX(GetPlayerStartLocation(tester))
        set y = GetStartLocationY(GetPlayerStartLocation(tester))
    endif
    set u = CreateUnit(p, t, x, y, 270.0)
    call SetPlayerAllianceStateBJ(p, tester, bj_ALLIANCE_ALLIED_VISION)
    call SetPlayerAllianceStateBJ(tester, p, bj_ALLIANCE_ALLIED_VISION)
    call SetHeroLevel(u, lvl, false)
    set ult = GSTF_SkillOf(t, 3)
    if mode >= 2 and ult != 0 then
        call SelectHeroSkill(u, ult)
    endif
    if mode == 3 and ult != 0 then
        call BlzStartUnitAbilityCooldown(u, ult, 30.0)
    endif
    if mode == 1 then
        call SetUnitState(u, UNIT_STATE_LIFE, GetUnitState(u, UNIT_STATE_MAX_LIFE) * 0.4)
        call SetUnitState(u, UNIT_STATE_MANA, GetUnitState(u, UNIT_STATE_MAX_MANA) * 0.2)
    endif
    set udg_HeroPlayer[pid + 1] = u

    if ult == 0 then
        set st = "|cffff8080궁극기 표에 없음!|r"
    elseif GetUnitAbilityLevel(u, ult) > 0 then
        set st = "|cff80ff80습득 Lv" + I2S(GetUnitAbilityLevel(u, ult)) + "|r"
    else
        set st = "미습득"
    endif
    call DisplayTextToPlayer(tester, 0, 0, "GSTF 봇" + I2S(n + 1) + " [P" + I2S(pid + 1) + "] " + GetUnitName(u) + " Lv" + I2S(GetHeroLevel(u)) + " / 궁: " + GetObjectName(ult) + " " + st)
    set p = null
    set h = null
    set u = null
endfunction

function GSTF_TestCmd takes nothing returns nothing
    local player tester = GetTriggerPlayer()
    local integer pid
    if GetEventPlayerChatString() == "-gskill" then
        set pid = GSTF_TestSlot(tester, 0)
        if pid >= 0 and udg_HeroPlayer[pid + 1] != null then
            call KillUnit(udg_HeroPlayer[pid + 1])
            call DisplayTextToPlayer(tester, 0, 0, "GSTF 봇1 처치")
        endif
    else
        call GSTF_TestSpawn(tester, 0, 2, 0)
        call GSTF_TestSpawn(tester, 1, 4, 1)
        call GSTF_TestSpawn(tester, 2, 6, 2)
        call GSTF_TestSpawn(tester, 3, 6, 3)
    endif
    set tester = null
endfunction

function GSTF_TestInit takes nothing returns nothing
    local trigger t = CreateTrigger()
    local integer i = 0
    loop
        exitwhen i > 11
        call TriggerRegisterPlayerChatEvent(t, Player(i), "-gstest", true)
        call TriggerRegisterPlayerChatEvent(t, Player(i), "-gskill", true)
        set i = i + 1
    endloop
    call TriggerAddAction(t, function GSTF_TestCmd)
    set t = null
endfunction
