"""수동 위키의 자료 목록과 검증만 담당한다. AI·네트워크 호출 없음."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit


def inside(root, name, area):
    root = root.resolve()
    path = root / name
    if path.is_symlink() or not path.resolve().is_relative_to(root / area):
        raise ValueError('허용 영역 밖의 경로')
    return path


def fingerprint(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def state(root):
    path = root / 'wiki/processed.json'
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}


def pending(root):
    done = state(root)
    result = []
    for path in sorted((root / 'raw').rglob('*')):
        if path.is_file() and path.name != 'README.md' and not path.name.startswith('.'):
            inside(root, path.relative_to(root).as_posix(), 'raw')
            name = path.relative_to(root).as_posix()
            if done.get(name, {}).get('sha256') != fingerprint(path):
                result.append(name)
    return result


def add_url(root, url):
    p = urlsplit(url)
    if p.scheme != 'https' or not p.hostname or p.username or p.password or any(c.isspace() for c in url) or any(c in url for c in '<>'):
        raise ValueError('공개 가능한 HTTPS 링크를 입력하세요')
    path = root / 'raw/user' / (hashlib.sha256(url.encode()).hexdigest()[:20] + '.md')
    inside(root, path.relative_to(root).as_posix(), 'raw')
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        with path.open('x', encoding='utf-8') as output:
            output.write('# 사용자 자료\n\n<' + url + '>\n')
    return path


def local_links(root, path):
    # 위키는 표준 Markdown 상대 링크를 사용한다. Obsidian 전용 링크는 지원하지 않는다.
    content = path.read_text(encoding='utf-8')
    if '[[' in content or '![' in content:
        raise ValueError('표준 Markdown 링크를 사용하세요')
    links = []
    for link in re.findall(r'\[[^\]]*\]\(([^)]+)\)', content):
        if link.startswith(('https://', 'http://', '#')):
            continue
        target = (path.parent / link.split('#')[0]).resolve()
        if not target.is_relative_to(root.resolve()) or not target.is_file():
            raise ValueError('존재하지 않거나 영역 밖인 링크')
        links.append(target)
    return links


def check(root):
    errors = []
    for path in (root / 'wiki').rglob('*.md'):
        try:
            inside(root, path.relative_to(root).as_posix(), 'wiki')
            local_links(root, path)
        except ValueError:
            errors.append(path.relative_to(root).as_posix() + ': 링크 검증 실패')
    for source, record in state(root).items():
        try:
            source_path = inside(root, source, 'raw')
            if not source_path.is_file():
                raise ValueError('원자료 없음')
            citations = set()
            for output in record['outputs']:
                output_path = inside(root, output, 'wiki')
                if not output_path.is_file():
                    raise ValueError('출력 파일 없음')
                citations.update(local_links(root, output_path))
            if source_path.resolve() not in citations:
                raise ValueError('원자료 인용 삭제')
        except (ValueError, KeyError, TypeError):
            errors.append('처리 기록 검증 실패')
    return errors


def mark(root, sources, outputs):
    if not sources or not outputs or check(root):
        raise ValueError('자료·출력과 위키 링크를 확인하세요')
    for required in ('wiki/index.md', 'wiki/log.md'):
        if not (root / required).is_file():
            raise ValueError('색인과 로그가 필요합니다')
    citations = set()
    for output in outputs:
        path = inside(root, output, 'wiki')
        if path.suffix != '.md' or output in ('wiki/index.md', 'wiki/log.md'):
            raise ValueError('내용 페이지를 지정하세요')
        citations.update(local_links(root, path))
    done = state(root)
    for source in sources:
        path = inside(root, source, 'raw')
        if path.resolve() not in citations:
            raise ValueError('출력에 원자료 링크가 필요합니다')
        done[source] = {'sha256': fingerprint(path), 'outputs': sorted(set(outputs))}
    target = root / 'wiki/processed.json'
    temporary = root / 'wiki/.processed.tmp'
    temporary.write_text(json.dumps(done, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temporary.replace(target)


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('pending')
    sub.add_parser('check')
    add = sub.add_parser('add-url')
    add.add_argument('url')
    complete = sub.add_parser('mark')
    complete.add_argument('--sources', nargs='+', required=True)
    complete.add_argument('--outputs', nargs='+', required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    if args.command == 'pending':
        print(json.dumps(pending(root), ensure_ascii=False, indent=2))
    elif args.command == 'add-url':
        print(add_url(root, args.url).relative_to(root))
    elif args.command == 'mark':
        mark(root, args.sources, args.outputs)
    else:
        errors = check(root)
        print('\n'.join(errors) if errors else '위키 링크 및 처리 기록 검증 통과')
        return bool(errors)
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception:
        print('위키 작업 실패: 경로·자료·처리 기록을 확인하세요.', file=sys.stderr)
        sys.exit(1)
