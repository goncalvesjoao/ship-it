# Monitoring cycle

Loaded only by the fresh monitoring worker dispatched by `monitor-it`. Execute one cycle and return; scheduling and shutdown belong to the main chat. Creating/editing these instructions does not authorize PR actions. Use the supplied authorization and constraints; merging is not authorized.

## Inputs and ownership

Receive PR identity, absolute project/checkout and ledger paths when known, absolute `address-it` skill path, authoritative spec/tickets, user constraints and review preference, authorization, and start/resume or scheduled-tick intent. Scheduled ticks carry the expected automation ID. A scheduling-unavailable instruction requires independent work followed by blocked handoff if continued monitoring is needed.

For scheduled ticks, verify the automation is active and matches the ledger ID before PR writes. Stopped, deleted, superseded, or unverifiable schedules return skipped without PR writes. Explicit start/resume permits an initial cycle while scheduling is inactive. Check the supplied cancellation condition before every external mutation; preserve local work and return if authorization is revoked.

Read repository instructions. For monitored work, recover the supplied ledger or derive `<git-common-dir>/address-it/<owner>/<repo>/<PR-number>.json` from the absolute Git common directory. Preserve finding evidence, pending operations, automation ID, wait deadlines, and retry history. Before the first monitored mutation, use atomic directory creation at `<ledger-path>.lock` for exclusive PR ownership; reconcile interrupted writes and verify the previous owner is inactive before stale-lock takeover. Release only your own lock on exit. If ownership is occupied/unverifiable, return skipped conflict without PR writes. The unused-Copilot handoff may verify writes directly without checkout/ledger, but must first verify no resolving pass owns the PR.

Load current human decisions from the ledger before assessing review mode or dispatching the resolver. Apply each answer only within its recorded scope; later recorded answers supersede older prompt snapshots. Pass the effective constraints, review preference, and scoped authorization to the resolver and preserve the decision records through ledger updates. If recorded decisions cannot be recovered or conflict without a clear supersession, pause affected work and return the limitation or question to the coordinator.

Before monitored external mutations, record intent/target/attempt time and expected result in the ledger, inspect external state afterward, and persist the verified result by temporary-file atomic replacement. Reconcile uncertain operations before retrying. On start/resume, reassess recorded blockers against fresh evidence rather than labels alone.

Recover supplied implementation context from the ledger before resolving feedback, including the report or its durable pointer, evidence pointers, approved deviations, and limitations. Pass relevant context to `address-it` under the scoped decision rules above. Missing or inaccessible supplied evidence leaves dependent decisions pending while independent work continues.

## Entry and review mode

Resolve the PR identity, open state, labels, and Copilot review configuration/activity. For closed or merged PRs, return the terminal state. Determine whether Copilot review is in use from user preference, accessible configuration, and actual review activity/requests. Explicit Copilot opt-in permits monitoring even when automatic review is disabled. A missing review alone does not establish that Copilot is unused. If unknown, return the review-mode question and request inactive scheduling until answered. Fetch failures remain unknown state under Recovery and waits.

If Copilot is unused or not configured for this PR, apply and verify `status/ready-for-review` using Status labels, verify the PR remains open, and return the human-review handoff for coordinator shutdown. This branch needs no checkout/ledger or resolver pass. Use `address-it` when the user asks to address existing feedback.

## Resolve and assess

For Copilot monitoring, read and invoke the supplied `address-it` skill within this worker. This same worker retains ownership across resolution and subsequent readiness mutations; the resolver may dispatch one implementer. Pass the PR identity, project/checkout and ledger paths, spec pointers, constraints, authorization, and cancellation condition. Request all feedback, not a reviewer-limited scope. Missing, interrupted, scoped, or incomplete results cannot satisfy readiness.

Keep PR feedback, code inspection, implementation logs, and validation here. Reconcile pending writes rather than recreating fixes. Record verified push times for updated-head waits; evaluate/request updated-head review on the next cycle after a fix push. Finish independent justified fixes before escalating human decisions or other blockers. Report human questions once through the coordinator, while preserving independent progress.

Evaluate review completion, recovery, and readiness every cycle, including cycles with no new feedback. Pending review/checks return active with an existing deadline; perform no polling loop inside the worker. If a fresh assessment invalidates a readiness label or clears a recorded blocker, verify the necessary status update. If scheduling is unavailable, finish useful work and use Blocked handoff when monitoring remains necessary.

## Review completion

On the first cycle and each new head, inspect automatic review activity, pending requests, and submitted reviews. If none applies and the deadline has not expired, request Copilot review through the supported mechanism, once per head SHA. A comment mentioning Copilot is not a request. An explicit post-timeout resume permits one new request for that same head in the resumed run if none is pending/completed. Confirmed unused/disabled review follows Entry and review mode; other access/capability failures follow Recovery.

