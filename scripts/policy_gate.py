#!/usr/bin/env python3
"""Fail-closed, stdlib-only sanity gate for AI-authored candidate patches.

The gate is an *additional* control, not a sandbox or a substitute for code review.
Run it on an applied patch in a clean checkout, after `git add -N` for new files.
"""
from __future__ import annotations
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / 'ops_policy.json'
# Known patterns; deliberately cautious. This never prints a secret to logs.
SENSITIVE = [
    re.compile(rb'\bsk-[A-Za-z0-9_-]{16,}\b'),
    re.compile(rb'\bghp_[A-Za-z0-9]{20,}\b'),
    re.compile(rb'\bgithub_pat_[A-Za-z0-9_]{20,}\b'),
    re.compile(rb'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----'),
]

class PolicyError(ValueError):
    pass


def validate_changes(changes: list[dict], policy: dict) -> list[str]:
    """Pure validation; changes have path, size, and content fields."""
    errors = []
    roots = tuple(policy['agent_write_roots'])
    forbidden_ext = set(policy['forbidden_extensions'])
    max_file = policy['max_changed_file_bytes']
    max_files = policy['max_changed_files']
    if len(changes) > max_files:
        errors.append('Changed file count exceeds safety limit')
    if not changes:
        errors.append('No candidate file changes found')
    for ch in changes:
        name = ch['path']
        parts = Path(name).parts
        if name.startswith('/') or '\\' in name or '..' in parts or not name.startswith(roots):
            errors.append(f'Forbidden path: {name}')
            continue
        if Path(name).suffix.lower() in forbidden_ext:
            errors.append(f'Forbidden extension: {name}')
        if ch['size'] > max_file:
            errors.append(f'File exceeds size limit: {name}')
        if ch.get('is_symlink'):
            errors.append(f'Symlink not permitted: {name}')
        data = ch.get('content', b'')
        for pattern in SENSITIVE:
            if pattern.search(data):
                errors.append(f'Suspected credential in: {name} (value suppressed)')
                break
        if name.lower().endswith(('.html','.js','.ts')):
            if re.search(rb'<script\s+[^>]*src\s*=\s*["\']?https?://',data,re.I):
                errors.append(f'Remote script source requires manual approval: {name}')
    return errors


def git_bytes(*args: str) -> bytes:
    return subprocess.check_output(['git', *args], cwd=ROOT, stderr=subprocess.STDOUT)


def collect_changes(base: str) -> list[dict]:
    # A locally produced candidate patch is already applied to checkout here.
    # -z avoids ambiguous newlines in file names. --diff-filter disallows deletions.
    names = git_bytes('diff', '--name-only', '-z', '--diff-filter=ACMRT', base).split(b'\0')
    deleted = [p.decode('utf-8',errors='replace') for p in git_bytes('diff','--name-only','-z','--diff-filter=D',base).split(b'\0') if p]
    if deleted:
        raise PolicyError('File deletions are disallowed: '+', '.join(deleted))
    changes = []
    for raw in names:
        if not raw: continue
        name = raw.decode('utf-8', errors='strict')
        full = ROOT / name
        if not full.exists() and not full.is_symlink():
            raise PolicyError('Changed file absent: '+name)
        symlink = full.is_symlink()
        contents = b'' if symlink else full.read_bytes()
        changes.append({'path':name,'size':len(contents),'content':contents,'is_symlink':symlink})
    return changes


def main() -> int:
    a = argparse.ArgumentParser()
    a.add_argument('--base',default='HEAD',help='Trusted base commit / ref')
    args=a.parse_args()
    try:
        policy=json.loads(POLICY.read_text(encoding='utf-8'))
        files=collect_changes(args.base)
        errors=validate_changes(files, policy)
        if errors:
            for e in errors: print('DENY: '+e,file=sys.stderr)
            return 2
        print('PASS: candidate change policy ('+str(len(files))+' file(s))')
        return 0
    except (OSError, subprocess.CalledProcessError, ValueError, UnicodeError) as exc:
        print('DENY: policy gate unable to validate changes: '+str(exc),file=sys.stderr)
        return 2

if __name__=='__main__':
    raise SystemExit(main())
