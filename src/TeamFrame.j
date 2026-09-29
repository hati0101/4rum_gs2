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

// 패널 윗변 높이 (상단 자원바 아래)
function GSTF_Top takes nothing returns real
    return 0.545
endfunction

// 영웅 유닛 타입 -> 궁극기 (tools/teamframe.py gen 으로 생성)
function GSTF_UltOf takes integer t returns integer
    if t == 'Hpal' then // 디바인 나이트
        return 'A0NM'
    elseif t == 'Hamg' then // 피닉스 마스터
        return 'A029'
    elseif t == 'Obla' then // 소드 마스터
        return 'A00E'
    elseif t == 'Hvwd' then // Hvwd
        return 'A11K'
    elseif t == 'Harf' then // 스워시 버클러
        return 'A065'
    elseif t == 'Emfr' then // 엘더 드루이드
        return 'A06Y'
    elseif t == 'Hkal' then // 스펠 인보커
        return 'A08J'
    elseif t == 'Ofar' then // 썬더 비스트
        return 'A0NE'
    elseif t == 'Hjai' then // 하프 엔젤릭
        return 'A08D'
    elseif t == 'Ewrd' then // 드로우 어쎄신
        return 'A0AP'
    elseif t == 'Emoo' then // 아케인 아처
        return 'A09U'
    elseif t == 'Hpb1' then // 블러디 나이트
        return 'A0BN'
    elseif t == 'Hmkg' then // 크루스닉
        return 'A0DQ'
    elseif t == 'Ekee' then // 달라란 다크메이지
        return 'A0C9'
    elseif t == 'Hmgd' then // 몽크
        return 'A0EY'
    elseif t == 'Hdgo' then // 문 울프
        return 'A0GW'
    elseif t == 'Hpb2' then // 네츄럴 샤먼
        return 'A0GO'
    elseif t == 'Hart' then // 룬 나이트
        return 'A0L8'
    elseif t == 'Npbm' then // 판다 워리어
        return 'A0H4'
    elseif t == 'Ogrh' then // 글라디에이터
        return 'A0AV'
    elseif t == 'Osam' then // 플레임 이보커
        return 'A0SD'
    elseif t == 'Etyr' then // 하이 프리스티스
        return 'A0JL'
    elseif t == 'Nsjs' then // 에인션트 트리
        return 'A07I'
    elseif t == 'Eevi' then // 펠 프린스
        return 'A09S'
    elseif t == 'Ntin' then // 고블린 팅커
        return 'A0ND'
    elseif t == 'Hmbr' then // 듀에르가 드워프 킹
        return 'A0O3'
    elseif t == 'Ekgg' then // 사일런서
        return 'A118'
    elseif t == 'Ocbh' then // 스톤 가드
        return 'A0U3'
    elseif t == 'Hhkl' then // 토테믹 워로드
        return 'A0ZH'
    elseif t == 'Huth' then // 할루시네이터
        return 'A11A'
    elseif t == 'Opgh' then // 드로우 라이더
        return 'A0HT'
    elseif t == 'Nman' then // 엘리멘탈리스트
        return 'A12D'
    elseif t == 'Hgam' then // 레바논 테크마스터
        return 'A144'
    elseif t == 'Ocb2' then // 로열 카발리어
        return 'A0WG'
    elseif t == 'Orex' then // 듀에르가 캐논 브라더
        return 'A007'
    elseif t == 'Edem' then // 프린스 오브 다크니스
        return 'A0JA'
    elseif t == 'Ewar' then // 드로우 프리스티스
        return 'A034'
    elseif t == 'Hblm' then // 폴른 메이지
        return 'A01H'
    elseif t == 'Udea' then // 둠 로드
        return 'A02A'
    elseif t == 'Nbrn' then // 카오스 위치
        return 'A11L'
    elseif t == 'Uear' then // 다크 템플러
        return 'A0PC'
    elseif t == 'Uvng' then // 다크 샤먼
        return 'A0LX'
    elseif t == 'Otch' then // 그레이트 워로드
        return 'A0N1'
    elseif t == 'Udre' then // 뱀파이어 로드
        return 'A09G'
    elseif t == 'Usyl' then // 소울 헌터
        return 'A09W'
    elseif t == 'Nbbc' then // 퓨리 파이터
        return 'A0U5'
    elseif t == 'Odrt' then // 플레임 블레이더
        return 'A0CT'
    elseif t == 'Hvsh' then // 메두사 퀸
        return 'A07Q'
    elseif t == 'Ogld' then // 메로닝거
        return 'A0D8'
    elseif t == 'Ulic' then // 로드 오브 노스윈터
        return 'A0EL'
    elseif t == 'Hant' then // 드로우 헌터
        return 'A0EW'
    elseif t == 'Umal' then // 섀도우 스토커
        return 'A0HA'
    elseif t == 'Ucrl' then // 로드 오브 뎁스
        return 'A0HN'
    elseif t == 'Uwar' then // 어비스 레이쓰
        return 'A0KZ'
    elseif t == 'Eevm' then // 커닝 트레이서
        return 'A12L'
    elseif t == 'Nmag' then // 인퀴지터
        return 'A0LS'
    elseif t == 'Oshd' then // 섀도우 시프
        return 'A0OB'
    elseif t == 'Ubal' then // 트롤 버서커
        return 'A02L'
    elseif t == 'Naka' then // 블랙 쉐이커
        return 'A04U'
    elseif t == 'Uclc' then // 다크 프리스트
        return 'A03B'
    elseif t == 'Eill' then // 메두사 로얄가드
        return 'A0NG'
    elseif t == 'Nplh' then // 드레드 나이트
        return 'A0VB'
    elseif t == 'Nklj' then // 데스 메신져
        return 'A0T1'
    elseif t == 'Hapm' then // 데스페라도
        return 'A0FU'
    elseif t == 'Utic' then // 오우거 로드
        return 'A03U'
    elseif t == 'Nfir' then // 로드 오브 인페르노
        return 'A0ZS'
    elseif t == 'Uanb' then // 뎁스 크라울러
        return 'A0ID'
    elseif t == 'H00I' then // (형태) H00I
        return 'A0EY'
    elseif t == 'H00O' then // (형태) H00O
        return 'A0EY'
    elseif t == 'H00P' then // (형태) H00P
        return 'A0EY'
    elseif t == 'H00Q' then // (형태) H00Q
        return 'A0EY'
    elseif t == 'N02K' then // (형태) N02K
        return 'A0ND'
    elseif t == 'N03I' then // (형태) N03I
        return 'A0T1'
    elseif t == 'N02L' then // (형태) N02L
        return 'A0ND'
    elseif t == 'N02M' then // (형태) N02M
        return 'A0ND'
    elseif t == 'H01P' then // (형태) H01P
        return 'A0O3'
    elseif t == 'O005' then // (형태) O005
        return 'A0HT'
    elseif t == 'U00I' then // (형태) U00I
        return 'A0ID'
    elseif t == 'O006' then // (형태) O006
        return 'A007'
    endif
    return 0
