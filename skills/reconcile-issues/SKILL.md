---
name: reconcile-issues
description: Find open GitHub issues whose requirements are already complete, verify the completion evidence, and close them as completed. Use for issue cleanup or reconciling issues after merged work.
---

# Reconcile issues

## Repository identity

Before GitHub access or Git writes/network operations, read and follow [the shared identity instructions](references/github-identity.md). All `gh` commands below use the required identity helper prefix.

Before asking any user question, read and follow [the user question rules](references/user-questions.md).

## Find candidates

Resolve the target repository from the user's reference or the current checkout. Keep discovery within that repository and any issue numbers, labels, or other filters the user supplied. If the repository is ambiguous, ask before GitHub access.

Read the repository's issue-tracker policy and completion rules. List open issues with pagination. Use completion labels, project status, checked tasks, completion comments, and linked merged PRs to prioritize inspection, not as proof by themselves. Report any retrieval limit or inaccessible evidence rather than claiming the scan was exhaustive.

For each candidate, read the full issue body, comments, timeline, linked PRs, and native sub-issues with pagination. Follow relevant completion reports and repository evidence. An implementation report under `docs/implementations/<issue-number>.md`, when present, is a starting point to verify against current GitHub state.

## Verify completion

Close an issue only when evidence accounts for every requirement and repository-defined acceptance gate:

- For implementation work, verify the relevant PRs actually merged into the intended delivery branch and cover the issue's whole scope. A PR mention, closing keyword, passing checks, or review-ready label alone is insufficient.
- For work completed without a PR, require concrete evidence appropriate to the task, such as a delivered document or an explicit completion confirmation from the responsible maintainer. Identify the evidence for each requirement.
- Check later comments, reopened work, reversions, and follow-up decisions that invalidate the completion claim. An unresolved required deployment, manual check, or acceptance step keeps the issue open.
- For parent/spec issues, inspect every native child and the parent's own requirements. Closed children may be duplicates or abandoned work; verify their completion reasons and evidence. Complete children do not by themselves prove the parent complete. Evaluate children first and recheck the parent afterward.

Leave partial, conflicting, or unverifiable candidates open and report what evidence is missing. Leave duplicate, abandoned, or obsolete issues open unless the user separately requests that kind of cleanup; those are not completed work.

## Close verified issues

If the user requested an audit, preview, or draft, return the proposed closures with evidence and make no changes. A request to find and close completed issues authorizes closures within that scope. If closure has not been authorized, present the verified list for approval before writing.

Process verified issues one at a time:

1. Refetch the issue's state, body, comments, relationships, and relevant PR state immediately before closing. Reevaluate if the evidence or requirements changed. Skip an issue already closed, preserving its existing closure reason.
2. Close as completed with a concise comment linking the completion evidence and explaining how it satisfies the scope:

   ```sh
   gh issue close <number> --repo <owner/repo> --reason completed --comment <evidence-summary>
   ```

   Use safe argument quoting. Preserve the issue's title, body, labels, assignments, and project fields. Do not merge PRs or implement missing work.
3. Read the issue back and verify `state` is `CLOSED` and `stateReason` is `COMPLETED`. Record the issue URL and evidence before moving on.

If a write fails or its outcome is uncertain, stop further closures and inspect the affected issue before retrying. Report confirmed closures and the remaining candidates; avoid duplicate comments on retries.

Return closed issue links with their completion evidence, skipped candidates with their missing requirements, and the scan's scope and coverage. Distinguish proposed closures from verified writes.
