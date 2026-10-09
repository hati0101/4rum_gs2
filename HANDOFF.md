# GS2 스킬 범위 표시 시스템 기술 이관서

작성일: 2026-10-09 / 시스템명: GSRI / 현재 구현: v9 fog

## 1. 인수자가 먼저 알아야 할 상태

Warcraft III Reforged 유즈맵 GS2의 스킬 조준 미리보기 작업이다. 최신 구현은 **v9 fog**이며, 정적 검사와 맵 파일 설치까지 완료했다. **v9의 시야 밖 표시, 멀티플레이 동기화, 성능은 게임 검증 대기**다. v8 지형 대응은 사용자 재시험에서 정상이라는 답변을 받았다. 정식 배포 완료로 해석하면 안 된다.

가장 최근 작업은 v9 위험 검토이며, 발견한 초기화 시점/성능 문제는 아직 수정하지 않았다. 다음 작업은 새 영웅 추가보다 해당 보완과 다인 검증이다. 이번 이관서 작성으로 코드·맵·Git 커밋·원격 저장소는 변경하지 않았다.

Git 원격: https://github.com/hati0101/4rum_gs2

- 로컬 브랜치: `codex/skill-range-indicators`
- 현재 HEAD: `9fb8d701a44d6af249a3bfe2729d8e1812f0c449`
- 최초 ZIP 작성 당시 GSRI 작업은 미커밋이었다. 이후 Git 업로드 대상으로 소스·문서·리소스와 v9 manifest/coverage를 이 브랜치에 포함했다. 맵 바이너리·검사 실행 파일·work 자료는 ZIP으로 별도 전달한다. 인수 시 `codex/skill-range-indicators` 브랜치를 확인한다.
- 사용자 지칭은 **아키텍트**, 한국어 존댓말로 간결하게 답한다.

## 2. 목표와 확정 범위

시전 거리와 실제 공격 도달 거리를 분리해서 동시에 보여준다. 예를 들어 시전 거리 500, 투사체 도달 거리 1000이면 시전자 중심 반지름 500 원과 마우스 방향 길이 1000 경로를 함께 표시한다. 이 숫자는 설명 예시이며 실제 스킬 데이터 대신 사용하면 안 된다.

사용자는 전체 영웅을 한 번에 구현하지 않고 **레인저/어스레이크 + 노네/스펠 인보커 두 명**으로 먼저 시험하기로 했다. 루리엔의 부채꼴 스킬은 후속 확대 대상이다. 우측 아군 영웅 패널의 `GSTF_SkillOf` 매핑을 조사 기준으로 활용하지만 해당 UI를 수정한 작업은 아니다.

- 단일 대상/지점 대상: 시전 거리 원.
- 직선 투사체: 실제 이동 거리와 판정 폭에 대응하는 경로.
- 확산 공격: 시작 폭·끝 폭·도달 거리 기반 경계.
- 게임 자체가 제공하는 지면 광역 커서는 유지한다.
- 무제한 거리 및 즉발 자기 중심 시전은 제외한다.
- 특성 스킬까지 확대하는 것이 장기 목표이나 **현재 두 영웅의 7개 등록 스킬만 지원**한다. 전체 특성 지원 완료가 아니다.
- 시야 밖에도 범위선을 보여야 하며 적/지형 시야를 실제로 부여해서는 안 된다.

공통 명시적 제외: 디멘션 도어 `A0OB`, 데스 프로마이즈 `A0T1`, 카오스 위치 궁극기 `A11L`, 에인션트 트리(사용자 표현: 에이션트 트리, 이름 윗브) 궁극기 `A07I`. 이 영웅들은 이번 시험 대상 자체에서도 제외되어 있다. 레인저 E `A12Q`는 무제한 거리, D는 즉발이라 제외한다.

### 사용자 지정 필수 제외 규칙 — 후속 확대에서도 유지

| 사용자가 지정한 제외 대상 | ver93 식별자/대응 | 처리 |
|---|---|---|
| 디멘션 도어 | `A0OB` | 범위 표시 제외 |
| 데스프로마이즈 / 데스 프로마이즈 | `A0T1` | 범위 표시 제외 |
| 카오스위치 궁극기 | `A11L`, 타임 오브 데스 | 범위 표시 제외 |
| 윗브 궁극기 | 에이션트 트리/에인션트 트리, `A07I`, 네추럴링 | 범위 표시 제외 |
| 그 밖의 무제한 거리 스킬 | 위 네 개만으로 한정하지 않음 | 시전 원·방향 경로 모두 제외 |
| 즉발형 내 주변 자기 시전 스킬 | 자기 중심으로 바로 발동하며 조준하지 않는 스킬 | 범위 표시 제외 |

