"""Offline tests: fake gh, real Git, disposable HOME/repositories only."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

SOURCE = Path(__file__).with_name('run.py')


class IdentityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='ship-it-test-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.repo = self.root / 'repo'
        self.repo.mkdir()
        self.bin = self.root / 'bin'
        self.bin.mkdir()
        gh = self.bin / 'gh'
        gh.write_text('''#!/usr/bin/env python3
import os, sys, subprocess
from pathlib import Path
if sys.argv[1:3] == ['auth', 'token']:
    assert '--user' in sys.argv and 'robot' in sys.argv
    assert 'GH_TOKEN' not in os.environ
    assert 'GITHUB_TOKEN' not in os.environ
    if os.environ.get('EXPECTED_GH_DIR'):
        assert os.environ['GH_CONFIG_DIR'] == os.environ['EXPECTED_GH_DIR']
        if os.environ.get('FAKE_TOKEN_FAIL'):
            sys.exit(1)
        assert (Path(os.environ['GH_CONFIG_DIR']) / 'hosts.yml').read_text() == 'simulated-login-config'
    print('simulated-token')
elif sys.argv[1:2] == ['api'] and 'user' in sys.argv:
    if os.environ.get('FAKE_FAIL'):
        sys.exit(1)
    assert os.environ['GH_TOKEN'] == 'simulated-token'
    assert os.environ['GH_CONFIG_DIR'] != os.environ['OLD_GH_CONFIG']
    print(os.environ.get('FAKE_LOGIN', 'robot'))
elif sys.argv[1:] == ['child-git']:
    sys.exit(subprocess.run(['git', 'commit', '--allow-empty', '-m', 'child']).returncode)
else:
    Path(os.environ['MARKER']).write_text('executed')
''')
        gh.chmod(0o700)
        self.env = dict(os.environ, HOME=str(self.root), XDG_CONFIG_HOME=str(self.root),
                        PATH=str(self.bin) + os.pathsep + os.environ['PATH'],
                        GH_TOKEN='human-token', GITHUB_TOKEN='human-token',
                        GH_CONFIG_DIR=str(self.root / 'human-gh'),
                        OLD_GH_CONFIG=str(self.root / 'human-gh'),
                        GIT_AUTHOR_NAME='Human override', GIT_COMMITTER_EMAIL='human@example.test',
                        MARKER=str(self.root / 'executed'))
        self.global_config = self.root / '.gitconfig'
        self.global_config.write_text('[user]\n name = Human\n email = human@example.test\n[credential]\n helper = !false\n')
        self.git('init', '-q')
        self.git('config', 'user.name', 'Local human')
        self.git('config', 'credential.https://github.com.helper', '!false')
        self.local = self.repo / '.git/config'
        self.before = self.local.read_bytes(), self.global_config.read_bytes()
        self.install = self.repo / '.git/ship-it'
        self.install.mkdir()
        self.run = self.install / 'run'
        shutil.copy(SOURCE, self.run)
        self.run.chmod(0o700)
        self.token = self.root / 'token'
        self.token.write_text('simulated-token')
        self.token.chmod(0o600)
        self.config = dict(mode='machine', account='robot', name='Robot',
                           email='robot@example.test', token_file=str(self.token))
        self.save()

    def save(self):
        (self.install / 'config.json').write_text(json.dumps(self.config))

    def git(self, *args):
        return subprocess.run(['git', *args], cwd=self.repo, env=self.env,
                              capture_output=True, text=True, check=True).stdout.strip()

    def wrapped(self, *args, cwd=None, input=None):
        return subprocess.run([str(self.run), '--account', 'robot', *args],
                              cwd=cwd or self.repo, env=self.env, input=input,
                              capture_output=True, text=True)

    def test_commit_and_credentials_are_isolated(self):
        result = self.wrapped('git', 'commit', '--allow-empty', '-m', 'offline test')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.git('log', '-1', '--format=%an <%ae>|%cn <%ce>'),
                         'Robot <robot@example.test>|Robot <robot@example.test>')
        result = self.wrapped('git', 'credential', 'fill', input='protocol=https\nhost=github.com\n\n')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('password=simulated-token', result.stdout)
        other = self.wrapped('git', 'credential', 'fill', input='protocol=https\nhost=example.test\n\n')
        self.assertNotEqual(other.returncode, 0)
        self.assertNotIn('simulated-token', other.stdout + other.stderr)
        self.assertEqual(self.before, (self.local.read_bytes(), self.global_config.read_bytes()))

    def test_ssh_and_https_remotes_remain_unchanged(self):
        for url in ('git@github.com:owner/repo.git', 'ssh://git@github.com/owner/repo.git',
                    'https://github.com/owner/repo.git'):
            self.git('config', 'remote.origin.url', url)
            result = self.wrapped('git', 'remote', 'get-url', 'origin')
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), 'https://github.com/owner/repo.git')
            self.assertEqual(self.git('config', 'remote.origin.url'), url)

    def test_failure_never_executes_requested_write(self):
        for failure in ('mismatch', 'missing', 'permissions', 'policy', 'rewrite'):
            with self.subTest(failure=failure):
                if failure == 'mismatch':
                    self.env['FAKE_LOGIN'] = 'human'
                elif failure == 'missing':
                    self.token.unlink()
                elif failure == 'permissions':
                    self.token.write_text('simulated-token')
                    self.token.chmod(0o644)
                elif failure == 'policy':
                    self.token.chmod(0o600)
                    self.config['account'] = 'human'
                    self.save()
                else:
                    self.config['account'] = 'robot'
                    self.save()
                    self.git('config', 'url.ssh://alias/.insteadOf', 'https://github.com/')
                result = self.wrapped('gh', 'issue', 'create')
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse((self.root / 'executed').exists())
                self.assertNotIn('simulated-token', result.stdout + result.stderr)
                self.env.pop('FAKE_LOGIN', None)

    def test_unavailable_verification_and_missing_configuration(self):
        self.env['FAKE_FAIL'] = '1'
        failed = self.wrapped('gh', 'issue', 'create')
        self.assertNotEqual(failed.returncode, 0)
        self.assertFalse((self.root / 'executed').exists())
        self.env.pop('FAKE_FAIL')
        (self.install / 'config.json').unlink()
        missing = self.wrapped('gh', 'issue', 'create')
        self.assertNotEqual(missing.returncode, 0)
        self.assertFalse((self.root / 'executed').exists())

    def test_unsupported_remote_stops_before_write(self):
        for url in ('git@my-github:owner/repo.git', 'https://human:secret@github.com/owner/repo.git'):
            self.git('config', 'remote.origin.url', url)
            result = self.wrapped('gh', 'issue', 'create')
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((self.root / 'executed').exists())
            self.assertNotIn('secret', result.stderr)

    def configure_gh_login(self):
        gh_dir = self.install / 'gh'
        gh_dir.mkdir(mode=0o700)
        hosts = gh_dir / 'hosts.yml'
        hosts.write_text('simulated-login-config')
        hosts.chmod(0o600)
        self.config.pop('token_file')
        self.config['auth'] = 'gh-login'
        self.env['EXPECTED_GH_DIR'] = str(gh_dir.resolve())
        self.save()
        return hosts

    def test_gh_login_loads_saved_config_and_isolates_git(self):
        hosts = self.configure_gh_login()
        before = hosts.read_bytes()
        result = self.wrapped('git', 'commit', '--allow-empty', '-m', 'isolated login')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.git('log', '-1', '--format=%an <%ae>|%cn <%ce>'),
                         'Robot <robot@example.test>|Robot <robot@example.test>')
        self.assertEqual(self.wrapped('gh', 'pr', 'edit').returncode, 0)
        self.assertEqual(hosts.read_bytes(), before)
        self.assertEqual(self.before, (self.local.read_bytes(), self.global_config.read_bytes()))

    def test_gh_login_failure_never_falls_back(self):
        hosts = self.configure_gh_login()
        for failure in ('missing', 'permissions', 'lookup', 'identity'):
            with self.subTest(failure=failure):
                hosts.write_text('simulated-login-config')
                hosts.chmod(0o600)
                if failure == 'missing':
                    hosts.unlink()
                elif failure == 'permissions':
                    hosts.chmod(0o644)
                elif failure == 'lookup':
                    self.env['FAKE_TOKEN_FAIL'] = '1'
                else:
                    self.env['FAKE_LOGIN'] = 'human'
                result = self.wrapped('gh', 'issue', 'create')
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse((self.root / 'executed').exists())
                self.assertNotIn('simulated-token', result.stdout + result.stderr)
                self.env.pop('FAKE_TOKEN_FAIL', None)
                self.env.pop('FAKE_LOGIN', None)

    def test_api_token_mode_does_not_use_unselected_login(self):
        gh_dir = self.install / 'gh'
        gh_dir.mkdir(mode=0o700)
        (gh_dir / 'hosts.yml').write_text('unused-stale-config')
        self.config['auth'] = 'api-token'
        self.save()
        self.token.unlink()
        self.assertNotEqual(self.wrapped('gh', 'issue', 'create').returncode, 0)
        self.assertFalse((self.root / 'executed').exists())

    def test_existing_account_and_linked_worker_checkout(self):
        self.config['mode'] = 'existing'
        self.save()
        self.assertEqual(self.wrapped('git', 'commit', '--allow-empty', '-m', 'initial').returncode, 0)
        worker = self.root / 'worker'
        self.git('worktree', 'add', '-q', '-b', 'worker', str(worker))
        common = subprocess.run(['git', 'rev-parse', '--path-format=absolute', '--git-common-dir'],
                                cwd=worker, env=self.env, capture_output=True, text=True, check=True)
        self.assertEqual((Path(common.stdout.strip()) / 'ship-it/run').resolve(), self.run.resolve())
        result = self.wrapped('git', 'commit', '--allow-empty', '-m', 'worker', cwd=worker)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.wrapped('gh', 'pr', 'edit', cwd=worker).returncode, 0)
        self.assertTrue((self.root / 'executed').exists())
        child = self.wrapped('gh', 'child-git', cwd=worker)
        self.assertEqual(child.returncode, 0, child.stderr)
        ident = subprocess.run(['git', 'log', '-1', '--format=%an <%ae>|%cn <%ce>'],
                               cwd=worker, env=self.env, capture_output=True, text=True, check=True)
        self.assertEqual(ident.stdout.strip(), 'Robot <robot@example.test>|Robot <robot@example.test>')


if __name__ == '__main__':
    unittest.main()
