---
name: implement-it
description: "Implement a spec with implement-spec, repeating fixes and code-review until both review axes report zero findings."
disable-model-invocation: true
metadata:
  dependency: "implement-spec, code-review"
  credits-author: Matt Pocock
  credits-url: https://github.com/mattpocock/skills
---

# Implement it

Requires Matt Pocock's `implement-spec` and `code-review` skills, their prerequisites, subagent support, and authenticated `gh` for GitHub issues. This skill extends `implement-spec` with a review gate before its finalization and cleanup.

## Implement

1. Locate and read both installed skills. Invoke through the Skill tool when available; otherwise read and follow their `SKILL.md` files. If either skill or a required capability is unavailable, report the missing prerequisite and leave the work incomplete.
2. Read the spec, tickets, repository instructions, and issue-tracker workflow. Pin the starting integration base to a commit SHA before implementation. Preserve that SHA and the authoritative spec pointers for every review round. For resumed work, recover the original base covering the entire spec implementation rather than using the current integration tip.
3. Before implementation starts, apply the issue status step below to the GitHub spec issue. Apply it to each GitHub ticket when work on that ticket begins, including resumed work. For local specs or tickets without a GitHub issue, skip labeling.
4. Invoke `implement-spec` with this explicit override: execute its implementation workflow and the review-and-fix loop below in place of its own review-and-fix step. Have it invoke `code-review`, dispatch fixes, and repeat until the gate passes, then return the review and check results before ticket closure, marking a PR ready, or worktree cleanup. Require its implementers to apply the issue status step before starting each ticket. Preserve its task graph, implementer subagents, TDD, and merger workflow. Override upstream PR creation and publication: return the reviewed implementation to the caller without creating or updating a PR. Leave publication-dependent ticket closure and PR readiness to the caller.

Require implementation and fix workers to report material decisions, tradeoffs, approved deviations, limitations, and evidence pointers alongside their results. Retain these findings for the caller and recovery. Record missing before evidence honestly.

## Implementation report

For a GitHub spec, fetch its authoritative issue number and URL. Create `docs/implementations/<spec-gh-issue-id>.md` in the integration checkout, using the spec issue number, not a child ticket or issue title. Reuse that report on resumed runs; verify its recorded spec URL before editing and preserve unrelated content and any recorded PR details. For a local spec, use its established filesystem-safe identifier instead of a GitHub issue number.

Record the spec URL or local source, ticket pointers, implementation summary, material decisions and tradeoffs, approved deviations with their approval source and scope, limitations, validation results, and durable evidence pointers. State when a category has no entries or evidence is unavailable; do not invent results. Include the integration branch name, its repository identity, and the original pinned base SHA for recovery. Prefer repository paths, commit references, and stable URLs over temporary logs; retain needed evidence durably without copying secrets or unrelated private material.

Create the report during implementation and update it before each review round's commit and checks so it is included in the full integration diff and review gate. Record blocked progress when possible without claiming completion. Keep the final reviewed SHA in the returned report rather than embedding a self-referential commit SHA in the Markdown. Return the report's absolute path to the caller.

## Issue status

Resolve each issue's repository and number from its authoritative pointer. Fetch its current labels with `gh issue view --repo <owner/repo> <number> --json labels`. Ensure `status/in-progress` exists in that repository; create it with `gh label create 'status/in-progress' --repo <owner/repo>` if absent, preserving existing label settings. Use `gh issue edit` to remove every current label starting with `status/` and add `status/in-progress`, preserving all other labels. Pass the exact label names through `--remove-label` and `--add-label`.

Fetch the labels again and verify that `status/in-progress` is the only label starting with `status/` and every previous non-status label remains. If the update or verification fails, report the blocker and leave implementation of that issue incomplete.

## Review and fix

Supply this replacement review-and-fix loop to `implement-spec`.

1. Wait for all implementation and merge work to finish. Update the implementation report, then commit only the task's changes on the integration branch so the review includes them, preserving unrelated user changes. Record the integration `HEAD` SHA and run the repository's required checks.
2. Invoke `code-review` against the original pinned base SHA, supplying the authoritative spec and tickets. Review the entire integration diff each round, including previous fixes. Preserve its independent Standards and Spec subagents and their separate reports.
3. If either axis reports findings, dispatch a single **implementer subagent** with all findings, both reports, the spec pointers, the reviewed SHA, and any failed checks. It must fix every finding within the approved spec, use the upstream implementation and TDD workflow, and report its commits, validation results, and any unresolved findings. Integrate its work through the upstream merger workflow, then repeat from step 1. Failed checks also require an implementer fix round even when the review reports no findings.
4. The gate passes only when the latest complete review reports **zero findings on both axes**, all required checks pass, the integration `HEAD` still equals the reviewed SHA, and no task changes remain uncommitted. A skipped axis, failed or incomplete review, empty diff, or unresolved finding leaves the gate unmet. Any subsequent implementation change requires another review.

Keep the original spec and standards authoritative. Fix findings rather than hiding them, weakening checks, or changing requirements to obtain a clean report. If a finding appears mistaken, give the next review the concrete counterevidence; it remains unresolved until that review withdraws it.

There is no preset round limit. Continue while actionable work remains. If progress requires a user decision, unavailable access, or an external change, report the exact blocker and outstanding findings, preserve the work, and leave the gate unmet. If the same findings recur after a fix, re-examine the cause and change the fix rather than repeating the same attempt.

## Finish

After the gate passes, resume implementation finalization subject to the publication override above. Retain the reviewed integration branch and usable checkout for the caller; clean up only temporary implementation worktrees that are no longer needed. Report the implementation report path, checkout path, original pinned base SHA, integration branch, number of review rounds, final reviewed SHA, check results, material decisions and evidence pointers, and the zero-finding result for each axis. A blocked run must report its unresolved findings instead of claiming completion.
