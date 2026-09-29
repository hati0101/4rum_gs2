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

// 영웅 유닛 타입 -> Q W E R 스킬 (tools/teamframe.py gen 으로 생성)
function GSTF_SkillOf takes integer t, integer s returns integer
    if t == 'Edem' then // 프린스 오브 다크니스
        if s == 0 then
            return 'A003'
        elseif s == 1 then
            return 'A00G'
        elseif s == 2 then
            return 'A04P'
        endif
        return 'A0JA'
    elseif t == 'Obla' then // 소드 마스터
        if s == 0 then
            return 'A00C'
        elseif s == 1 then
            return 'A0UC'
        elseif s == 2 then
            return 'A11M'
        endif
        return 'A00E'
    elseif t == 'Hvwd' then // Hvwd
        if s == 0 then
            return 'A012'
        elseif s == 1 then
            return 'A0O8'
        elseif s == 2 then
            return 'A12Q'
        endif
        return 'A11K'
    elseif t == 'Hpal' then // 디바인 나이트
        if s == 0 then
            return 'A090'
        elseif s == 1 then
            return 'A0UB'
        elseif s == 2 then
            return 'A00Y'
        endif
        return 'A0NM'
    elseif t == 'Harf' then // 스워시 버클러
        if s == 0 then
            return 'A01X'
        elseif s == 1 then
            return 'A01M'
        elseif s == 2 then
            return 'A0NA'
        endif
        return 'A065'
    elseif t == 'Hblm' then // 폴른 메이지
        if s == 0 then
            return 'A01I'
        elseif s == 1 then
            return 'A01J'
        elseif s == 2 then
            return 'A01K'
        endif
        return 'A01H'
    elseif t == 'Oshd' then // 섀도우 시프
        if s == 0 then
            return 'A09P'
        elseif s == 1 then
            return 'A0OA'
        elseif s == 2 then
            return 'A0G6'
        endif
        return 'A0OB'
    elseif t == 'Hamg' then // 피닉스 마스터
        if s == 0 then
            return 'A023'
        elseif s == 1 then
            return 'A025'
        elseif s == 2 then
            return 'A098'
        endif
        return 'A029'
    elseif t == 'Nbrn' then // 카오스 위치
        if s == 0 then
            return 'A02D'
        elseif s == 1 then
            return 'A02C'
        elseif s == 2 then
            return 'A02B'
        endif
        return 'A11L'
    elseif t == 'Ewar' then // 드로우 프리스티스
        if s == 0 then
            return 'A02Q'
        elseif s == 1 then
            return 'A067'
        elseif s == 2 then
            return 'A02O'
        endif
        return 'A034'
    elseif t == 'Udea' then // 둠 로드
        if s == 0 then
            return 'A02F'
        elseif s == 1 then
            return 'A02M'
        elseif s == 2 then
            return 'A02K'
        endif
        return 'A02A'
    elseif t == 'Udre' then // 뱀파이어 로드
        if s == 0 then
            return 'A0V9'
        elseif s == 1 then
            return 'A09J'
        elseif s == 2 then
            return 'A0GQ'
        endif
        return 'A09G'
    elseif t == 'Ucrl' then // 로드 오브 뎁스
        if s == 0 then
            return 'A0HX'
        elseif s == 1 then
            return 'A0HK'
        elseif s == 2 then
            return 'A0HL'
        endif
        return 'A0HN'
    elseif t == 'Hmkg' then // 크루스닉
        if s == 0 then
            return 'A0AC'
        elseif s == 1 then
            return 'A0AD'
        elseif s == 2 then
            return 'A0AE'
        endif
        return 'A0DQ'
    elseif t == 'Emfr' then // 엘더 드루이드
        if s == 0 then
            return 'A06V'
        elseif s == 1 then
            return 'A06X'
        elseif s == 2 then
            return 'A06U'
        endif
        return 'A06Y'
    elseif t == 'Uear' then // 다크 템플러
        if s == 0 then
            return 'A07T'
        elseif s == 1 then
            return 'A07U'
        elseif s == 2 then
            return 'A0QE'
        endif
        return 'A0PC'
    elseif t == 'Hjai' then // 하프 엔젤릭
        if s == 0 then
            return 'A086'
        elseif s == 1 then
            return 'A05T'
        elseif s == 2 then
            return 'A088'
        endif
        return 'A08D'
    elseif t == 'Hkal' then // 스펠 인보커
        if s == 0 then
            return 'A08G'
        elseif s == 1 then
            return 'A03V'
        elseif s == 2 then
            return 'A08H'
        endif
        return 'A08J'
    elseif t == 'Uvng' then // 다크 샤먼
        if s == 0 then
            return 'A08K'
        elseif s == 1 then
            return 'A08L'
        elseif s == 2 then
            return 'A08M'
        endif
        return 'A0LX'
    elseif t == 'Otch' then // 그레이트 워로드
        if s == 0 then
            return 'A0MS'
        elseif s == 1 then
            return 'A08Q'
        elseif s == 2 then
            return 'A0RY'
        endif
        return 'A0N1'
    elseif t == 'Ofar' then // 썬더 비스트
        if s == 0 then
            return 'A0QN'
        elseif s == 1 then
            return 'A091'
        elseif s == 2 then
            return 'A092'
        endif
        return 'A0NE'
    elseif t == 'Usyl' then // 소울 헌터
        if s == 0 then
            return 'A149'
        elseif s == 1 then
            return 'A0A1'
        elseif s == 2 then
            return 'A0A2'
        endif
        return 'A09W'
    elseif t == 'Eevm' then // 커닝 트레이서
        if s == 0 then
            return 'A09M'
        elseif s == 1 then
            return 'A0CN'
        elseif s == 2 then
            return 'A08S'
        endif
        return 'A12L'
    elseif t == 'Ewrd' then // 드로우 어쎄신
        if s == 0 then
            return 'A013'
        elseif s == 1 then
            return 'A0A7'
        elseif s == 2 then
            return 'A0ZT'
        endif
        return 'A0AP'
    elseif t == 'Hpb2' then // 네츄럴 샤먼
        if s == 0 then
            return 'A0BC'
        elseif s == 1 then
            return 'A0N2'
        elseif s == 2 then
            return 'A0BD'
        endif
        return 'A0GO'
    elseif t == 'Hpb1' then // 블러디 나이트
        if s == 0 then
            return 'A0BO'
        elseif s == 1 then
            return 'A0BM'
        elseif s == 2 then
            return 'A0NP'
        endif
        return 'A0BN'
    elseif t == 'Emoo' then // 아케인 아처
        if s == 0 then
            return 'A0TL'
        elseif s == 1 then
            return 'A12I'
        elseif s == 2 then
            return 'A0BX'
        endif
        return 'A09U'
    elseif t == 'Ekee' then // 달라란 다크메이지
        if s == 0 then
            return 'A04O'
        elseif s == 1 then
            return 'A0C4'
        elseif s == 2 then
            return 'A104'
        endif
        return 'A0C9'
    elseif t == 'Nbbc' then // 퓨리 파이터
        if s == 0 then
            return 'A0TM'
        elseif s == 1 then
            return 'A0CF'
        elseif s == 2 then
            return 'A0KR'
        endif
        return 'A0U5'
    elseif t == 'Odrt' then // 플레임 블레이더
        if s == 0 then
            return 'A0Z4'
        elseif s == 1 then
            return 'A0CP'
        elseif s == 2 then
            return 'ANic'
        endif
        return 'A0CT'
    elseif t == 'Hvsh' then // 메두사 퀸
        if s == 0 then
            return 'A0CO'
        elseif s == 1 then
            return 'A0CZ'
        elseif s == 2 then
            return 'A145'
        endif
        return 'A07Q'
    elseif t == 'Ogld' then // 메로닝거
        if s == 0 then
            return 'A07V'
        elseif s == 1 then
            return 'A0D6'
        elseif s == 2 then
            return 'A0DB'
        endif
        return 'A0D8'
    elseif t == 'Ulic' then // 로드 오브 노스윈터
        if s == 0 then
            return 'A0EK'
        elseif s == 1 then
            return 'A0EI'
        elseif s == 2 then
            return 'A0EJ'
        endif
        return 'A0EL'
    elseif t == 'Hant' then // 드로우 헌터
        if s == 0 then
            return 'A0XQ'
        elseif s == 1 then
            return 'A00S'
        elseif s == 2 then
            return 'S007'
        endif
        return 'A0EW'
    elseif t == 'Hmgd' then // 몽크
        if s == 0 then
            return 'A0EX'
        elseif s == 1 then
            return 'A0EZ'
        elseif s == 2 then
            return 'A0MG'
        endif
        return 'A0EY'
    elseif t == 'Hart' then // 룬 나이트
        if s == 0 then
            return 'A0FI'
        elseif s == 1 then
            return 'A0FJ'
        elseif s == 2 then
            return 'A0GK'
        endif
        return 'A0L8'
    elseif t == 'Hdgo' then // 문 울프
        if s == 0 then
            return 'A0FM'
        elseif s == 1 then
            return 'A0GA'
        elseif s == 2 then
            return 'A0FO'
        endif
        return 'A0GW'
    elseif t == 'Nfir' then // 로드 오브 인페르노
        if s == 0 then
            return 'A13M'
        elseif s == 1 then
            return 'A111'
        elseif s == 2 then
            return 'A0WM'
        endif
        return 'A0ZS'
    elseif t == 'Umal' then // 섀도우 스토커
        if s == 0 then
            return 'A0H7'
        elseif s == 1 then
            return 'A0H8'
        elseif s == 2 then
            return 'A0HC'
        endif
        return 'A0HA'
    elseif t == 'Npbm' then // 판다 워리어
        if s == 0 then
            return 'A0ZB'
        elseif s == 1 then
            return 'A139'
        elseif s == 2 then
            return 'A0H2'
        endif
        return 'A0H4'
    elseif t == 'Huth' then // 할루시네이터
        if s == 0 then
            return 'A0IF'
        elseif s == 1 then
            return 'A10A'
        elseif s == 2 then
            return 'A0JZ'
        endif
        return 'A11A'
    elseif t == 'Ubal' then // 트롤 버서커
        if s == 0 then
            return 'A0RD'
        elseif s == 1 then
            return 'A0RE'
        elseif s == 2 then
            return 'A0J8'
        endif
        return 'A02L'
    elseif t == 'Hmbr' then // 듀에르가 드워프 킹
        if s == 0 then
            return 'A0NZ'
        elseif s == 1 then
            return 'A0O0'
        elseif s == 2 then
            return 'A11H'
        endif
        return 'A0O3'
    elseif t == 'Nmag' then // 인퀴지터
        if s == 0 then
            return 'A0M8'
        elseif s == 1 then
            return 'A0LV'
        elseif s == 2 then
            return 'A0FK'
        endif
        return 'A0LS'
    elseif t == 'Eevi' then // 펠 프린스
        if s == 0 then
            return 'A0L9'
        elseif s == 1 then
            return 'A0LA'
        elseif s == 2 then
            return 'A0LB'
        endif
        return 'A09S'
    elseif t == 'Osam' then // 플레임 이보커
        if s == 0 then
            return 'A0IS'
        elseif s == 1 then
            return 'A0IT'
        elseif s == 2 then
            return 'A0IU'
        endif
        return 'A0SD'
    elseif t == 'Eill' then // 메두사 로얄가드
        if s == 0 then
            return 'A0T7'
        elseif s == 1 then
            return 'A0NK'
        elseif s == 2 then
            return 'A0NL'
        endif
        return 'A0NG'
    elseif t == 'Etyr' then // 하이 프리스티스
        if s == 0 then
            return 'A0JE'
        elseif s == 1 then
            return 'A0JH'
        elseif s == 2 then
            return 'A0JJ'
        endif
        return 'A0JL'
    elseif t == 'Hhkl' then // 토테믹 워로드
        if s == 0 then
            return 'A0T8'
        elseif s == 1 then
            return 'A0T4'
        elseif s == 2 then
            return 'A0IN'
        endif
        return 'A0ZH'
    elseif t == 'Nsjs' then // 에인션트 트리
        if s == 0 then
            return 'A0L2'
        elseif s == 1 then
            return 'A0L3'
        elseif s == 2 then
            return 'A0RW'
        endif
        return 'A07I'
    elseif t == 'Uwar' then // 어비스 레이쓰
        if s == 0 then
            return 'A0AJ'
        elseif s == 1 then
            return 'A0KO'
        elseif s == 2 then
            return 'A0GI'
        endif
        return 'A0KZ'
    elseif t == 'Hapm' then // 데스페라도
        if s == 0 then
            return 'A07Z'
        elseif s == 1 then
            return 'A136'
        elseif s == 2 then
            return 'A0PY'
        endif
        return 'A0FU'
    elseif t == 'Ntin' then // 고블린 팅커
        if s == 0 then
            return 'A0NB'
        elseif s == 1 then
            return 'A0NU'
        elseif s == 2 then
            return 'A0NJ'
        endif
        return 'A0ND'
    elseif t == 'Uclc' then // 다크 프리스트
        if s == 0 then
            return 'A02W'
        elseif s == 1 then
            return 'A00A'
        elseif s == 2 then
            return 'A03A'
        endif
        return 'A03B'
    elseif t == 'Hgam' then // 레바논 테크마스터
        if s == 0 then
            return 'A0CA'
        elseif s == 1 then
            return 'A0KU'
        elseif s == 2 then
            return 'A004'
        endif
        return 'A144'
    elseif t == 'Utic' then // 오우거 로드
        if s == 0 then
            return 'A07A'
        elseif s == 1 then
            return 'A04Y'
        elseif s == 2 then
            return 'A10Z'
        endif
        return 'A03U'
    elseif t == 'Ocbh' then // 스톤 가드
        if s == 0 then
            return 'A05M'
        elseif s == 1 then
            return 'A05S'
        elseif s == 2 then
            return 'A0U1'
        endif
        return 'A0U3'
    elseif t == 'Naka' then // 블랙 쉐이커
        if s == 0 then
            return 'A03T'
        elseif s == 1 then
            return 'A09F'
        elseif s == 2 then
            return 'A046'
        endif
        return 'A04U'
    elseif t == 'Nklj' then // 데스 메신져
        if s == 0 then
            return 'A0JN'
        elseif s == 1 then
            return 'A0SP'
        elseif s == 2 then
            return 'A00K'
        endif
        return 'A0T1'
    elseif t == 'Ekgg' then // 사일런서
        if s == 0 then
            return 'A03K'
        elseif s == 1 then
            return 'A03F'
        elseif s == 2 then
            return 'A0RG'
        endif
        return 'A118'
    elseif t == 'Nman' then // 엘리멘탈리스트
        if s == 0 then
            return 'A0VQ'
        elseif s == 1 then
            return 'A0VR'
        elseif s == 2 then
            return 'A13V'
        endif
        return 'A12D'
    elseif t == 'Ocb2' then // 로열 카발리어
        if s == 0 then
            return 'A0FB'
        elseif s == 1 then
            return 'A0KN'
        elseif s == 2 then
            return 'A0GV'
        endif
        return 'A0WG'
    elseif t == 'Ogrh' then // 글라디에이터
        if s == 0 then
            return 'A078'
        elseif s == 1 then
            return 'A0D0'
        elseif s == 2 then
            return 'A0AR'
        endif
        return 'A0AV'
    elseif t == 'Opgh' then // 드로우 라이더
        if s == 0 then
            return 'A13W'
        elseif s == 1 then
            return 'A0G4'
        elseif s == 2 then
            return 'A0FR'
        endif
        return 'A0HT'
    elseif t == 'Nplh' then // 드레드 나이트
        if s == 0 then
            return 'A0KT'
        elseif s == 1 then
            return 'A0VD'
        elseif s == 2 then
            return 'A0VC'
        endif
        return 'A0VB'
    elseif t == 'Uanb' then // 뎁스 크라울러
        if s == 0 then
            return 'A0I6'
        elseif s == 1 then
            return 'A03D'
        elseif s == 2 then
            return 'A0ZR'
        endif
        return 'A0ID'
    elseif t == 'Orex' then // 듀에르가 캐논 브라더
        if s == 0 then
            return 'A00N'
        elseif s == 1 then
            return 'A0N3'
        elseif s == 2 then
            return 'A0WY'
        endif
        return 'A007'
    elseif t == 'Othr' then // 블랙 스파이더
        if s == 0 then
            return 'A10Q'
        elseif s == 1 then
            return 'A0RC'
        elseif s == 2 then
            return 'A0DZ'
        endif
        return 'A0L5'
    elseif t == 'N02D' then // 에인션트 트리
        if s == 0 then
            return 'A0L2'
        elseif s == 1 then
            return 'A0L3'
        elseif s == 2 then
            return 'A0RW'
        endif
        return 'A0L5'
    elseif t == 'N02K' then // 고블린 팅커
        if s == 0 then
            return 'A0NB'
        elseif s == 1 then
            return 'A0NU'
        elseif s == 2 then
            return 'A0NJ'
        endif
        return 'A0ND'
    elseif t == 'H016' then // 던 울프
        if s == 0 then
            return 'A0D5'
        elseif s == 1 then
            return 'A0BU'
        elseif s == 2 then
            return 'A0CD'
        endif
        return 'A0DX'
    elseif t == 'H01I' then // 던 울프
        if s == 0 then
            return 'A0D5'
        elseif s == 1 then
            return 'A0BU'
        elseif s == 2 then
            return 'A0CD'
        endif
        return 'A0DX'
    elseif t == 'N03I' then // 데스 메신져
        if s == 0 then
            return 'A0JN'
        elseif s == 1 then
            return 'A0SP'
        elseif s == 2 then
            return 'A00K'
        endif
        return 'A0T1'
    elseif t == 'N02L' then // 고블린 팅커
        if s == 0 then
            return 'A0NB'
        elseif s == 1 then
            return 'A0NU'
        elseif s == 2 then
            return 'A0NJ'
        endif
        return 'A0ND'
    elseif t == 'N02M' then // 고블린 팅커
        if s == 0 then
            return 'A0NB'
        elseif s == 1 then
            return 'A0NU'
        elseif s == 2 then
            return 'A0NJ'
        endif
        return 'A0ND'
    elseif t == 'H01P' then // 듀에르가 드워프 킹
        if s == 0 then
            return 'A0NZ'
        elseif s == 1 then
            return 'A0O0'
        elseif s == 2 then
            return 'A11H'
        endif
        return 'A0O3'
    elseif t == 'N01L' then // 판다렌 듀얼 블레이더
        if s == 0 then
            return 'A0A6'
        elseif s == 1 then
            return 'A022'
        elseif s == 2 then
            return 'A0CU'
        endif
        return 'A0ZL'
    elseif t == 'O006' then // 듀에르가 캐논 브라더
        if s == 0 then
            return 'A00N'
        elseif s == 1 then
            return 'A0N3'
        elseif s == 2 then
            return 'A0WY'
        endif
        return 'A007'
    endif
    return 0