이 목록은 임시 두 영웅 테스트에만 적용하는 조건이 아니라 **사용자가 명시한 후속 구현 제약**이다. 전체 영웅·특성 스킬로 확대하더라도 자동 등록으로 되살리지 않는다. 단, 지점을 조준하는 일반 광역 스킬까지 자기 시전으로 묶어 제외하면 안 된다. 해당 스킬의 기존 게임 광역 커서는 유지한다.

현재 `tools/range_indicator.py`의 `EXCLUDE`에 네 ID가 있으며, 자기 시전 계열·Channel 대상 형식·사거리 필터를 함께 사용한다. 런타임은 `0 < castRange < 9999`를 요구한다. 이 임계값은 현재 구현 규칙일 뿐 모든 스킬의 의미를 자동 판별한다는 보장은 아니다. 최신본에서 ID 변경, 특성 파생/대체 능력, 트리거 기반 사실상 무제한 스킬을 다시 조사하고 의미 기준으로 제외를 유지한다. 최신본 ID를 확인하지 않고 ver93 ID만 복사해 제외 처리가 끝났다고 선언하지 않는다.

## 3. 환경·경로·식별자

아래 절대 경로는 작성 당시 PC 기준이다. 다른 PC에서는 조정한다.

| 용도 | 경로 |
|---|---|
| 프로젝트 루트 | `C:\Users\admin\OneDrive\문서\ChatGPT\warcraft\gs2-source` |
| 보존 원본 | `C:\Users\admin\Downloads\GS2vF_ver93.w3x` |
| 게임 설치/CASC | `D:\Warcraft III` |
| 게임 실행 파일 | `D:\Warcraft III\_retail_\x86_64\Warcraft III.exe` |
| 현재 게임 테스트 폴더 | `C:\Users\admin\OneDrive\문서\Warcraft III\Maps\Download\00_레인저_노네_범위테스트` |
| 이전 맵 보관 | `C:\Users\admin\OneDrive\문서\Warcraft III\Maps\Download\GS2_이전맵_보관_20261009` |
| 개발 산출물 | 프로젝트의 `maps/testing/` |

게임 테스트 폴더에는 이관서 작성 시 v9 맵 한 개가 있다. 같은 내부 제목의 맵이 여러 개여서 사용자가 혼동했던 이력이 있다. 파일명/폴더와 게임 채팅 `-range` 버전 문자열로 확인한다. 게임이 파일을 잡고 있으면 이동이 실패할 수 있으므로 강제 종료하거나 삭제하지 않는다.

| 파일 | SHA256 |
|---|---|
| 원본 `GS2vF_ver93.w3x` | `057f8ae676762de28c652603339d6a3f70a6831ddf7631eed638b41e61b2356f` |
| 지형 기준본 `GS2vF_ver93_range_Ranger_None_v8_terrain.w3x` | `8121e4b67009fc3008df60c54316825f98643121cc0cbcefa95972aab3a09e64` |
| 최신 후보 `GS2vF_ver93_range_Ranger_None_v9_fog.w3x` | `56d25b8cf45fec3165bf0b7cabf01bb4affe55fea9cd1ef77f4b1f8f25f1ef04` |

원본은 최신 운영 맵이 아니다. 최신본 적용 요청 시 최신 원본을 다시 확보하고 구조를 재검토해야 한다.

## 4. 기술 스택

