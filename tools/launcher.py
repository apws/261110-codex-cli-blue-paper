#!/usr/bin/env python3
"""Explicit profile-v2 launcher for a validated custom package; ordinary codex is unchanged."""
import json
import os
from pathlib import Path
import re
import sys

DEFAULT_PROFILE = {
    'enabled': True,
    'paper': '#D9EBFF',
    'ink': '#000000',
    'emphasis_ink': 'auto',
    'hint_ink': 'auto',
    'cursor': 'terminal',
    'cursor_text': 'auto',
    'user_text_bold': False,
}


def validate_profile(values):
    if not isinstance(values, dict):
        raise ValueError('The color profile must be a JSON object.')
    unknown = set(values) - set(DEFAULT_PROFILE)
    if unknown:
        raise ValueError('Unknown color profile keys: ' + ', '.join(sorted(unknown)))
    profile = DEFAULT_PROFILE | values
    for key in ('enabled', 'user_text_bold'):
        if not isinstance(profile[key], bool):
            raise ValueError(f'{key} must be true or false, not a string.')
    for key in ('paper', 'ink', 'emphasis_ink', 'hint_ink', 'cursor', 'cursor_text'):
        value = profile[key]
        special = {'auto'} if key in ('emphasis_ink', 'hint_ink', 'cursor_text') else {'auto', 'terminal'} if key == 'cursor' else set()
        if not isinstance(value, str):
            raise ValueError(f'{key} must be a hex color' + (' or ' + '/'.join(sorted(special)) if special else '') + '.')
        value = value.strip()
        if value.lower() in special:
            profile[key] = value.lower()
        elif re.fullmatch(r'#?[0-9a-fA-F]{6}', value):
            profile[key] = '#' + value.lstrip('#').upper()
        else:
            raise ValueError(f'Invalid {key}: expected #RRGGBB' + (' or ' + '/'.join(sorted(special)) if special else '') + '.')
    return profile


def profile_environment(profile, inherited, off=False):
    profile = validate_profile(profile)
    env = inherited.copy()
    names = {
        'enabled': 'CODEX_BLUE_PAPER',
        'paper': 'CODEX_BLUE_PAPER_BG',
        'ink': 'CODEX_BLUE_PAPER_FG',
        'emphasis_ink': 'CODEX_BLUE_PAPER_EMPHASIS_FG',
        'hint_ink': 'CODEX_BLUE_PAPER_HINT_FG',
        'cursor': 'CODEX_BLUE_PAPER_CURSOR',
        'cursor_text': 'CODEX_BLUE_PAPER_CURSOR_TEXT',
        'user_text_bold': 'CODEX_BLUE_PAPER_BOLD',
    }
    for key, variable in names.items():
        value = profile[key]
        env.setdefault(variable, ('1' if value else '0') if isinstance(value, bool) else value)
    if off:
        env['CODEX_BLUE_PAPER'] = '0'
    return env


def main():
    base = Path.home() / '.local/share/codex-blue'
    path = Path.home() / '.config/codex-blue/colors.json'
    try:
        profile = validate_profile(json.loads(path.read_text()))
    except (OSError, ValueError) as error:
        raise SystemExit(f'codex-blue profile: {error}') from error
    package = (base / 'current').resolve(strict=True)
    build = json.loads((package / 'codex-blue.json').read_text())
    arguments = sys.argv[1:]
    if arguments == ['--blue-info']:
        print(json.dumps(dict(profile=profile, package=str(package), build=build,
                              profile_schema=2,
                              package_supports_profile=build.get('profile_schema') == 2), indent=2))
        return
    if build.get('profile_schema') != 2:
        raise SystemExit('codex-blue: this package is incompatible with the profile-v2 launcher; select a validated schema-2 release or use its saved matching launcher.')
    off = arguments[:1] == ['--blue-off']
    if off:
        arguments = arguments[1:]
    env = profile_environment(profile, os.environ, off=off)
    env['PATH'] = str(package / 'codex-path') + os.pathsep + env.get('PATH', '')
    binary = package / 'bin/codex'
    os.execve(binary, [str(binary), *arguments], env)


if __name__ == '__main__':
    main()
