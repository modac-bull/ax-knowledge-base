"""세션 알림 또는 Git 인덱스 검증. 네트워크·AI 호출과 파일 수정 없음."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from wiki import pending, check

root = Path(__file__).resolve().parents[1]
if '--staged' in sys.argv:
    # 작업 폴더가 아닌 실제 커밋 예정 버전을 검사한다.
    with tempfile.TemporaryDirectory() as temporary:
        subprocess.run(['git', 'checkout-index', '--all', '--prefix=' + temporary + '/'], cwd=root, check=True)
        errors = check(Path(temporary))
        if errors:
            print('\n'.join(errors), file=sys.stderr)
            sys.exit(1)
else:
    json.load(sys.stdin)
    count = len(pending(root))
    context = '미처리 raw 자료 %d개. 위키 갱신은 사용자 명시 호출 $wiki-ingest로만 수행합니다.' % count
    print(json.dumps({'hookSpecificOutput': {'hookEventName': 'SessionStart', 'additionalContext': context}}, ensure_ascii=False))