| 구성 | 기술/용도 |
|---|---|
| 게임 로직 | JASS, Reforged `Blz*` 네이티브 |
| 에디터 저장 지원 | `war3map.wct`에 vJASS library와 initializer 삽입; JassHelper 필요 |
| 현재 렌더링 | 사용자 정의 lightning `GSRL`, `AddLightningEx`/`MoveLightningEx`/`SetLightningColor` |
| 선 리소스 | `Splats\LightningData.slk` 신규 행, `GSRI\white.tga` |
| 지형 높이 | 재사용 location + `MoveLocation` + `GetLocationZ` |
| 입력/갱신 | OSKEY, 마우스 이동/클릭, 채팅, 시전·선택 해제 이벤트, 64Hz 타이머 |
| 빌드·분석 | Python 3.14.4, 표준 라이브러리, 로컬 MPQ/CASC/오브젝트 파서 |
| 과거 모델 생성 | Node.js v24.15.0 + `war3-model` 4.0.1, MDL→MDX 생성·재파싱 |
| 정적 문법 검사 | `pjass.exe` + 설치 게임에서 추출한 `common.j`, `blizzard.j` |
| 파일 조작 | Windows PowerShell; 원본 보존, 새 출력 파일 생성 |

버전 값은 이번 PC에서 확인한 환경이며 최소 지원 버전 선언은 아니다. v9 manifest의 CASC 버전은 `3.0.0.24268`이다. v9 런타임에는 MDX 모델을 넣지 않는다. Node 도구는 과거 모델 재생성과 white.tga 생성에 쓰며, 기존 white.tga가 있으면 현재 맵 빌드는 Python으로 가능하다.

## 5. 이관할 파일

아래 경로는 프로젝트 루트 기준 상대 경로다.

| 파일/폴더 | 역할·이관 여부 |
|---|---|
| `HANDOFF.md` | 본 문서, 인수 시작점 |
| `src/RangeIndicator.template.j` | **수정 원본**. 현재 v9 런타임 |
| `src/RangeIndicator.j` | 생성된 등록 테이블을 포함한 JASS. 빌드 시 재생성되므로 여기에만 수정하지 않는다 |
| `src/range-audited-functions.json` | 원본 투사체 관련 함수 감사 지문 |
| `tools/range_indicator.py` | 분석·등록 테이블 생성·스크립트 삽입·MPQ 패키징·보존 검증 |
| `tools/w3x.py`, `objdata.py`, `casc.py` | 위 도구가 사용하는 MPQ/오브젝트/CASC 파서 |
| `tools/check_jass.py`, `game_scripts.py` | 문법 검사 및 게임 기본 스크립트 추출 |
| `tools/range_assets.cjs` | 모델/텍스처 생성 원본. v6~v8 표현 재현용 포함 |
| `assets/range/white.tga` | v9 필수 텍스처 |
| `assets/range/`의 나머지 MDL/MDX | 과거 표현과 재현 자료. v9 패키지에는 미사용 |
| `maps/testing/*v8_terrain.w3x`, `*v9_fog.w3x` | 지형 기준본·현재 후보 |
| 각 맵의 `.manifest.json`, `.coverage.csv` | 입력/출력 해시, 변경 멤버, 지원/제외 능력 목록 |
| `docs/RangeIndicator.md` | 버전별 기술 설명 |
| `docs/RangeIndicator-risk-v9.md` | 위험 검토와 배포 조건 |
| `work/ver93/` | 원본 추출 JASS/WTS 등 조사 자료 |
| `work/validator/pjass.exe`, `work/validator/game/` | 이번 검사 환경. 다른 PC 이관 시 출처·실행 가능 여부 확인 |
| `work/RangeIndicator_v7.template.j`, `work/RangeIndicator_v8.template.j` | 이전 런타임 스냅샷 |
| `work/model-tools/` | 격리된 npm 의존성. 필요하면 같은 버전으로 다시 설치 |

이 문서만으로 소스 파일이 전달되는 것은 아니다. **위 소스/도구/필수 리소스와 원본 맵을 함께 이관**한다. 소스는 `codex/skill-range-indicators` 브랜치, 원본·테스트맵·검사 실행 파일은 `GS2_GSRI_이관자료_20261009_v9.zip`을 사용한다. 최초 ZIP의 문서는 Git 업로드 전 상태를 기록한다.

## 6. 스킬 데이터와 계산 근거

| 영웅 / 입력 | 능력 ID | 시전 원 반지름 | 추가 표시 |
|---|---|---|---|
| 레인저 `Hvwd` Q | `A012` | 650 | 없음 |
| 레인저 W | `A0O8` | 1800 | 중심 이동 1170, 반경 120인 경로 |
| 레인저 R | `A11K` | 400 / 450 / 500 | 없음 |
| 노네 `Hkal` Q | `A08G` | 700 | 거리 825, 시작 반폭 125/150, 끝 반폭 200 |
| 노네 W | `A03V` | 650 | 없음 |
| 노네 E | `A08H` | 800 | 게임 기본 광역 커서 유지 |
| 노네 R | `A08J` | 750 | 없음 |

