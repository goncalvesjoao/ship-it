---
name: setup-ship-it
description: Configure a repository for Ship-it, reusing Matt Pocock's setup and optionally isolating a dedicated GitHub machine user's authentication and commit identity.
metadata:
  dependency: "setup-matt-pocock-skills"
---

# Setup Ship-it

Configure the current repository only when invoked for setup. Editing this skill does not configure the development machine. Read [the user question rules](references/user-questions.md) before questions. Never create an account or request secrets in chat.

## Inspect and decide

Read repository instructions, `docs/agents/*.md`, Git remotes including push URLs, existing local Ship-it setup, and the installed `setup-matt-pocock-skills` skill and templates. Inspect Git's common directory, worktrees, authentication-related Git settings, and available `gh` accounts without printing tokens or credential-bearing URLs/configuration. Account names and sanitized remote hosts are sufficient. Preserve existing policy, tracker, labels, domain layout, reviewer, and authentication choices on reruns. Ask only for unresolved decisions or requested changes.

If issue-tracker, triage-label, or domain configuration is missing or needs updating, invoke the installed `setup-matt-pocock-skills` using the Skill tool when available, otherwise read and follow it. Preserve its findings, question sequence, draft approval, instruction-file selection, and existing user choices. Do not copy its templates or implement a second setup workflow. If unavailable, report the prerequisite. Ship-it publication skills require GitHub; preserve a chosen alternative tracker and explain that limitation instead of switching it.

Default new setups to the user's existing personal GitHub account and stored `gh` credentials. A separate assistant account is optional; offer machine-account isolation only as an opt-in, and preserve that choice on reruns. Resolve the expected login from existing policy and account inspection, asking only when ambiguous. Personal-account setup requires neither a new account nor a separate token file or human reviewer. For a machine account, also resolve a human reviewer distinct from the machine login and explicit commit name/email. Use an account-owned verified email or its GitHub noreply address, never infer the human's email. Existing-account mode can reuse the user's confirmed effective Git identity. Account creation, permission grants, or credential provisioning remain human tasks outside this skill; continue preparing a reviewable setup while those are missing.

### Collect machine-account details

Only enter this sequence after the user chooses machine-account mode. Use the structured question tool under the shared user question rules. Ask one missing field per question, wait for its answer, then continue; skip fields already established by inspection or prior answers. Do not ask for a combined paragraph or JSON configuration.

| Field | Question and answer guidance |
| --- | --- |
| Machine login | "What is the machine account's GitHub username?" Example: `project-assistant`, without `@`. If the account does not exist yet, offer to use the personal account instead or leave machine setup pending. |
| Human reviewer | "Which person's GitHub username should receive PR review requests?" Example: `alex`. Explain that it must differ from the machine login. |
| Commit name | "What name should appear on commits made by the machine account?" Suggest the inspected account display name or `Project assistant`; let the user confirm or supply another name. |
| Commit email | "Which email belonging to the machine account should commits use?" Accept its verified email or exact GitHub noreply address. Explain where to find it in the machine account's GitHub email settings; never guess its numeric account ID or use the human's email. |
| Credential file | "Do you already have this account's token saved in a private local file?" Offer "Yes, provide its absolute file path" or "Not yet, show local provisioning steps". Collect only the path, never the token. If provisioning is needed, guide it locally and keep verification pending until the file exists. |

Show a compact summary of the collected non-secret settings before the setup draft approval. Corrections update only the affected field; retain the other answers. Personal-account setup skips this sequence.

## Prepare and approve

Show a concrete draft of the repository policy and local file locations before editing. Preserve Matt's independent approval requirements. Configuration approval does not authorize test issues/PRs, account creation, global Git changes, `gh auth switch`, `gh auth setup-git`, or modification of shared remotes.

Use one locator on every machine: `<absolute-git-common-dir>/ship-it/run` with sibling `config.json`. Resolve the common directory using `git rev-parse --path-format=absolute --git-common-dir`. Linked worktrees share it; independent clones provision it separately. Keep these files and credentials outside the working tree. Check that the common directory is not tracked or inside a tracked nested repository. Use private directories and files, and never stage local setup.

Install [scripts/run.py](scripts/run.py) there as executable `run`, using Python 3. Its sibling JSON contains only:

```json
{
  "mode": "existing",
  "account": "expected-login",
  "name": "Confirmed commit name",
  "email": "confirmed-account-email"
}
```

The example uses the personal-account workflow. For `existing` mode omit `token_file`; the helper captures the named account's stored token through `gh auth token --user`, ignoring ambient token variables. It does not switch or update the active account. If that account has no stored credential, report provisioning needed rather than silently using an environment token.

