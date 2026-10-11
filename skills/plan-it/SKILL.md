---
name: plan-it
description: "Turn a discussed feature into a GitHub spec issue in the parent chat, then delegate approved sub-issues to a fresh subagent."
metadata:
  dependency: "to-spec, to-tickets"
  credits-author: Matt Pocock
  credits-url: https://github.com/mattpocock/skills
---

# Plan it

## User questions

Before asking or relaying any user question, read and follow [the user question rules](references/user-questions.md).

Requires [spec-it](../spec-it/SKILL.md), [ticket-it](../ticket-it/SKILL.md), their prerequisites, and subagent support.

Invoking this skill authorizes publishing the spec and approved tickets through those skills. Preserve their user confirmation and approval steps. Creating or editing this skill does not start publication.

## Orchestrate

1. Read repository instructions and resolve the absolute repository path, target GitHub repository, tracker configuration, and both local skill paths. Resolve missing prerequisites or an ambiguous target before publication.
2. Read and follow `spec-it` and its upstream dependencies directly in the parent chat, using the Skill tool when available. This keeps the current discussion and codebase understanding available to `to-spec`. Preserve its test-seam confirmation and wait for successful publication with the verified issue URL and labels.
3. Independently fetch the returned issue and verify its target repository, that it is an issue rather than a pull request, and that it has `spec` and a `status/` label. Start the next stage only after `spec-it` reports success and this verification passes.
4. Start a fresh worker for `ticket-it` with conversation inheritance disabled, such as `fork_turns="none"` when supported. Supply its absolute skill path, repository path, verified parent issue URL, tracker configuration, and any user constraints or decisions absent from the published spec. Have it read and follow that skill and its upstream dependencies, fetching the parent's full body and comments. Require the proposed breakdown for user approval before publication unless that exact breakdown was already approved. Handle input as described below and wait for its verified completion report.
5. Return the parent and child URLs with their blockers and verification results. Claim completion only when both stages succeeded and every approved slice has a verified ticket.

## User input

Give the ticketing worker these instructions: when a delegated skill needs a user answer or approval, return to the parent with the question, relevant draft or options, current progress, and existing artifact URLs. Pause dependent work until the parent supplies the user's response.

Ask the question in the parent chat through the User questions procedure and wait for the user. Relay the actual answer and its scope to the same worker, resuming it with the available follow-up tool. Repeat for further questions or revisions. Preserve `to-tickets`' breakdown review; delegation does not waive it. A request to run `plan-it` is not approval of an unseen breakdown.

## Recovery

If a replacement worker is needed, pass the user's accumulated decisions, constraints, and approvals with their exact scope, alongside the saved progress and artifact pointers. Do not treat approval of an earlier draft as approval of a revised draft.

On failure, interruption, or unverifiable results, leave the workflow incomplete and report the completed stage, existing issue URLs, incomplete operation, and remaining work. Retain the ticketing worker identifier and artifact pointers across user turns. Resume the spec stage in the parent chat or the existing ticketing worker where possible; if the worker is unavailable, give a replacement the recorded progress and have it inspect GitHub state before continuing. Reuse published issues and repair incomplete operations according to the relevant skills rather than creating duplicates. After a verified spec stage, resume ticketing directly against that parent.