endfunction

// 쿨다운이 없는 스킬(패시브): 쿨다운 숫자 / 준비 표시 안 함
function GSTF_IsPassive takes integer a returns boolean
    if a == 'A004' then
        return true
    elseif a == 'A00K' then
        return true
    elseif a == 'A01M' then
        return true
    elseif a == 'A03U' then
        return true
    elseif a == 'A046' then
        return true
    elseif a == 'A04O' then
        return true
    elseif a == 'A07V' then
        return true
    elseif a == 'A092' then
        return true
    elseif a == 'A098' then
        return true
    elseif a == 'A09U' then
        return true
    elseif a == 'A0A2' then
        return true
    elseif a == 'A0AE' then
        return true
    elseif a == 'A0AR' then
        return true
    elseif a == 'A0BO' then
        return true
    elseif a == 'A0BX' then
        return true
    elseif a == 'A0CN' then
        return true
    elseif a == 'A0DB' then
        return true
    elseif a == 'A0DZ' then
        return true
    elseif a == 'A0FK' then
        return true
    elseif a == 'A0FR' then
        return true
    elseif a == 'A0FU' then
        return true
    elseif a == 'A0G6' then
        return true
    elseif a == 'A0GI' then
        return true
    elseif a == 'A0GK' then
        return true
    elseif a == 'A0GQ' then
        return true
    elseif a == 'A0GV' then
        return true
    elseif a == 'A0H2' then
        return true
    elseif a == 'A0H4' then
        return true
    elseif a == 'A0HA' then
        return true
    elseif a == 'A0HC' then
        return true
    elseif a == 'A0HL' then
        return true
    elseif a == 'A0J8' then
        return true
    elseif a == 'A0JZ' then
        return true
    elseif a == 'A0KN' then
        return true
    elseif a == 'A0KR' then
        return true
    elseif a == 'A0LB' then
        return true
    elseif a == 'A0LX' then
        return true
    elseif a == 'A0MG' then
        return true
    elseif a == 'A0MS' then
        return true
    elseif a == 'A0N3' then
        return true
    elseif a == 'A0NA' then
        return true
    elseif a == 'A0NP' then
        return true
    elseif a == 'A0PC' then
        return true
    elseif a == 'A0RG' then
        return true
    elseif a == 'A0RW' then
        return true
    elseif a == 'A0RY' then
        return true
    elseif a == 'A0T4' then
        return true
    elseif a == 'A0U1' then
        return true
    elseif a == 'A0U3' then
        return true
    elseif a == 'A0UB' then
        return true
    elseif a == 'A0VC' then
        return true
    elseif a == 'A0WM' then
        return true
    elseif a == 'A0WY' then
        return true
    elseif a == 'A0ZL' then
        return true
    elseif a == 'A10A' then
        return true
    elseif a == 'A10Z' then
        return true
    elseif a == 'A111' then
        return true
    elseif a == 'A11M' then
        return true
    elseif a == 'A13M' then
        return true
    elseif a == 'A145' then
        return true
    elseif a == 'A149' then
        return true
    elseif a == 'ANic' then
        return true
    elseif a == 'S007' then
        return true
    endif
    return false
endfunction

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
