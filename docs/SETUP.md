# 설정 가이드

## 1. 무료 Gemini 키

1. [Google AI Studio](https://aistudio.google.com/apikey)에서 결제를 연결하지 않은 무료 프로젝트를 선택하고 API 키를 발급합니다.
2. [공식 요금표](https://ai.google.dev/gemini-api/docs/pricing)에서 모델의 무료 티어와 계정 할당량을 확인합니다. 기본값은 `gemini-2.5-flash-lite`입니다.
3. [저장소 Secret 설정](https://github.com/modac-bull/ax-knowledge-base/settings/secrets/actions)에서 **New repository secret**을 선택합니다.
4. 이름 `GEMINI_API_KEY`, 값은 발급받은 키로 등록합니다. 채팅·파일·스크린샷에 키를 올리지 마세요.
5. 모델 변경이 필요하면 같은 화면의 Variables에 `GEMINI_MODEL`을 추가합니다. 무료 제공 여부를 먼저 확인하세요.

키가 없고 새 소식이 있으면 생성 작업은 실패합니다. 무료 한도 초과도 실패 처리하며 유료 API로 대체하지 않습니다.

## 2. GitHub Actions 확인

1. [Actions](https://github.com/modac-bull/ax-knowledge-base/actions)에서 **검증** 결과를 확인합니다.
2. **AX 데일리 브리핑** → **Run workflow** → 브랜치 `develop` → **Run workflow**를 선택합니다.
3. 성공 후 `01-Daily/`의 한국 날짜 파일과 새 커밋을 확인합니다. 신규 뉴스가 있다면 `status: generated`, 없다면 `status: no-news`입니다.
4. 같은 날 다시 실행합니다. 수집·Gemini 호출을 생략하며 추가 커밋이 없어야 합니다.
5. 이후 매일 UTC 23:00, 한국 시간 다음 날 08:00 전후 실행합니다.

기본 브랜치 외 수동 실행은 건너뜁니다. 브랜치 보호가 자동 커밋을 차단하면 권한을 무작정 넓히지 말고 별도 게시 브랜치/PR 방식으로 변경하세요.

## 3. 별도 Obsidian Vault 연결

기존 개인 Vault가 아닌 새 폴더에서 실행합니다. 아래는 예시 경로입니다.

```sh
mkdir -p ~/Documents/AX
git clone https://github.com/modac-bull/ax-knowledge-base.git ~/Documents/AX/ax-knowledge-base
```

Obsidian의 보관함 관리에서 **Open folder as vault / 폴더를 보관함으로 열기**를 선택해 `~/Documents/AX/ax-knowledge-base`를 엽니다. `00-Dashboard/Home`에서 탐색을 시작합니다.

브리핑 생성 후 해당 폴더에서 `git pull --ff-only`를 실행하면 노트가 들어옵니다. 저장소의 기본 브랜치 `develop`이 체크아웃되었는지 확인하세요.

## 4. 무료 자동 Pull

Obsidian 설정 → 커뮤니티 플러그인에서 **Git / Obsidian Git**을 검색하여 공식 목록의 플러그인을 설치·활성화합니다. [플러그인 공식 문서](https://publish.obsidian.md/git-doc/)에서 현재 버전의 이름을 확인하며 다음 동작을 설정합니다.

- 시작할 때 Pull.
- 10~30분 주기로 Pull.
- 자동 커밋·Push는 처음에는 끔. 로컬 메모는 수동 커밋.

Git 명령 사용이 가능해야 합니다. 공개 저장소 Pull에는 개인 토큰이 필요 없습니다. 자신의 메모 Push를 원하면 GitHub에서 권장하는 Git 인증을 별도로 설정하세요. 토큰을 원격 URL이나 노트에 넣지 마세요. 모바일 지원은 OS 및 플러그인 버전별로 다르므로 우선 데스크톱에서 확인하세요.

기기가 꺼져 있거나 Obsidian이 종료되면 로컬 동기화는 다음 실행 때 이뤄집니다. `.obsidian/`은 제외되어 플러그인 설정은 다른 기기에 자동 복제되지 않습니다.
