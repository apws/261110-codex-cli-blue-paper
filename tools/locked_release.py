"""Normalize only local 0.0.0 release labels left stale by upstream release tagging."""
import copy
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tomllib


def normalize_lock(source: Path):
    path = source / 'codex-rs/Cargo.lock'
    original = subprocess.check_output(['git', 'show', 'HEAD:codex-rs/Cargo.lock'], cwd=source)
    version = tomllib.loads((source / 'codex-rs/Cargo.toml').read_text())['workspace']['package']['version']
    expected = copy.deepcopy(tomllib.loads(original.decode()))
    count = 0
    for package in expected['package']:
        if 'source' not in package and package['version'] == '0.0.0':
            package['version'] = version
            count += 1
    blocks = re.split(r'(?=^\[\[package\]\]$)', original.decode(), flags=re.MULTILINE)
    for index, block in enumerate(blocks):
        if block.startswith('[[package]]') and not re.search(r'^source = ', block, re.MULTILINE):
            blocks[index] = re.sub(r'^version = "0\.0\.0"$', 'version = "' + version + '"', block, count=1, flags=re.MULTILINE)
    normalized = ''.join(blocks).encode()
    assert tomllib.loads(normalized.decode()) == expected
    assert path.read_bytes() in (original, normalized), 'Unexpected lockfile delta; review required.'
    path.write_bytes(normalized)
    sha = lambda value: hashlib.sha256(value).hexdigest()
    return dict(original_sha256=sha(original), normalized_sha256=sha(normalized),
                workspace_version=version, local_release_labels_normalized=count,
                external_packages_and_all_dependency_edges_unchanged=True)