레인저 W는 원본 `Trig_Poison_Sniping_Actions`, `Trig_Poison_Sniping_Move_Actions`, `Trig_Poison_Sniping_Move_Func001C`, `GS2_AuditRangeRegister`를 조사했다. 30씩 39회 이동해 1170이고 등록된 반경은 120이다. 따라서 전체 폭 240, 양 끝에 반원이 있는 경로를 표시한다. 반원의 바깥쪽 끝은 중심 이동 끝보다 120 더 나간다. 대상 유닛의 충돌 반경까지 포함한 실제 엔진 피격 경계는 미검증이다.

노네 Q는 `ACbf` 기반이며 `Ucs3=825`, `Ucs4=200`이다. 시작 반폭 `aare`는 1레벨에서 기본 데이터 125를 상속하고 2~4레벨은 맵의 150을 사용한다. 전체 시작 폭은 250/300, 끝 폭은 400이다. 꼭짓점이 하나인 부채꼴로 단정하지 않고 넓어지는 통로형 경계로 구현했다. 기본값 상속을 누락해 전 레벨 150으로 처리했던 v5는 사용하지 않는다.

빌드 시 `war3map.w3a`와 `war3mapSkin.w3a`, WTS, 설치 게임 `AbilityData.slk`를 합쳐 조사한다. 원은 실행 중 `ABILITY_RLF_CAST_RANGE`를 읽는다. 형상 수치는 감사한 상수이며 완전 자동 추론 기능이 아니다. 이름 기반 두 영웅 필터, 대상 능력 계열 허용 목록, 자기 시전 제외 목록, 단축키/버튼 위치/범위 검사로 등록 대상을 제한한다. `A08H`의 E 키는 명시적 보정이다.

## 7. 런타임 구현

### 7.1 초기화와 입력

`main → GSRI_Init → GSRI_LoadData` 순서로 시작한다. 시전자 참조는 `udg_HeroPlayer[GetPlayerId(GetLocalPlayer())+1]`다. 로컬 플레이어가 선택한 살아 있는 Hvwd/Hkal만 표시한다.

`GSRI_OnKey`가 A~Z 입력을 받고 `GSRI_Find`가 실제 보유 능력의 등록 키를 찾는다. 같은 키가 여러 능력에 중복되면 취소한다. 최초 입력 즉시 탐색하고 이후 0.125초마다 갱신한다. 그 사이에도 해당 능력 존재와 허용 조건을 검사한다.

`GSRI_OnMouse`는 수신된 월드 좌표를 저장하고 클릭 시 취소한다. Enter/Esc/F1/F8/O, 시전 채널 시작, 선택 해제, 사망·포커스 상실·30초 경과 등에서도 숨긴다. 채팅 상태를 Enter 수신 여부로 토글해 고정하는 방식은 사용하지 않는다.

### 7.2 방향 보간

`GSRI_PERIOD=0.015625`, `GSRI_TURN_BLEND=0.30`이다. 각 갱신에서:

```text
target = atan2(mouseY - casterY, mouseX - casterX)
delta = atan2(sin(target - yaw), cos(target - yaw))
yaw = yaw + delta * 0.30
```

±π 경계에서 최단 방향을 따른다. 최초 표시는 바로 현재 수신 방향을 쓰며 취소 시 보간 상태를 초기화한다. 정지 목표에는 계산상 약 141ms 이내 95% 수렴하지만, 마우스 이벤트 전달 지연은 별도다. 실제 발사 방향이나 마우스 명령을 변경하지 않는다.

### 7.3 지형을 따르는 경계

`GSRI_Draw`가 원/경로를 만들고 `GSRI_Line → GSRI_Segment`에서 짧은 선으로 나눈다. 직선 구간 길이는 48 이하이며 원은 `floor(2πr/48)+1`, 최대 256조각이다. 각 조각의 양 끝·중간 지형 높이에 12를 더한다.