A completed review requires author `copilot-pull-request-reviewer[bot]`, populated `submitted_at`, current-head `commit_id`, and state `COMMENTED`, `APPROVED`, or `CHANGES_REQUESTED`. A zero-finding `COMMENTED` review qualifies. Missing, older-head, dismissed, pending, or error-only reviews do not.

| Review wait | Deadline |
| --- | --- |
| Newly opened PR with no findings or submitted reviewer review | 30 minutes after PR creation; apply immediately if already expired. |
| Updated head after a fix push | 30 minutes after the push. |
| Explicit resume after timeout with a newly verified request | 30 minutes after that request; preserve previous timeout history. |

An expired review wait requires Blocked handoff and one comment explaining the missing review, wait start/deadline, PR creation time, and outstanding request.

## Status labels

Before any status transition, read and follow [the resolver's Status labels procedure](../../address-it/SKILL.md#status-labels), including for the unused-Copilot handoff without invoking a resolver pass. Uncertain/failed transitions remain pending under Recovery and waits.

## Recovery and waits

Record each wait's event, head SHA, request/check-run IDs, start, deadline, and observed status in the ledger. End waits when their event occurs, becomes irrelevant, or is handed off; preserve history. Polls, unrelated comments, restarts, and schedule restoration never reset deadlines. New heads supersede old-head waits. After expiration, resume alone creates no new wait; require completion evidence or a genuinely new request/check run. For recovered pushes, use the recorded attempt time as the review-wait start when actual push time is unavailable.

CI uses its documented maximum duration plus queue allowance, otherwise **30 minutes** from check-run creation or first observation when unavailable. Other transient readiness waits, including unknown mergeability, use a 30-minute fallback. Expired waits preventing readiness require Blocked handoff.

Network/server failures allow **three consecutive failed cycles**, persisted across restarts and cleared after a successful complete fetch. Below the retry limit, return active for a later tick without dependent writes; do not continue into readiness on partial evidence. Preserve verified state and stop dependent writes. Honor retry-after/reset times for rate limits, with a maximum 30-minute wait. Exhausted retries/waits require Blocked handoff. Permission failures, unavailable capabilities, and unsupported operations require handoff without repeated attempts. Persist early-fetch recovery using the supplied ledger or a path derived from the Git project and PR identity; if unavailable, report the limitation rather than losing retry history.

## Blocked handoff

Finish independent justified fixes before handing off, using the resolver when possible. A blocker exists when no autonomous action or bounded wait can resolve remaining work, including exhausted retries, unavailable access/scheduling/resolution channels, required human decisions/approvals, contradictory feedback, or expired waits. Progressing reviews/checks within deadlines and fixable failures remain active work.

Apply `status/blocked` using Status labels. Leave one explanatory comment if the reason/next action is not clear from existing discussion; review timeouts always require their comment. Record outstanding findings, head SHA, and handoff reason, then return blocked for coordinator shutdown. Report unverified writes explicitly.

## Finish

A fresh complete fetch must confirm:

- A completed current-head Copilot review under Review completion.
- Every finding has an evidenced disposition; fixes are pushed and validated.
- All review conversations are resolved; findings outside threads have explicit closure or reviewer acknowledgment.
- Required checks pass; no active changes-requested review or pending reviewer request remains.
- Required approvals and merge rules pass, and GitHub confirms mergeability.
- No implementer is active or task changes uncommitted; remote head equals the validated/reviewed SHA.

Recheck head/review state immediately before applying `status/ready-for-merge`. Assign the author only if still unassigned, preserving existing assignments. Verify labels, assignees, and head afterward; changed state reopens the gate and removes the readiness label. Record the verified ready SHA and return ready for merge for coordinator shutdown.

## Return compact result

Persist the cycle result and detailed evidence in the ledger when one is required. The unused-Copilot handoff and closed/merged branch may return without creating a ledger. Return only:

- Outcome: active, ready for human review, ready for merge, blocked, closed/merged, needs review-mode decision, skipped inactive, or skipped ownership conflict.
- PR URL, checkout/ledger paths, observed/verified head SHA, verified changes this cycle, and unverified operations.
- Whether another tick is needed, any preserved deadline/retry-after time, and required human question/action.

Summarize verified fix commits/checks, rejected-finding reasons, labels, and assignment only when changed or needed for a terminal report. Keep raw reviews, diffs, logs, review metadata, and readiness reasoning in the ledger. Readiness/handoff is provisional until the coordinator verifies monitor shutdown. Interrupted cycles preserve pending writes and never claim success.
