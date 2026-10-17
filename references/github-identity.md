# Repository identity

Before Ship-it GitHub access or Git writes/network operations, read `docs/agents/issue-tracker.md`, including its Ship-it identity policy. Missing policy requires `setup-ship-it` before those operations. Local inspection and drafting can continue. Preserve upstream approval gates.

Resolve the helper afresh in each checkout:

```sh
git rev-parse --path-format=absolute --git-common-dir
```

The helper is `<absolute-git-common-dir>/ship-it/run`. Execute it with `--account <expected-login-from-policy> gh <args>` or `--account <expected-login-from-policy> git <args>`, explicitly in the intended checkout. All `gh`/`git` examples in these skills and invoked upstream skills use this prefix. Use explicit GitHub repository/host arguments. The helper verifies the login on every invocation, including reads; a prior successful check is insufficient. Keep credentials out of arguments, logs, chat, and tracked files. Do not invoke credential-display commands. Use the CLI through the helper for GitHub writes; connectors and managed worktree tools do not inherit its identity. Use wrapped `git worktree` commands where a managed tool cannot guarantee the policy identity for its Git operations.

Pass this reference's absolute path, the expected login, policy path, and target checkout to every upstream skill, implementer, merger, PR worker, review worker, replacement worker, and fresh monitoring worker. Require nested delegation to forward them. Shell environment inheritance is insufficient. Workers discover the helper through their own Git common directory; a separate clone needs its own setup.

Include the same identity instructions and policy pointer in saved monitoring prompts. On every tick and resumed run, reload current repository policy and rediscover the local helper before GitHub access or Git writes. Saved logins are expectations to reconcile with current policy, never authority to silently change accounts. Missing helper/configuration/credentials, policy disagreement, or verification failure stops affected operations without falling back to ambient `gh`, connectors, SSH agents, or another account. Existing-account mode intentionally uses the configured personal account; this is not a fallback. Return the local setup blocker through the normal coordinator; pause affected monitoring and report any unverified status or shutdown. Do not attempt a GitHub blocker label/comment when authentication is unavailable.

For machine-authored PRs, request review from the configured human reviewer at review handoff, verifying the request or an existing human review. If assignment is needed and the PR is unassigned, assign that human, preserving existing assignments. Never assign the machine author as the handoff. Apply this at both implementation readiness and monitoring's human-review/merge-ready outcomes. A missing or ineligible reviewer leaves handoff incomplete. Existing-account setups retain their established assignment rules unless policy specifies a human reviewer.
