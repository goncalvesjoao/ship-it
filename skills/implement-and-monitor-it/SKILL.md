---
name: implement-and-monitor-it
description: "Deliver a spec by delegating implementation and PR creation to one worker running implement-it, verifying its result, and starting monitor-it."
disable-model-invocation: true
metadata:
  dependency: "implement-spec, code-review, pr"
  credits-author: Matt Pocock
  credits-url: https://github.com/mattpocock/skills
---

# Implement and monitor it

## User questions

Before asking or relaying any user question, read and follow [the user question rules](references/user-questions.md).

Requires [implement-it](../implement-it/SKILL.md), [monitor-it](../monitor-it/SKILL.md), and their prerequisites.

Invoking this skill to deliver a spec authorizes implementation, the commits and normal pushes needed to open its PR, and the monitoring actions described by `monitor-it`, including scheduled checks, scoped fixes, review requests and replies, labels, and assignment. It does not authorize merging. Creating or editing this skill does not start delivery.

## Deliver

If any stage fails, is interrupted, incomplete, or unverifiable, or encounters a missing prerequisite or ambiguous target, preserve the work and leave delivery incomplete. Advance only after the current stage succeeds and its handoff is verified.

1. Read repository instructions. Resolve the authoritative spec and tickets, absolute repository path, intended PR repository and base, and dependency skill paths. Confirm worker and nested implementer/reviewer subagent support and check prerequisite declarations before dispatch; defer full workflows to their workers.
2. Dispatch a fresh worker without inherited conversation history, using `fork_turns="none"` when available, to read and follow `implement-it`. Supply its absolute skill path, repository path, authoritative spec/ticket pointers, target repository and base, relevant user decisions, constraints, and implementation and PR publication authorization. The worker must acquire spec ownership and create or recover its dedicated integration worktree through `implement-it`, preserving the supplied repository checkout. It must complete the implementation gate and PR readiness procedure using its retained context and actual validation evidence. Preserve the issue-tracker closing references in the PR. If PR preparation requires implementation changes, rerun `implement-it` against the original pinned base and mark the PR ready only after the updated SHA passes the full gate. Retain the reviewed integration branch and usable checkout for monitoring. Use the Skill tool when available; otherwise follow `SKILL.md`. Require a report with checkout path, integration branch, original pinned base SHA, final reviewed SHA, review rounds, zero-finding results for both axes, required check results, the implementation report path under `docs/implementations/`, with material findings, decisions, approved deviations, limitations, evidence, and verified PR URL, ready state, repository, base, head repository/branch, and head SHA. Wait for completion.
3. Require the successful implementation and PR report. In the returned absolute checkout, verify its repository and that it is the dedicated integration worktree, then independently verify that the integration branch still points to the reviewed SHA and no task changes remain uncommitted. Require the publication worker's verified result to confirm that the PR is open and ready for review and its repository, base, head repository/branch, and head SHA match the intended target and final reviewed SHA; compare those returned fields without refetching GitHub state. Pass the expected identity and SHA to monitoring, whose worker verifies current state before acting. Any mismatch leaves delivery incomplete. Retain the pinned base, report, and evidence pointers for recovery.
4. Read and invoke `monitor-it` in the parent chat as an explicit start request with the verified PR URL and expected repository/base/head branch and reviewed SHA, checkout path, authoritative spec and tickets, retained implementation report and evidence pointers, relevant user decisions and constraints, and authorization above. Include approved deviations and limitations from implementation in this handoff. Follow its workflow and retain a usable checkout while monitoring requires it.

## User input and recovery

Instruct the worker to return required user questions or approvals to the parent with the relevant draft/options, current progress, and artifact pointers, pausing dependent work. Ask in the parent chat through the User questions procedure, wait for the user's response, and resume the same worker with the actual answer and its scope. Retain the worker identifier and report across user turns. Keep exploration and full tool output in the worker; return concise evidence sufficient to verify each gate.

On a resumed run, inspect the retained checkout and any existing PR before restarting stages. Reuse verified implementation and published PR artifacts; repair incomplete operations rather than creating duplicates. If a worker is unavailable, give its replacement the saved progress, pinned base, reviewed SHA, artifact pointers, and accumulated user decisions, constraints, and approvals with their exact scope. Approval of an earlier draft does not approve a revised draft. Report the incomplete operation and outstanding work on failure.

Report the PR URL, implementation review and check results, and the verified review state: ready for human review, ready for merge, monitoring active, or blocked. Active monitoring is a handoff, not completed delivery. Claim merge readiness only when `monitor-it` passes its merge-readiness gate; report outstanding work on failure.
