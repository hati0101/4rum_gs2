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
| `maps/GS2vF_ver19_portraitfix.w3x` | 2.0 패치 초상화 버그 수정본 |
| `maps/GS2vF_ver19_teamframe_test.w3x` | 초상화 수정본 + 팀원 현황 패널 (인게임 테스트용, 자동 시작) |

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

## 도구

Python 3만 있으면 됩니다 (외부 패키지 없음).

```bash
cd tools

# 맵에서 텍스트 데이터 추출 (맵 수정 후 커밋 전에 실행)
python extract.py ../maps/<맵>.w3x ../extracted

# 2.0 초상화 버그 일괄 수정: 모델이 바뀐 영웅에 초상화 모델(upor)을 모델과 같게 설정
python fix_portraits.py <입력>.w3x <출력>.w3x
```

- `w3x.py` — MPQ 아카이브 읽기/쓰기 (파일 교체 시 `(attributes)` CRC 갱신)
- `objdata.py` — 오브젝트 데이터(.w3u 등)와 `.wts` 문자열 파서

## 작업 흐름

1. 월드 에디터로 `maps/`의 맵을 수정하고 저장
2. `python tools/extract.py maps/<맵>.w3x extracted` 로 텍스트 데이터 갱신
3. `CHANGELOG.md`에 수정 내용 기록 후 커밋
