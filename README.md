# 가디언 스피리츠 II (Guardian Spirits II) — 4rum

워크래프트 3 유즈맵 **가디언 스피리츠 II** (5 vs 5, 가디언 vs 다크니스)의 수정·개선 저장소입니다.

- 원작: 4rum Community ([4rum.co.kr](http://4rum.co.kr))
- 대상 게임 버전: Warcraft III: Reforged 2.0 이상 (리포지드 월드 에디터로 편집)

## 구성

```
maps/        맵 파일 (.w3x, Git LFS)
extracted/   맵에서 추출한 텍스트 데이터 — 변경 내용을 git diff로 보기 위함
  war3map.j    맵 스크립트
  war3map.wts  트리거 문자열
  heroes.md    진영별 영웅 목록 (모델·초상화 정보 포함)
src/         맵에 넣는 JASS 코드
  TeamFrame.template.j  팀원 현황 패널 원본 (직접 수정하는 파일)
  TeamFrame.j           궁극기 표가 채워진 결과물 (teamframe.py gen 으로 생성)
tools/       맵 분석·패치용 파이썬 스크립트
CHANGELOG.md 버전별 수정 내역
```

## 맵 파일

| 파일 | 설명 |
|---|---|
| `maps/GS2vF_ver19.w3x` | 원본 (vF_8FKfix [R2 TEST +G5]) |
| `maps/release/GS2vF_ver52_fix.w3x` | **배포용 (최신, ver52 기준)** — ver52 + 천둥 일격 기반 스킬 4레벨 피해 제한 수정 |
| `maps/GS2vF_ver52.w3x` | ver52 원본 (공동 작업자 버전: ver19 patch3 + 밸런스·툴팁·스크립트 수정) |
| `maps/release/GS2vF_ver19_patch4.w3x` | 배포용 (ver19 기준) — patch3 + 천둥 일격 기반 스킬 4레벨 피해 제한 수정 |
| `maps/release/GS2vF_ver19_patch3.w3x` | 배포용 — patch2 + 팀원 패널 Q W E R 스킬·패시브·궁극기 강조·부활 시간 |
| `maps/release/GS2vF_ver19_patch2.w3x` | 배포용 — patch1 + 진행 투표 제거, 선택판 랜덤 버튼, -랜덤 버그 수정 |
| `maps/release/GS2vF_ver19_patch1.w3x` | 배포용 — 수정본 + 팀원 현황 패널 + 모드 선택 팝업 + 영웅 선택판 (테스트 기능 없음) |
| `maps/GS2vF_ver19_fixed.w3x` | 버그 수정본 (2.0 초상화, 평화 기반 스킬 무적, 천둥 일격 기반 피해 제한, -랜덤) — 다른 작업의 기준 맵 |
| `maps/GS2vF_ver19_teamframe_test.w3x` | 수정본 + 팀원 현황 패널·모드 선택·영웅 선택판 (인게임 테스트용: 자동 시작, 자기 영웅도 표시, 테스트 명령어 `-gstest`/`-gskill`) |

## 배포 맵 만들기

```bash
cd tools
python teamframe.py gen ../maps/GS2vF_ver19_fixed.w3x
python teamframe.py inject ../maps/GS2vF_ver19_fixed.w3x ../maps/release/<이름>.w3x --autostart --pickflow
```

배포 맵은 초기화 호출이 스크립트(main)에 직접 들어가 있어 그대로 실행됩니다.
월드 에디터에서 열어 저장할 경우에는 맵 초기화 트리거에 사용자 지정 스크립트
`call GSTF_Init()`, `call GSPF_Init()` 두 줄을 추가해야 합니다.

## 팀원 현황 패널 (GSTF)

화면 오른쪽 벽에 팀원 영웅의 아이콘·레벨·체력·마나·궁극기 상태를 표시합니다 (LoL 스타일).

- 궁극기: 미습득 = 흐림 / 쿨다운 = 남은 초 표시 / 마나 부족·사망 = 반투명 / 준비 = 밝게 + 초록 점
- 설정: `src/TeamFrame.template.j` 상단 함수 (`GSTF_ShowSelf` 자기 영웅 표시 여부, 크기, 위치)

맵에 넣기:

```bash
cd tools
python teamframe.py gen ../maps/<맵>.w3x                              # 궁극기 표 생성 -> src/TeamFrame.j
python teamframe.py inject ../maps/<맵>.w3x ../maps/<출력>.w3x          # 맵 헤더 스크립트에 코드 추가
```

`inject`는 코드를 맵 사용자 지정 스크립트(헤더)에 넣습니다. 월드 에디터에서
**맵 초기화 트리거 하나에 사용자 지정 스크립트 `call GSTF_Init()`** 를 추가해야 동작합니다.
(`--autostart`는 트리거 없이 바로 테스트하기 위한 옵션이며, 에디터에서 다시 저장하면 사라집니다.)

테스트 빌드: `inject ... --autostart --show-self --test`
- `-gstest`: 내 팀 빈 슬롯 4곳에 같은 진영 영웅 생성 (Lv2 궁 미습득 / Lv4 체력·마나 감소 / Lv6 궁 준비 / Lv6 궁 쿨다운 30초), 채팅에 궁극기 이름·습득 여부 출력
- `-gskill`: 봇1 처치 (사망 표시 확인)
- 월드 에디터의 맵 테스트(Ctrl+F9)는 스크립트를 다시 만들어 자동 시작이 빠지므로, 게임에서 사용자 지정 게임으로 실행

## 도구

Python 3만 있으면 됩니다 (외부 패키지 없음).

```bash
cd tools

# 맵에서 텍스트 데이터 추출 (맵 수정 후 커밋 전에 실행)
python extract.py ../maps/<맵>.w3x ../extracted

# 2.0 초상화 버그 일괄 수정: 모델이 바뀐 영웅에 초상화 모델(upor)을 모델과 같게 설정
python fix_portraits.py <입력>.w3x <출력>.w3x

# 이후 패치에서 생긴 능력 필드의 레벨별 원본값 무력화
#  - 평화 기반: 2레벨 이상 시전 시 1초 무적 (Etq4)
#  - 천둥 일격 기반: 4레벨 이상 총 피해 1400 제한 (Htc5)
python fix_new_fields.py <입력>.w3x <출력>.w3x

# 같은 유형의 숨은 필드 찾기 (설치된 게임 데이터 필요)
python audit_stock_levels.py <맵>.w3x "D:\Warcraft III"

# -랜덤 트리거 수정 (선택판 랜덤 버튼 연결, 다크니스 범위 버그, 중복 영웅)
python patch_random.py <입력>.w3x <출력>.w3x

# 게임 원본 common.j/blizzard.j 로 문법 검사 (pjass)
python check_jass.py <pjass 폴더> <맵>.w3x
```

- `w3x.py` — MPQ 아카이브 읽기/쓰기 (파일 교체 시 `(attributes)` CRC 갱신)
- `objdata.py` — 오브젝트 데이터(.w3u 등)와 `.wts` 문자열 파서

## 작업 흐름

1. 월드 에디터로 `maps/`의 맵을 수정하고 저장
2. `python tools/extract.py maps/<맵>.w3x extracted` 로 텍스트 데이터 갱신
3. `CHANGELOG.md`에 수정 내용 기록 후 커밋
