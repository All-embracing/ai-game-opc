#!/usr/bin/env python3
"""Offline readiness report. Never reads or outputs secrets."""
from __future__ import annotations
import argparse
import csv
import json
import subprocess
from datetime import datetime
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def check_project(root: Path):
    checks=[]
    def add(key, ok, desc): checks.append({'check':key,'pass':bool(ok),'detail':desc})
    required = ['README.md','studio.json','ops_policy.json','data/backlog.json',
                'data/metrics.csv','games/emotion-garden/index.html',
                '.github/workflows/quality.yml',
                '.github/workflows/ai-daily-dev.yml']
    missing=[f for f in required if not (root/f).is_file()]
    add('project_structure',not missing, 'Missing: '+', '.join(missing) if missing else 'Required project files exist')
    try:
        tasks=json.loads((root/'data/backlog.json').read_text(encoding='utf-8'))
        ids=[t['id'] for t in tasks]
        eligible=[t for t in tasks if t.get('agent_eligible') is True and t.get('status')=='todo']
        add('backlog_valid',len(ids)==len(set(ids)) and all('acceptance' in t for t in tasks),
            f'{len(tasks)} task(s); {len(eligible)} eligible task(s); no duplicate IDs: {len(ids)==len(set(ids))}')
    except (OSError,ValueError,KeyError,TypeError) as exc:
        add('backlog_valid',False,'Cannot read task queue: '+type(exc).__name__)
    try:
        with (root/'data/metrics.csv').open(encoding='utf-8-sig',newline='') as f:
            rows=list(csv.DictReader(f))
        cols={'date','playtests','spend_cny','revenue_cny'}
        add('metrics_schema', not rows or all(cols <= set(r) for r in rows),
            f'{len(rows)} recorded row(s); validate each entry against original evidence; blanks mean unknown')
    except (OSError,ValueError) as exc:
        add('metrics_schema',False,'Cannot read metrics: '+type(exc).__name__)
    try:
        proc=subprocess.run(['git','remote','get-url','origin'],cwd=root,capture_output=True,text=True,timeout=4)
        remote=proc.stdout.strip() if proc.returncode==0 else ''
        # Mask URL: never show tokens embedded in a remote URL.
        add('github_remote_configured',bool(remote) and ('github.com' in remote),
            'GitHub remote origin configured' if remote and 'github.com' in remote else 'Not configured: upload the project to a private GitHub repository')
    except (OSError,subprocess.TimeoutExpired):
        add('github_remote_configured',False,'Git remote not available in this environment')
    add('cloud_actions_verified',False,'Unknown: only GitHub run logs can confirm cloud execution; offline test cannot verify')
    add('api_credentials_verified',False,'Unknown: this checker intentionally does not access API secrets')
    add('player_research_verified',False,'Unknown until real playtest evidence is entered and independently checked')
    return checks


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--json',action='store_true')
    ap.add_argument('--output',default='')
    args=ap.parse_args()
    checks=check_project(ROOT)
    if args.json:
        out=json.dumps({'generated_at':datetime.now().astimezone().isoformat(),'checks':checks},ensure_ascii=False,indent=2)
    else:
        lines=['# OPC 部署前自检', '', '说明：这是离线自检，无法证明云端已经部署。', '']
        for x in checks:
            lines.append(('- [x] ' if x['pass'] else '- [ ] ')+f"{x['check']}：{x['detail']}")
        out='\n'.join(lines)+'\n'
    if args.output:
        dest=Path(args.output)
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(out,encoding='utf-8')
    else: print(out)

if __name__=='__main__': main()