끝/중간 높이 차이가 64를 넘거나 중간점이 직선 높이 보간에서 12보다 크게 벗어나면 해당 조각을 숨긴다. 절벽 벽면까지 그리는 투영이 아니며 절벽의 짧은 빈 구간은 의도된 동작이다. 선의 단절은 투사체가 막힌다는 뜻이 아니다. 수면·다리·장식물 윗면 대응은 미검증이다.

### 7.4 v9 시야 밖 렌더링

lightning 풀 384개를 모든 클라이언트에 같은 순서로 생성한다. 0~255는 원, 256~383은 경로에 사용한다. `AddLightningEx("GSRL",false,...)`와 `MoveLightningEx(...,false,...)`의 시야 검사 옵션을 꺼서 선을 표시한다. 색상·투명도와 좌표만 로컬 표시 상태에 따라 갱신한다.

`GSRL`의 `Width=3`, `NoiseScale=0`, `AvgSegLen=32`, `TexCoordScale=1`, `Duration=1000000`이며 흰 텍스처를 색으로 변조한다. 시야 제공/안개 해제 함수는 없다. 새 GSRL 행만 추가하고 기존 lightning 셀은 보존한다.

좌표가 같은 조각은 높이 조회·선 이동을 생략한다. 다만 원의 삼각함수 계산과 구간 루프 자체는 아직 매번 수행한다. 정지 중 지형이 변형되면 재표시 또는 좌표 변경 전까지 캐시가 오래된 높이를 유지할 수 있다.

## 8. 빌드와 최신 맵 이식

### 재생성 명령

PowerShell에서 프로젝트 루트로 이동한 뒤 실행한다. 새 출력 이름을 사용해야 한다.

```powershell
Set-Location 'C:\Users\admin\OneDrive\문서\ChatGPT\warcraft\gs2-source'
$env:PYTHONIOENCODING = 'utf-8'
python tools/range_indicator.py 'C:\Users\admin\Downloads\GS2vF_ver93.w3x' 'maps/testing/GS2vF_ver93_range_next.w3x' --game 'D:\Warcraft III'
if ($LASTEXITCODE -ne 0) { throw 'Map build failed' }
python tools/check_jass.py work/validator 'maps/testing/GS2vF_ver93_range_next.w3x'
if ($LASTEXITCODE -ne 0) { throw 'JASS validation failed' }
Get-FileHash 'maps/testing/GS2vF_ver93_range_next.w3x' -Algorithm SHA256
```

텍스처/과거 모델을 재생성해야 할 때만 실행한다. 의존성이 없으면 먼저 같은 버전을 설치한다.

```powershell
npm install --prefix work/model-tools war3-model@4.0.1
node tools/range_assets.cjs work/model-tools/node_modules/war3-model
```

검사 기본 스크립트를 새 게임 설치에서 추출하려면:

```powershell
New-Item -ItemType Directory -Force work/validator/game | Out-Null
python tools/game_scripts.py 'D:\Warcraft III' work/validator/game
```

`pjass.exe`는 `work/validator/`에 별도로 필요하다. 자동 다운로드나 자동 설치 기능은 없다. 검사 통과가 실제 게임·멀티플레이 통과는 아니다.

### 삽입·보존 방식

빌더는 입력/기존 출력 덮어쓰기를 거부한다. 깨끗한 원본에만 적용하며 GSRI가 이미 있으면 중단한다. 템플릿의 테이블 자리표시자를 생성 코드로 바꾸고 globals와 함수를 `war3map.j`에 삽입한 뒤 main 끝에 초기화 호출을 추가한다. `war3map.wct`에는 `library GSRangeIndicator initializer GSRI_Init`를 넣는다.

MPQ의 신규/변경 블록과 테이블을 덧붙이고 CRC 속성·import 목록을 갱신한다. PKWARE 압축 listfile은 이 파서에서 지원하지 않아 원본 바이트를 유지한다. 신규 경로는 import 목록에 등록한다. v9 변경 멤버는 다음 여섯 개다.

```text
war3map.j
war3map.wct
war3map.imp
Splats\LightningData.slk
GSRI\white.tga
(attributes)
```

변경 멤버 재읽기, 미변경 1061개 원본 블록의 메타데이터/압축 바이트 동일성, 원본 불변을 검사한다. v8의 미변경 블록 수 1062와 혼동하지 않는다.

### 최신본 적용 전 확인