endfunction

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

        // 플레이어 이름
        set f = BlzCreateFrameByType("TEXT", "GSTF_Name", slot, "", i)
        call BlzFrameSetSize(f, 0.044, 0.012)
        call BlzFrameSetPoint(f, FRAMEPOINT_TOPLEFT, slot, FRAMEPOINT_TOPLEFT, 0.045, -0.006)
        call BlzFrameSetTextAlignment(f, TEXT_JUSTIFY_MIDDLE, TEXT_JUSTIFY_LEFT)
        call BlzFrameSetScale(f, 0.8)

        // 궁극기 아이콘 + 쿨다운 숫자 + 준비 표시(초록 점)
        set f = BlzCreateFrameByType("BACKDROP", "GSTF_Ult", slot, "", i)
        call BlzFrameSetSize(f, 0.018, 0.018)
        call BlzFrameSetPoint(f, FRAMEPOINT_TOPRIGHT, slot, FRAMEPOINT_TOPRIGHT, -0.004, -0.004)
        set g = BlzCreateFrameByType("TEXT", "GSTF_UltCd", f, "", i)
        call BlzFrameSetAllPoints(g, f)
        call BlzFrameSetTextAlignment(g, TEXT_JUSTIFY_MIDDLE, TEXT_JUSTIFY_CENTER)
        set g = BlzCreateFrameByType("BACKDROP", "GSTF_UltDot", f, "", i)
        call BlzFrameSetSize(g, 0.006, 0.006)
        call BlzFrameSetPoint(g, FRAMEPOINT_CENTER, f, FRAMEPOINT_BOTTOMRIGHT, 0.0, 0.0)
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
    call BlzFrameSetText(BlzGetFrameByName("GSTF_Lvl", i), I2S(GetHeroLevel(u)))
    call BlzFrameSetText(BlzGetFrameByName("GSTF_Name", i), GetPlayerName(p))

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
                call BlzFrameSetText(BlzGetFrameByName("GSTF_UltCd", i), I2S(R2I(cd) + 1))
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

function GSTF_Update takes nothing returns nothing
    local integer lid = GetPlayerId(GetLocalPlayer())
    local integer first
    local integer pid
    local integer k = 0
    local unit u
    local real w = I2R(BlzGetLocalClientWidth())
    local real h = I2R(BlzGetLocalClientHeight())
    local real right = 0.8
    local framehandle root = BlzGetFrameByName("GSTF_Root", 0)
    local framehandle slot

    // 표시는 로컬 플레이어 기준 (프레임 조작만 하므로 디싱크 없음)
    if lid >= 1 and lid <= 5 then
        set first = 1
    elseif lid >= 7 and lid <= 11 then
        set first = 7
    else
        call BlzFrameSetVisible(root, false)
        set root = null
        return
    endif
    call BlzFrameSetVisible(root, true)

    // 와이드 화면에서도 실제 오른쪽 끝에 붙임
    if h > 0 then
        set right = 0.4 + 0.3 * w / h
    endif
    call BlzFrameClearAllPoints(root)
    call BlzFrameSetAbsPoint(root, FRAMEPOINT_TOPRIGHT, right - 0.004, GSTF_Top())

    set pid = first
    loop
        exitwhen pid > first + 4
        set u = udg_HeroPlayer[pid + 1]
        if u != null and GetUnitTypeId(u) != 0 and (pid != lid or GSTF_ShowSelf()) then
            set slot = BlzGetFrameByName("GSTF_Slot", k)
            call BlzFrameClearAllPoints(slot)
            call BlzFrameSetPoint(slot, FRAMEPOINT_TOPRIGHT, root, FRAMEPOINT_TOPRIGHT, 0.0, -k * (GSTF_H() + GSTF_Gap()))
            call BlzFrameSetVisible(slot, true)
            call GSTF_FillSlot(k, Player(pid), u)
            set k = k + 1
        endif
        set pid = pid + 1
    endloop
    loop
        exitwhen k > 4
        call BlzFrameSetVisible(BlzGetFrameByName("GSTF_Slot", k), false)
        set k = k + 1
    endloop
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
