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
tools/       맵 분석·패치용 파이썬 스크립트
CHANGELOG.md 버전별 수정 내역
```

## 맵 파일

| 파일 | 설명 |
|---|---|
| `maps/GS2vF_ver19.w3x` | 원본 (vF_8FKfix [R2 TEST +G5]) |
| `maps/GS2vF_ver19_portraitfix.w3x` | 2.0 패치 초상화 버그 수정본 |

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
