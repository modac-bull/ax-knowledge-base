# raw 수집과 수동 위키

## 매일 자동으로 하는 일

Gemini 리포트를 raw/daily/YYYY-MM-DD.md에 발행하고, 후보 원문 링크를 raw/links/YYYY-MM-DD.md에 함께 저장합니다. 원문 전문은 저장하지 않습니다. 위키 생성 API는 추가로 호출하지 않습니다. 전환 이전 리포트도 raw/daily에 보존했습니다. 이전 노트의 링크 목록은 리포트에 실제 포함된 링크로만 복원할 수 있습니다. 볼트의 시작 페이지는 wiki/index.md입니다.

## 원하는 자료 추가

raw/user/에 공개 가능한 자료를 넣습니다. 링크만 추가하려면 `python3 scripts/wiki.py add-url 'https://example.com/article'`을 실행하거나 Markdown에 링크를 직접 적습니다. 이 명령은 자료를 다운로드하거나 Gemini를 호출하지 않습니다. GitHub 웹에서 직접 추가하거나 로컬 변경을 커밋·Push하면 됩니다.

## 위키 수동 실행

1. 저장소를 Pull하고 그 폴더를 Codex 프로젝트로 엽니다. 부모 폴더가 아닌 이 저장소 자체를 엽니다.
2. 다음을 입력합니다: `$wiki-ingest 미처리 자료를 위키로 정리해주세요.`
3. 특정 자료만 처리하려면 `$wiki-ingest raw/user/문서.md만 처리해주세요.`처럼 요청합니다.
4. 결과의 근거·원문 열람 여부·변경된 판단을 검토한 후 원하는 경우 커밋·Push를 요청합니다.

스킬은 .agents/skills/wiki-ingest에 저장되어 있으며 명시 호출 전용입니다. 목록에 나타나지 않으면 프로젝트를 다시 열고 해당 SKILL.md 경로를 직접 지정해 실행할 수 있습니다. 별도 Gemini/OpenAI API 키를 요구하지 않지만, 실행 중인 Codex 또는 에이전트의 구독·사용 한도는 적용됩니다.

처리 완료된 자료는 wiki/processed.json에 내용 해시와 연결된 출력 경로를 기록합니다. 같은 자료는 재처리하지 않고 내용이 바뀌면 다시 후보가 됩니다. 초기에는 한 번에 최대 10개만 처리합니다. 링크만 있는 자료는 웹 열람이 가능할 때 원문을 읽으며, 접근하지 못하면 확인 불가로 표시하거나 보류합니다. 이미지·PDF 등은 해당 형식 열람 도구가 있어야 처리할 수 있습니다.

## 훅과 검증

.codex/hooks.json은 SessionStart 때 미처리 개수와 수동 호출 방법만 알립니다. 원문 내용은 세션에 주입하지 않으며 위키 작성이나 커밋은 하지 않습니다. 저장소 .codex 설정이 신뢰된 프로젝트에서만 로드됩니다. 훅이 작동하지 않아도 스킬과 아래 명령으로 동일하게 사용할 수 있습니다. 전역 설정과 기존 사용자의 훅은 변경하지 않습니다.

```sh
python3 scripts/wiki.py pending
python3 scripts/wiki.py check
python3 -m unittest discover -s tests -v
```

선택적으로 로컬 Git 커밋 전 검증을 설치할 수 있습니다. 기존 core.hooksPath가 있다면 덮어쓰지 말고 기존 훅에 검증 명령을 합치세요.

```sh
git config --get core.hooksPath
# 기존 설정이 없을 때만 실행
git config --local core.hooksPath .githooks
```

pre-commit은 작업 폴더가 아닌 스테이징된 파일을 검사합니다. CI도 위키 링크와 처리 기록을 검사합니다. 이 검사는 출처가 존재하는지 확인하며 AI 주장의 정확성·프롬프트 주입 방어를 보장하지 않습니다. 수동 실행 결과를 검토하세요.

훅은 [공식 Codex 훅 형식](https://learn.chatgpt.com/docs/hooks)을 사용합니다. 다른 에이전트는 스킬 지침을 직접 읽게 할 수 있지만 Codex 훅을 그대로 사용할 수 있다고 가정하지 마세요.