For `machine` mode set `mode` to `machine` and add `token_file` with the absolute private token-file path. The human provisions an account token in a private absolute file outside all checkouts, mode 600, using a secure local terminal or secret manager. Never ask them to paste it into chat or run a command that prints it. Choose only the repository access/permissions needed for the selected workflow, including its issues, PRs, labels, review requests, and Git pushes. Explain any organization approval/SSO requirement discovered during verification. The helper uses that file directly with a temporary isolated `GH_CONFIG_DIR`; there is no persistent `gh` login to alter. Do not overwrite an existing token or local configuration on rerun. Compare non-secret settings, propose only necessary changes, and replace approved config atomically.

The helper applies author and committer identity and Git credential settings per process, including child Git processes. Standard `https://github.com/owner/repo.git`, `git@github.com:owner/repo.git`, and `ssh://git@github.com/owner/repo.git` remotes work without edits: SSH URLs are translated to HTTPS only during that command. Inspect both fetch and push targets. SSH aliases, custom ports, custom URL rewrite rules, credential-bearing URLs, and Enterprise hosts require a separately reviewed extension; stop affected setup rather than changing remotes or falling back to SSH. Do not certify them as supported.

## Record and verify

Append/update a single Ship-it identity section in `docs/agents/issue-tracker.md`, preserving Matt's tracker policy and unrelated edits. Record:

- Mode and expected GitHub account, plus human reviewer for machine mode.
- Confirmed commit identity and the supported GitHub host/repository.
- Helper locator relative to Git's common directory, command prefix, and instruction to reload policy on every run.
- Local provisioning on each machine/independent clone; credentials and absolute machine paths stay untracked.
- Missing local setup or identity mismatch stops GitHub access and Git writes/network operations, with no fallback to another account. The configured personal account is valid in existing-account mode. Local inspection/drafting may continue; monitoring must pause and report the blocker without unauthenticated GitHub writes.

In the existing agent instruction file selected by Matt's workflow, add/update one pointer requiring all Ship-it commands, delegated/nested workers, resumed runs, and scheduled ticks to read that policy. Use [the shared identity instructions](references/github-identity.md) for the full execution and reviewer rules. If no instruction file exists and Matt's setup has not selected one, ask which to create.

After approval and local provisioning, run the installed helper from the repository with `--account <expected-login> gh api --hostname github.com user --jq .login`. Check effective author/committer using wrapped `git var GIT_AUTHOR_IDENT` and `git var GIT_COMMITTER_IDENT`. Verify repository access with wrapped read-only `gh repo view <owner/repo> --json nameWithOwner,viewerPermission`. Use wrapped `git ls-remote <existing-remote>` for fetch authentication, with no remote/config changes. A public read alone does not prove push permission. Do not publish test issues/PRs or push test commits. When a human reviewer is configured, verify they can review this repository through read-only API evidence; if eligibility/access cannot be established, leave that validation pending.

### Final agent verification

After all setup edits, including on reruns, the agent must execute these read-only checks itself in a fresh command invocation from the target checkout. Reload the saved policy and rediscover the installed helper through Git's common directory, just as a later worker will. Use the saved expected login rather than the ambient active account:

```sh
"<absolute-git-common-dir>/ship-it/run" --account <expected-login> gh api --hostname github.com user --jq .login
"<absolute-git-common-dir>/ship-it/run" --account <expected-login> gh repo view <owner/repo> --json nameWithOwner,viewerPermission
```

Both commands must exit successfully. Compare the returned login with the policy login and the returned repository with the configured target. Missing credentials, mismatched identity/repository, or failed access leaves setup incomplete; report the failing check without secrets and stop without falling back to another account. A human-run check, `gh auth status`, or a simulated test does not satisfy this gate.

Report the observed account, repository, and viewer permission as live read-only verification evidence. These checks prove the agent can use the configured account through the actual execution path; they do not prove every write permission. Do not publish test issues/PRs or push commits to verify access.

Report files changed, verified login/commit identity, supported remotes, and any incomplete provisioning or permission verification. Distinguish local simulated checks from live read-only GitHub evidence. Missing credentials leave setup prepared but unverified; never claim ready. Reruns reuse approved settings and repair only missing or explicitly changed pieces.

The helper uses the documented [GitHub CLI environment precedence](https://cli.github.com/manual/gh_help_environment) and [Git credential helper protocol](https://git-scm.com/docs/gitcredentials).
