#!/usr/bin/env python3
"""Safely push the initial AI Game OPC project to an EXISTING EMPTY repository.

Never overwrites remote history. Requires local Git credentials, supplied by user.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import shutil
import subprocess
import sys

DEFAULT_REPO = "https://github.com/All-embracing/ai-game-opc.git"
PROJECT = Path(__file__).resolve().parent.parent
REQUIRED = ["README.md", "AGENTS.md", ".github/workflows/quality.yml", ".github/workflows/ai-daily-dev.yml", "games/emotion-garden/index.html", "tests/test_daily_ops.py"]


def run(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(list(args), cwd=PROJECT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=check)


def halt(message: str) -> None:
    print("\n[STOP] " + message, file=sys.stderr)
    raise SystemExit(2)


def main() -> None:
    p = argparse.ArgumentParser(description="One-time safe upload into an existing, empty GitHub repository")
    p.add_argument("--repo", default=DEFAULT_REPO, help="Existing Git repository URL (for local test also accepts a filesystem path)")
    p.add_argument("--yes", action="store_true", help="Proceed without the confirmation prompt")
    args = p.parse_args()
    print("AI GAME OPC | Initial upload check")
    print("Project:", PROJECT)
    print("Target :", args.repo)
    if not shutil.which("git"):
        halt("Git is not installed. Install it from https://git-scm.com/downloads and reopen your terminal.")
    missing = [f for f in REQUIRED if not (PROJECT / f).is_file()]
    if missing: halt("Unpacked project is incomplete. Missing: " + ", ".join(missing))
    if (PROJECT / '.git').exists():
        halt("This project already has a .git directory. No changes made; inspect the existing remote/branch manually.")
    for key in ('user.name','user.email'):
        cp=run('git','config','--get',key,check=False)
        if cp.returncode != 0 or not cp.stdout.strip():
            halt(f"Git identity '{key}' is not configured. Set it with: git config --global {key} \"YOUR_VALUE\"")
    # Check remote state before creating local history. Never auto-merge or force push.
    probe = run('git','ls-remote','--heads',args.repo,check=False)
    if probe.returncode:
        halt("Cannot reach/authenticate the target repository (or it does not exist). "
             "Run 'gh auth login' and 'gh auth setup-git' first. "
             "Git message: " + probe.stderr.strip()[:350])
    if probe.stdout.strip():
        halt("Remote repository already has branch commits. Refusing to overwrite. "
             "Please DO NOT use force push. Clone it first and copy files into it, then commit normally.")
    print("[OK] Target has no branches; initial upload is safe to attempt.")
    if not args.yes:
        try: answer=input("Type UPLOAD to initialize and push the full project: ").strip()
        except EOFError: halt("No confirmation received.")
        if answer != 'UPLOAD': halt("Cancelled without changes.")
    commands=[('git','init','-b','main'),('git','remote','add','origin',args.repo),('git','add','.'),('git','commit','-m','Initialize AI Game OPC v0.3.1'),('git','push','-u','origin','main')]
    for cmd in commands:
        print('RUN:', ' '.join(cmd[:2]), '...')
        p=run(*cmd,check=False)
        if p.returncode:
            halt("Command failed: " + ' '.join(cmd[:2]) + '\n' + (p.stderr or p.stdout).strip()[-1500:] +
                 "\nNo force push attempted. Check authentication and repository state before retrying.")
    print("\n[SUCCESS] Initial commit pushed. Open: https://github.com/All-embracing/ai-game-opc")
    print("Next: GitHub Actions -> OPC Quality Gate -> review result.")
    print("Keep OPENAI_API_KEY only in Settings -> Secrets and variables -> Actions; never share it in chat.")


if __name__ == '__main__':
    main()
