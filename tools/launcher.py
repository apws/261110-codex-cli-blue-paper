#!/usr/bin/env python3
"""Explicit launcher for the validated custom package; ordinary codex is unchanged."""
import json
import os
from pathlib import Path
import sys

base = Path.home() / '.local/share/codex-blue'
profile_path = Path.home() / '.config/codex-blue/colors.json'
profile = json.loads(profile_path.read_text())
package = (base / 'current').resolve(strict=True)
arguments = sys.argv[1:]
if arguments == ['--blue-info']:
    print(json.dumps(dict(profile=profile, package=str(package),
                          build=json.loads((package / 'codex-blue.json').read_text())), indent=2))
    raise SystemExit(0)
off = arguments[:1] == ['--blue-off']
if off:
    arguments = arguments[1:]
env = os.environ.copy()
env.setdefault('CODEX_BLUE_PAPER', '1' if profile.get('enabled', True) else '0')
env.setdefault('CODEX_BLUE_PAPER_BG', profile['paper'])
env.setdefault('CODEX_BLUE_PAPER_FG', profile['ink'])
if off:
    env['CODEX_BLUE_PAPER'] = '0'
env['PATH'] = str(package / 'codex-path') + os.pathsep + env.get('PATH', '')
binary = package / 'bin/codex'
os.execve(binary, [str(binary), *arguments], env)
