# AX 브리핑 구현 계획

> 실행 방식: 현재 세션에서 직접 실행하며 테스트 우선 개발과 최종 독립 검토를 적용한다.

**목표:** RSS 및 Releases를 한국어 일일 노트로 생성한다.
**구조:** Python 표준 라이브러리로 네트워크 수집, 검증, Markdown 생성을 분리한다.
**기술:** Python 3.12, unittest, Gemini REST, GitHub Actions.
**설계:** `docs/superpowers/specs/2026-10-30-ax-briefing-design.md`

## 공통 제약

한국 날짜, 최근 72시간, 입력 최대 30개, 출력 최대 5개, API 최대 3회 시도. 공개 자료만 사용하고 API 오류 본문을 로그에 출력하지 않는다. 자동 커밋은 일일 노트 한 파일만 포함한다.

## 검토 초점

날짜 경계, 날짜 없는 피드, 리디렉션, Gemini 차단·잘림 응답, 원격 브랜치 충돌을 확인한다.

## 작업 1: 수집과 정규화

- [ ] `tests/test_briefing.py`에 RSS·Atom·릴리스, 추적 URL, KST 날짜, 미래·오래된 날짜, 네트워크 제한 테스트를 작성한다.
- [ ] 테스트 실패를 확인한다.
- [ ] `scripts/briefing.py`에 `canonical_url`, `parse_feed`, `parse_releases`, `collect`, `request_bytes`를 구현한다. 출처는 `config/sources.json`으로 관리한다.
- [ ] `python3 -m unittest discover -s tests -v`로 통과를 확인한다.

## 작업 2: 검증과 일일 파일

- [ ] 위조 출처·중복·모델 종료 상태·비한국어·주입 텍스트 거부, 기존 날짜 API 미호출, 수집 실패 시 파일 미생성, 재실행 중복 방지 테스트를 작성하고 실패를 확인한다.
- [ ] `validate_summary`, `generate`, `run`을 구현한다. 노트의 해시 메타데이터에서 중복을 읽고 검증 후 파일을 독점 생성한다.
- [ ] 전체 테스트 통과와 실제 출처 수집을 확인한다.

## 작업 3: 실행과 안내

- [ ] SHA 고정 Actions, 읽기 전용 테스트, 기본 브랜치 전용 수동·예약 생성과 명시적 파일 커밋을 구성한다.
- [ ] 한국어 README, 설정·운영·보안 안내와 Vault 폴더를 작성한다.
- [ ] 전체 테스트, 독립 검토 후 GitHub 연결 도구로 게시한다. Secret이 없으면 실제 Gemini 성공은 미검증으로 보고한다.

## 실행 기록

- 초기 원격 저장소는 README만 존재하고 기본 브랜치는 `develop`이다. 기존 체크아웃이 없는 별도 폴더에서 구현하므로 기존 코드와 충돌하지 않는다.
- 사용자의 ‘다음’을 승인된 설계의 구현 진행으로 해석한다. 저장소 공개 생성 및 자동화 구성은 이미 승인된 범위다.
