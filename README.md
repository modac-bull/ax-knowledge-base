# AX Knowledge Base

## 현재 운영 방식

매일 자동으로 `raw/daily/`에 리포트, `raw/links/`에 원문 링크 목록을 쌓습니다. 사용자는 `raw/user/`에 원하는 자료를 넣을 수 있습니다. **위키는 저장소에서 `$wiki-ingest`를 직접 호출할 때만 생성·갱신**합니다. 일일 자동화는 위키용 AI 요청을 추가로 하지 않습니다.

[수동 위키 사용 안내](docs/MANUAL-WIKI.md) · [위키](wiki/index.md) · [사용자 자료 추가](raw/user/README.md)

이전 `01-Daily/` 노트는 보존하며 초기 자료는 raw/daily에도 복사했습니다.

공개 AX 뉴스·개발 도구 릴리스를 수집해 한국어 일일 브리핑으로 저장하는 별도 Obsidian Vault입니다.

GitHub Actions → RSS·GitHub Releases → Gemini → `raw/daily/YYYY-MM-DD.md` → 로컬 Git Pull → Obsidian 순서로 동작합니다. 한국 시간 매일 오전 8시 전후 실행하며 GitHub 예약 지연이 가능합니다.

## 시작하기

1. [설정 가이드](docs/SETUP.md)에 따라 무료 Gemini 프로젝트와 `GEMINI_API_KEY` Secret을 준비합니다.
2. Actions의 **AX 데일리 브리핑**을 기본 브랜치 `develop`에서 수동 실행합니다.
3. `raw/daily/`와 `raw/links/`에 오늘의 한국 날짜 노트가 커밋되는지 확인합니다.
4. 같은 날 다시 실행해 추가 커밋이 없는지 확인합니다.
5. 저장소를 별도 폴더에 복제하여 Obsidian Vault로 엽니다.

## 운영 원칙

- 하루 한 파일이며 이미 소개한 원문 URL을 다시 요약하지 않습니다.
- 최근 72시간의 입력 최대 30개에서 최대 5개를 선택합니다.
- 새 소식이 없으면 Gemini 없이 상태 노트를 저장합니다. 모든 출처가 실패하면 저장하지 않습니다.
- 부분 수집 실패를 노트에 표시합니다. AI 출력 검증 실패 시 게시하지 않습니다.
- 자동화는 raw 리포트와 링크만 추가합니다. wiki는 수동 스킬로 관리합니다.
- 링크·날짜는 출처 데이터로 렌더링하며 AI의 해석과 사실 요약을 구분합니다.

## 무료 운영 조건

공개 저장소의 표준 GitHub 호스팅 러너와 Gemini API 무료 티어를 사용합니다. Gemini는 **결제를 연결하지 않은 무료 프로젝트의 키**를 사용하세요. 모델은 기본 `gemini-3.5-flash-lite`이며 제공 여부와 할당량은 계정별로 확인해야 합니다. 결제가 연결된 프로젝트에서는 같은 코드도 비용이 발생할 수 있습니다. 자동 유료 전환이나 대체 유료 모델 호출은 구현하지 않았습니다.

무료 API 입력은 제품 개선에 사용될 수 있으므로 공개 뉴스만 전송합니다. 계정·지역·모델 정책 변경으로 계속 무료 이용할 수 있다는 보장은 없습니다.

## 개발 검증

Python 3.12 권장, 외부 패키지 설치가 필요 없습니다.

```sh
python3 -m unittest discover -s tests -v
python3 scripts/briefing.py --collect-only
```

수집 전용 명령은 Gemini를 호출하거나 노트를 만들지 않고 개수와 실패 출처 이름만 출력합니다.

- [대시보드](00-Dashboard/Home.md)
- [설정](docs/SETUP.md) · [운영 및 복구](docs/OPERATIONS.md) · [보안](SECURITY.md)
- [Gemini 공식 요금](https://ai.google.dev/gemini-api/docs/pricing)
- [GitHub 예약 실행 제약](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)

기존 ChatGPT 브리핑 예약과는 별도 실행입니다. 기존 예약은 변경하지 않습니다.