1. 최신 원본을 별도 보관하고 SHA256을 기록한다. 현재 파일로 원본을 덮어쓰지 않는다.
2. `udg_HeroPlayer`, `GSTF_SkillOf`, 두 영웅/7개 능력 ID, 이름/단축키, 시전/판정 수치를 실제 최신 파일에서 다시 확인한다.
3. 빌더는 네 투사체 관련 함수 지문과 노네 Q 필드를 비교한다. 다르면 중단되며, 확인 없이 지문만 갱신해서 우회하지 않는다.
4. 최신본에 기존 LightningData.slk가 없거나 구조/ID가 다르면 재검토한다. 현재 도구는 ver93 형식에 맞춘 제한적 패처다.
5. 에디터 재저장 시 JassHelper가 필요하다. initializer 보존, import 보존, JASS 검사, 실제 게임 재시험을 수행한다.
6. 현재 위험 보완과 다인 시험이 끝나기 전 전체 영웅이나 정식 배포본으로 확대하지 않는다.

## 9. 진행 이력과 실패한 방식

| 버전/단계 | 내용 | 근거·상태 |
|---|---|---|
| 초기 프로토타입 | MDX 텍스처 경로 문제 | 수정 후 재생성. 초기 파일을 기준으로 쓰지 않는다 |
| v2 | 레인저 Q/W/R, 원·경로 표시 | 사용자: 첫 번만 표시, 재사용 실패, W 형상/폭 이상 |
| v3~v5 | 채팅 상태·모델 변환 정리, 노네 조사 | 중간 후보. v5 노네 Q 1레벨 상속 폭 누락 |
| v6 | 단일 형상 모델, 노네 레벨별 폭 반영 | 사용자: 노네 Q 표시·반복 사용·채팅 통과. 방향 움직임 끊김 보고 |
| v7 | 최단 각도 보간·64Hz, 탐색 8Hz | 단일 평면 모델이 높이 차이를 따르지 못함 |
| v8 | 경계 분절·지형 높이 샘플링 | 재시험 후 사용자 정상 확인. 시야 밖 표시 요구 추가 |
| v9 | 분절 lightning 및 시야 검사 해제 | 빌드/문법/보존 검사 통과. 안개·멀티·성능 게임 검증 대기 |
| 위험 검토 | 초기화 등록 시점·연산량·검증 누락 식별 | 문서 작성만 완료, 보완 코드 미적용 |

반복하면 안 되는 접근: Enter만으로 채팅 상태를 토글해 유지하기, 긴 모델 전체에 시전자 높이 하나 적용하기, 재질 Unfogged만으로 전장의 안개 처리가 끝났다고 보기, 기본 오브젝트 상속값 생략하기, 문법 검사만으로 게임 정상이라고 선언하기.

## 10. 확인된 검증과 남은 위험

정적 검토에서 원본 함수 4618개 중 main의 초기화 호출 추가만 기존 함수 변경으로 확인했다. 신규 GSRI 함수 19개가 설치본과 생성 소스에서 일치했다. 능력·스킨 능력·유닛·지형·맵 설정 파일은 원본과 동일하다. 기존 LightningData 셀 293개를 유지하고 14셀 한 행을 추가했다. 피해·이동 명령·경제·시야 부여 호출은 추가하지 않았다.

| 위험 | 현재 판단 | 다음 조치 |
|---|---|---|
| 초기화 중 마우스 이벤트 등록 | 과거 엔진 버전에서 유사 경로 충돌 재현 보고. 현 빌드에서 직접 재현하지 않음 | 게임 시작 후 등록으로 지연, 다인 로딩 반복 시험 |
| 성능 | 고정 풀 384개 + 64Hz. 레인저 W 최대 335구간, 초당 21440회 구간 방문/64320회 높이 조회 가능 | 원/경로 변화 없는 경우 상위 계산부터 생략, 원본 대비 프레임시간 측정 |
| 동기화 | 동등한 생성 경로와 로컬 렌더 상태 분리. 멀티 안전성 미확정 | 2인 이상 표시·채팅·선택·포커스 교차 시험 |
| 실제 피격 일치 | 명목 경로 표시이며 대상 충돌 크기/네이티브 확산 경계 미검증 | 경계 안팎 표적 실측 |
| 조준 지연 | 보간으로 순간적인 선/발사 방향 차이 가능 | 급회전 즉시 시전 사례 검사 |
| 메모리 | 반복 시전 중 추가 생성 경로 없음. 고정 자원 유지 | 장시간 게임 실측 |
| 비활성화 | 게임 중 완전 OFF 토글 없음. 취소는 숨기기만 함 | 긴급 비활성화 설계; 현재 복구는 원본으로 재시작 |
| 이식/에디터 | 특정 ver93 구조 의존, 재저장 미검증 | 최신본 재감사·JassHelper 재저장 QA |

