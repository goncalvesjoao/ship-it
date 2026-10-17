#!/usr/bin/env python3
"""Run one gh/Git command with a verified repository identity."""
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tempfile


def capture(args, env):
    result = subprocess.run(args, env=env, text=True, capture_output=True)
    if result.returncode:
        raise ValueError('Credential or configuration check failed; no command executed')
    return result.stdout.strip()


def main():
    # Git calls this mode internally; credentials go only to Git's private pipe.
    if len(sys.argv) > 1 and sys.argv[1] == 'credential':
        fields = dict(line.rstrip('\n').split('=', 1) for line in sys.stdin if '=' in line)
        if sys.argv[-1] == 'get' and fields.get('protocol') == 'https' and fields.get('host') == 'github.com':
            print('username=x-access-token\npassword=' + os.environ['GH_TOKEN'])
        return 0
    if len(sys.argv) < 5 or sys.argv[1] != '--account' or sys.argv[3] not in ('gh', 'git'):
        raise ValueError('Usage: run --account EXPECTED_LOGIN gh|git ARGS...')
    expected, command = sys.argv[2], sys.argv[3:]
    config = json.loads(Path(__file__).with_name('config.json').read_text())
    if config['account'].lower() != expected.lower():
        raise ValueError('Local account differs from repository policy')
    env = dict(os.environ)
    for key in list(env):
        if key.startswith(('GH_', 'GITHUB_', 'GIT_CONFIG_', 'GIT_TRACE')) or key in (
            'GIT_ASKPASS', 'SSH_ASKPASS', 'GIT_SSH', 'GIT_SSH_COMMAND', 'GIT_CURL_VERBOSE',
            'GIT_AUTHOR_NAME', 'GIT_AUTHOR_EMAIL', 'GIT_COMMITTER_NAME', 'GIT_COMMITTER_EMAIL'):
            env.pop(key)
    mode = config['mode']
    if mode == 'machine':
        auth = config.get('auth', 'api-token')
        if auth == 'api-token':
            token_path = Path(config['token_file'])
            if not token_path.is_absolute() or token_path.stat().st_mode & 0o077:
                raise ValueError('Token file must be absolute and private (chmod 600)')
            token = token_path.read_text().strip()
        elif auth == 'gh-login':
            gh_dir = Path(__file__).resolve().with_name('gh')
            hosts = gh_dir / 'hosts.yml'
            if gh_dir.stat().st_mode & 0o077 or hosts.stat().st_mode & 0o077:
                raise ValueError('Isolated gh configuration must be private')
            env['GH_CONFIG_DIR'] = str(gh_dir)
            token = capture(['gh', 'auth', 'token', '--hostname', 'github.com', '--user', expected], env)
        else:
            raise ValueError('Unknown machine authentication method')
    elif mode == 'existing':
        if os.environ.get('GH_CONFIG_DIR'):
            env['GH_CONFIG_DIR'] = os.environ['GH_CONFIG_DIR']
        # Capture the named stored account, never the ambient active account/token.
        token = capture(['gh', 'auth', 'token', '--hostname', 'github.com', '--user', expected], env)
    else:
        raise ValueError('Unknown identity mode')
    if not token or '\n' in token or '\r' in token:
        raise ValueError('Missing or invalid credential')
    with tempfile.TemporaryDirectory(prefix='ship-it-') as isolated:
        env.update(GH_TOKEN=token, GH_HOST='github.com', GH_CONFIG_DIR=isolated,
                   GH_PROMPT_DISABLED='1', GIT_TERMINAL_PROMPT='0')
        login = capture(['gh', 'api', '--hostname', 'github.com', 'user', '--jq', '.login'], env)
        if login.lower() != expected.lower():
            raise ValueError('GitHub identity mismatch; no command executed')
        name, email = config['name'], config['email']
        if not name or not email or any(c in name + email for c in '\r\n'):
            raise ValueError('Missing or invalid commit identity')
        env.update(GIT_AUTHOR_NAME=name, GIT_AUTHOR_EMAIL=email,
                   GIT_COMMITTER_NAME=name, GIT_COMMITTER_EMAIL=email)
        # Clear inherited credential helpers/headers, including URL-specific entries.
        settings = [('credential.helper', ''), ('http.extraHeader', '')]
        raw = capture(['git', 'config', '--null', '--list'], env)
        for entry in raw.split('\0'):
            key, _, value = entry.partition('\n')
            if re.fullmatch(r'remote\..*\.(url|pushurl)', key, re.I) and not re.fullmatch(
                r'(?:https://github\.com/|git@github\.com:|ssh://git@github\.com/)[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/?', value
            ):
                raise ValueError('Unsupported remote; review local setup before execution')
            if re.fullmatch(r'credential\..*\.helper|http\..*\.extraheader', key, re.I):
                settings.append((key, ''))
            if re.fullmatch(r'url\..*\.(insteadof|pushinsteadof)', key, re.I):
                raise ValueError('Custom URL rewrite requires manual review before isolated execution')
        helper = '!' + shlex.join([sys.executable, str(Path(__file__).resolve()), 'credential'])
        settings += [('credential.helper', helper), ('credential.interactive', 'false'),
                     ('url.https://github.com/.insteadOf', 'git@github.com:'),
                     ('url.https://github.com/.insteadOf', 'ssh://git@github.com/'),
                     ('user.name', name), ('user.email', email)]
        for i, (key, value) in enumerate(settings):
            env[f'GIT_CONFIG_KEY_{i}'] = key
            env[f'GIT_CONFIG_VALUE_{i}'] = value
        env['GIT_CONFIG_COUNT'] = str(len(settings))
        env['GIT_ASKPASS'] = '/usr/bin/false'
        env['GIT_SSH_COMMAND'] = '/usr/bin/false'
        return subprocess.run(command, env=env).returncode


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError):
        # Do not echo configuration, subprocess stderr, or token-bearing exceptions.
        print('Ship-it identity unavailable or mismatched. Repair local setup; no fallback.', file=sys.stderr)
        sys.exit(1)