성능 숫자는 소스 계산량이고 FPS 실측값이 아니다. 현재 한 클라이언트는 본인 영웅만 표시하므로 이를 참가자 수로 단순 곱하지 않는다. 시야 밖 적을 조회하지 않지만 선의 높이·절벽 단절로 미탐색 지형 정보가 표현될 수 있다. 저장/불러오기·리플레이·관전자 역시 검증하지 않았다.

## 11. 다음 작업 순서와 시험 항목

1. v9 실행 시 `-range`가 `GSRI v9 fog`인지 확인한다. 안개/검은 미탐색 영역에서 선만 표시되고 적 정보는 드러나지 않는지 시험한다.
2. 초기화 중 마우스 이벤트 등록을 게임 시작 이후로 옮기는 최소 보완을 한다. 무관한 로직은 리팩터링하지 않는다.
3. 원 계산의 위치/반지름 캐시, 경로의 방향/위치 캐시로 불필요한 전체 루프를 줄인다. 보간 자체를 느리게 만들어 해결하지 않는다.
4. 레인저 Q/W/R, 노네 Q/W/E/R를 표시→취소→재표시 5회, 채팅 후 반복, 실제 시전 후 반복한다. 노네 Q는 1레벨과 2레벨 이상을 비교한다.
5. 평지/경사/절벽/시야 경계, 급회전, 사망/재선택/Alt-Tab을 검사한다. 선 단절을 공격 판정으로 오해하지 않도록 확인한다.
6. 최소 2인 후 실제 인원으로 로딩·전투·장시간 시험을 한다. 충돌/접속 분리/다른 사람 표시 노출/기존 번개 변화가 없는지 확인한다.
7. 통과하면 최신 원본에 이식하고 같은 검증을 반복한다. 루리엔·다른 특성·전체 영웅 확대는 그 다음이다.

## 12. 참고 자료

- 내부 상세 구현: `docs/RangeIndicator.md` — 버전별 기록이므로 구버전 설명을 현 구현으로 혼동하지 않는다.
- 내부 위험 검토: `docs/RangeIndicator-risk-v9.md`.
- [OSKEY 이벤트 제작자 설명](https://www.hiveworkshop.com/threads/oskey-player-key-event.319903/) — 채팅/프레임 포커스와 입력 이벤트.
- [마우스 좌표 동기화 지연 보고](https://us.forums.blizzard.com/en/warcraft3/t/please-give-us-blzgetlocalmousescreenposition/36519).
- [지형 기울기 효과 구현 예](https://www.hiveworkshop.com/threads/terrain-aligned-special-effect.358171/) — v8 참고, 현재 v9는 lightning 끝점 높이 사용.
- [사용자 정의 LightningData 작성](https://www.hiveworkshop.com/threads/how-to-customise-lightning-effects.203171/).
- [AddLightningEx API 설명](https://lep.nrw/jassbot/doc/AddLightningEx) — checkVisibility 옵션.
- [초기화 중 마우스 이벤트 충돌 최소 재현](https://us.forums.blizzard.com/en/warcraft3/t/20323175-mouse-events-ub-crash/37517).
- [후속 마우스 충돌 보고 및 작성자 정정](https://us.forums.blizzard.com/en/warcraft3/t/mouse-events-and-getters-are-causing-crashes/37954) — 일반 게임 중 충돌 주장은 자기 코드 문제 가능성으로 수정되었다. 모든 마우스 API가 확정적으로 충돌한다고 인용하지 않는다.

외부 자료는 구현 근거/기존 보고이며 현 게임 버전에서 직접 검증한 결과를 대신하지 않는다. 자료 이관 후에는 본 문서 → 최신 소스 → manifest → 위험 검토 순서로 확인하고, 게임 검증 전 완료/배포 가능 상태로 승격하지 않는다.
