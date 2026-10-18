# Offline behavior checks

Use the coordinator, monitoring reference, and resolver skill with each scenario below and report the next actions, terminal label if any, and schedule state. Treat these as simulated inputs; make no GitHub, schedule, or source changes. Verify outcomes against these criteria when changing the workflow.

| Scenario | Required outcome |
| --- | --- |
| Current-head Copilot review is `COMMENTED`, submitted, and has zero findings. All other readiness conditions pass. | Apply `status/ready-for-merge`, use the configured human reviewer for machine-authored PRs, otherwise assign the author if unassigned; record the ready SHA, disable monitoring. |
| Copilot monitoring is enabled. PR was created 31 minutes ago, has no review or findings, and no independent work remains. | Apply `status/blocked`, explain the review timeout, disable monitoring. Do not create a request that silently resets the expired creation deadline. |
| Current-head review passes, but required CI has been pending for 31 minutes with no documented duration. | Apply `status/blocked`, explain the stalled check and next action as needed, disable monitoring. |
| A push succeeded but the process stopped before recording success. The remote contains the intended commit. | Reconcile the intended write, verify the remote SHA, mark the fix handled, and evaluate/request review. Do not recreate the fix or push a duplicate commit. |
| One finding requires a product decision; another is an independent reproducible bug. | Ask for the decision once, dispatch one implementer for the bug, verify/push the fix, then hand off as blocked when no independent work or bounded wait remains. |
| First GitHub fetch fails with a transient server error. The next succeeds. | Keep monitoring, perform no writes based on unknown state, clear the failure count after success. Three consecutive failed cycles instead trigger blocked handoff. |
| User explicitly resumes a paused monitor; PR needs work and has an unexpired wait. | Reconcile fresh state, reactivate the matching schedule, verify one active schedule, preserve the original wait deadline. |
| User explicitly resumes; recorded automation was deleted but another matching active monitor exists. | Reuse the matching monitor and update its ID in the ledger. Create no duplicate. |
| User explicitly resumes; recorded automation was deleted, no replacement exists, PR needs work. | Create and verify one replacement schedule, preserve ledger and valid wait deadlines. |
| User explicitly resumes a paused/deleted monitor; PR is already ready or closed. | Reconcile terminal state, leave monitoring inactive, create no replacement. |
| An old scheduled tick arrives after its automation was paused/deleted. | Do not recreate/reactivate the automation. Preserve state and respect the inactive schedule. |
| User resumes after the CI deadline expired; the same check run is still pending. | Keep the expired deadline and hand off as blocked. Resume alone does not grant that run another 30 minutes. |
| Readiness passes with `status/in-progress`, someone else's `status/blocked`, and `bug` applied. | Remove both competing status labels and verify removal before adding `status/ready-for-merge`. Preserve `bug`, verify only the ready status remains, disable monitoring. |
| A blocked handoff has `status/blocked` already applied alongside `status/in-progress`. | Remove `status/in-progress` and verify that `status/blocked` is the only status label, then disable monitoring. |
| Removing a competing status label fails or has an uncertain result. | Keep the label transition pending in the ledger, reconcile the actual labels before adding the target, and report failure if it cannot be completed. |
| A justified finding is ready for implementation with `status/ready-for-review` applied. | Replace it with `status/in-progress` and verify the transition before dispatching the implementer. |
| The implementer finishes; resolver validation passes, fixes are pushed, and GitHub confirms the new head SHA. | Replace `status/in-progress` with `status/ready-for-review`, verify it is the only status label, and continue waiting for current-head review. |
| The implementer finishes locally, but validation fails or the push is unverified. | Keep implementation pending, do not apply `status/ready-for-review`, and continue useful work or follow the blocked handoff. |
| Saved `copilot_review: false`; PR has no Copilot review and all other readiness gates pass. | Run resolution and readiness, apply `status/ready-for-merge`, verify configured human handoff, disable monitoring; create no Copilot request. |
| Copilot is disabled; required CI is pending within its deadline. | Keep monitoring with the original deadline; request neither Copilot nor human review yet. |
| Copilot is disabled; required human approval is the only remaining gate. | Apply `status/blocked`, request the configured human reviewer, explain the required approval, disable monitoring. |
| Setup has no saved Copilot choice. | Ask Yes or No, wait for the answer, and include `copilot_review` in the policy draft. Reruns preserve the saved answer. |
| Repository configuration disables Copilot review for this PR; a matching monitor exists. | Apply and verify `status/ready-for-review`, disable and verify the matching monitor, create no replacement. |
| No Copilot review exists and configuration is inaccessible; user preference is unknown. | Ask which review mode to use, leave scheduling inactive. Do not infer disabled review or apply a terminal status. |
| Automatic Copilot review is disabled, but user explicitly requests Copilot monitoring. | Run the monitoring cycle, request review through the supported mechanism, schedule only if useful work or a bounded wait remains. |
| Copilot state fetch fails. | Preserve unknown state and follow bounded recovery; do not label ready for human review based on the failure. |
| Human-review handoff or merge-readiness writes succeed, but monitor shutdown cannot be verified. | Preserve the verified outcome and ready SHA, report shutdown failure, and do not claim completed handoff/readiness or create a replacement. |
| A heartbeat starts with a valid active automation and ledger ID. | Coordinator loads only coordinator instructions and dispatches one fresh worker without inherited chat history, passing authorization, constraints, cancellation condition, spec and ledger pointers. Monitoring worker owns PR fetching, feedback resolution, review requests, deadlines, and merge readiness; coordinator owns scheduling and uses compact verified outcomes without repeating PR fetches. Raw GitHub payloads and deadline reasoning remain in the worker. |
| A fresh worker sees an unchanged pending review within its deadline. | Monitoring worker recovers the deadline, invokes the resolver, and returns active without a waiting loop; coordinator keeps scheduling without fetching raw PR state. |
| Monitoring is stopped while an implementer has unpublished local fixes. | Interrupt cycle and implementer, preserve work, disable schedules, and make no subsequent push or conversation-resolution write. |
| A cycle is interrupted after a PR mutation but before returning. | Fresh worker reconciles the pending operation from the ledger; coordinator does not claim completion or duplicate the write. |
| Another tick arrives while a cycle is running. | Skip the tick; start no second cycle or implementer. |
| Review mode becomes unknown while a matching monitor is active. | Coordinator asks the review-mode question, disables and verifies the existing monitor, and resumes only after an explicit answer/start request. |
| The first pre-mode fetch fails transiently before a ledger exists. | Initialize recovery state using the supplied ledger or Git project/PR identity, persist the failure count, and preserve unknown review mode. If persistence is unavailable, report the limitation for handoff. |
| User invokes address-it for human feedback with Copilot disabled. | Ignore Copilot configuration, evaluate existing feedback, delegate justified fixes, validate and verify the push, reply with evidence, and return review-ready with outstanding acknowledgments. Create no schedule or Copilot request. |
| A resolution pass has no actionable feedback, an old PR, and no Copilot review. | Report no actionable feedback; create no timeout, blocked label, Copilot request, or schedule, and claim no merge readiness. |
| Resolved fixes are pushed, but the human changes-requested review and CI remain pending. | Preserve the human review state, report review-ready and outstanding CI/acknowledgment, and return without polling or claiming merge readiness. |
| A resolution pass overlaps an active scheduled cycle or cannot verify cycle ownership. | Report the ownership conflict, make no concurrent PR writes, and preserve schedule state. |
| A resolution pass encounters a required product decision plus an independent bug. | Fix and verify the independent bug, ask for the decision, and hand off as blocked for the unresolved requirement; create no schedule. |
| A resolution pass encounters partial feedback fetch or an interrupted push. | Preserve unknown/pending state, reconcile any prior write before repeating it, and report incomplete work; create no retry schedule or false readiness. |
| The same PR feedback and constraints are supplied by a user and by monitor-it. | Resolve feedback identically in both runs. Return evidence without schedules, new review requests, polling deadlines, assignment, or establishing merge readiness. Resolver may invalidate an existing stale readiness label. The monitoring worker separately evaluates monitoring requirements. |
| A resolver reports only a requested reviewer scope while other feedback remains unresolved. | Report excluded unresolved feedback and scope; monitoring worker cannot treat that report as satisfying its complete readiness gate. |
| Two resolver/coordinator writers try to acquire PR ownership simultaneously. | Atomic lock-directory creation admits one owner; the other reports the conflict without PR writes. Atomic ledger replacement alone is insufficient ownership. |
| Monitoring worker invokes the resolver while holding exclusive pass ownership. | Resolver verifies the lock belongs to the same pass and reuses it; it does not reacquire or release the monitoring worker's lock. Standalone resolver ownership remains exclusive. |
| Monitoring worker supplies a verified noncanonical ledger path to the resolver. | Resolver preserves that ledger and same-pass lock instead of deriving a different path; findings, pending writes, and caller-owned waits remain continuous. |
| User answers a product question between ticks; the saved heartbeat still carries the older constraint. | Coordinator persists and verifies the actual answer and scope under exclusive ownership. Every later worker loads the decision from the ledger and passes effective constraints to the resolver; the older prompt cannot override it. Preserve wait deadlines and unrelated decisions. |
| A consequential answer arrives during an active cycle, or its ledger write fails. | Interrupt affected work and reconcile ownership before saving the answer. Resume affected work only after persistence is verified; on failure report the limitation and keep it paused. An answer alone does not reactivate stopped monitoring. |
| Delivery supplies an approved implementation deviation and its evidence, absent from the PR description; a later fresh tick receives feedback challenging it. | Coordinator persists and verifies implementation context in the PR ledger. Every worker recovers it and passes relevant decisions/evidence to the resolver, which evaluates feedback within approved scope. Later human answers supersede only their stated scope; missing evidence leaves dependent decisions pending. |
| Either skill receives spec issue `#42`; `42.md` identifies its integration branch but contains no PR entry. | Verify the report identity, resolve the unique associated PR through GitHub, and retain implementation context in the ledger. |
| The report is absent locally but available in an existing worktree or branch. | Recover and verify the report before resolving its integration branch through GitHub. |
| A report is absent everywhere; GitHub links one PR to the spec or its verified tickets. | Resolve that PR through verified issue links and continue the normal workflow. |
| Numeric input `#42` has no associated PR, but an unrelated PR `#42` exists. | Report no matching PR; numeric input remains a spec issue ID. |
| A report is unreadable or conflicts with the supplied spec/repository, candidate lookup is incomplete, or multiple PRs match. | Report the blocker or ambiguity before PR or schedule writes. |
| A legacy report contains a stale PR entry and a verified integration branch. | Resolve through GitHub using the branch and issue association, ignoring the stored PR entry. |
| Caller supplies an explicit PR URL or a scheduled tick supplies a verified PR identity. | Bypass issue lookup, preserve supplied context and same-pass ownership, and continue the normal workflow. |
| implement-it finalizes a reviewed implementation with a report. | Verify and return the published PR without adding a PR entry, committing a report update, or starting a post-publication implementation gate. |
| implement-it resumes with a clean HEAD with exact-SHA passing checks and both zero-finding implementation reviews against the pinned base. | Reuse verified validation evidence without running the suite again. |
| Validation evidence lacks an exact SHA, covers a different HEAD, has failed/incomplete checks, or omits a review axis for governed work. | Run required validation; governed work must pass the full implementation gate before PR readiness. |
| The SHA matches but the user requests fresh checks, required checks change, or the validation environment changes. | Run fresh validation rather than relying on prior results. |
| An existing PR matches the validated HEAD, target repositories/base/branch, intended description and closing references, requested draft state, and required label. | Attach and return the verified PR without regenerating its body, rerunning checks, or writing to GitHub. |
| An existing PR has a stale description, different head SHA or draft state, or missing review label. | Continue with that PR and repair pending work; a label-only repair preserves its correct description and reused validation. |
| PR preparation changes the implementation after validation. | Pass the full governed implementation gate on the new SHA before PR readiness; prior results cannot authorize the changed HEAD. |
| monitor-it receives an explicit PR URL or a verified caller/tick identity. | Coordinator passes the identity without fetching live PR state; worker verifies identity and current state before dependent writes. |
| Delivery's publication worker returns verified PR metadata and SHA. | Parent compares returned identity/SHA with the intended target and local reviewed HEAD; monitoring worker checks live state without a duplicate parent fetch. |
| A worker observes a different PR head or target from the supplied publication result. | Reconcile current state before dependent writes; prior publication evidence does not establish readiness on a changed head. |
| Required lint, formatting, and tests are read-only and use independent resources. | Run them concurrently, await every command, and retain every exit status; any failed check keeps the gate unmet. |
| Tests depend on a build, share browser/server state, or their command already builds. | Preserve dependency order and serialize conflicting suites; avoid duplicate builds without removing required checks. |

## User question routing

Apply these scenarios to each Ship-it skill, including questions from upstream skills and nested workers.

| Scenario | Required outcome |
| --- | --- |
| A structured question tool is available and permitted for the question type and mode. | Ask through that tool using its schema; do not substitute a chat-only question. |
| No structured question tool is available, or available tools prohibit this question type or mode. | Explain the tool limitation before asking in chat; preserve the existing answer or approval gate. |
| A nested worker needs a user decision or approval. | Return the question, draft/options, and progress through parents to the user-facing coordinator. Coordinator uses the permitted structured tool or explains the fallback, then relays the actual answer and scope to the worker. |
| A required question has no submitted answer, but time passes or an option is preselected. | Keep dependent work paused and continue only independent work; infer no answer or approval. |

## Draft PR implementation

| Scenario | Required outcome |
| --- | --- |
| First ticket merges while later tickets and checks remain incomplete. | Let implement-spec create or reuse the initial draft and description with honest progress and closing references. Do not invoke pr, apply readiness labels, or close tickets early. |
| Draft creation succeeds remotely but its response is lost. | Find and verify the existing PR before retrying; create no duplicate. |
| Review finds issues or required checks fail after draft publication. | Keep the PR draft, preserve the work and report, and continue the fix loop. Draft publication does not satisfy the gate. |
| Both review axes and required checks pass on the current clean HEAD. | Use pr to finalize the description unless already correct, verify the remote SHA, mark ready, and verify the sole status label is status/ready-for-review. |
| A resumed ready PR needs implementation changes. | Convert to draft, remove stale readiness statuses, and require the full gate on the changed SHA before restoring readiness. |
| A resumed implementation report identifies a missing or conflicting integration branch. | Report a blocker; do not create a replacement branch or publish unrelated checkout contents. |

## Implementation preflight and review

| Scenario | Required outcome |
| --- | --- |
| A prerequisite issue is closed, but its implementation commit is absent from the integration history. | Verify and integrate the completed prerequisite before dependent implementation, preserving the original pinned review base. Issue closure alone does not satisfy preflight. |
| Two specs use isolated worktrees but change the same adapter contract. | Coordinate the interface and integration order before dependent writers start; pass prerequisite commits and shared-file ownership to workers. |
| Existing lint/test commands have neither CI coverage nor a configured hook. | Report the missing guardrail and run required local checks. Add infrastructure only within authorized scope. |
| A reference cannot be redistributed, but local acquisition or another permitted reference has not been investigated. | Investigate feasible authorized alternatives before blocked handoff; preserve reuse and activation gates. |
| Alternatives are exhausted; progress needs a specific permission or external evidence. | Preserve work, report investigated alternatives and the exact dependency, leave the gate unmet, and follow the existing blocked handoff. |
| Full checks and both reviews pass; only the final outcomes remain to be recorded. | Write the exact-SHA validation record outside tracked files and report it in the PR/final response. Create no report-only commit or extra validation round. |
| A necessary report correction is committed after passing checks. | Validate and review the new HEAD; documentation changes do not silently inherit exact-SHA evidence. |
| A resumed run has a matching validation record but its evidence files are missing. | Treat evidence as incomplete and run fresh validation before readiness. |
| An access block stops a job, but an attached manual request can still enqueue follow-up traffic. | Spec review traces the follow-up transition and rejects the implementation; add a regression asserting terminal state and bounded request count before repeating the gate. |
| A mixed-source job saves some results before another source blocks. | Review retained results, truthful partial outcome and follow-up behavior; passing the single-source path alone is insufficient. |

## Integration worktree isolation

| Scenario | Required outcome |
| --- | --- |
| Two sessions implement different specs from the same primary checkout. | Acquire separate spec ownership locks and use separate integration branches and worktrees. Preserve the primary checkout's branch, index, and files. |
| Two sessions start the same spec before its report exists. | Atomic lock-directory creation admits one owner. The other reports the ownership conflict without issue, checkout, or PR writes. |
| A run resumes with a report and an inactive prior owner. | Verify owner inactivity, acquire ownership, reconcile report and worktree identity, and reuse the dedicated checkout, branch, and original base. |
| An owner appears old but its activity cannot be established. | Preserve its lock and work; report the blocker without takeover. |
| Interruption occurs after worktree creation but before the first report. | Recover the spec, checkout, branch, and original base from the ownership record and Git state after verifying the old owner is inactive. Do not create a duplicate integration branch. |
| A legacy integration branch is checked out in the primary checkout or another active worktree. | Report the conflict and preserve that checkout. Do not switch, reset, stash, or force-checkout its branch. |
| The recorded dedicated worktree is gone, but its integration branch survives and is not checked out elsewhere. | After acquiring ownership, recreate a dedicated worktree on the existing branch without resetting it or choosing a new base. |
| A merger inherits the primary checkout as its working directory. | Use the supplied absolute integration checkout and verify its repository/branch before merging. No primary-checkout mutation. |
| A run finishes, blocks, or pauses with a nested writer still active. | Stop or await the writer before releasing ownership. Preserve the integration checkout and task work; retain the lock if inactivity cannot be verified. |
| A PR has no review findings but conflicts with its freshly fetched base. | Delegate base-into-head conflict resolution, preserve both intended behaviors, validate the merge commit, normal-push and verify GitHub head, then return review-ready with base/head and conflict evidence. Create no schedule or review request. |
| GitHub mergeability is unknown or the local merge check fails to run. | Keep conflict status unknown and report incomplete evidence; do not infer a conflict or a clean merge. |
| The checkout contains unrelated edits or another in-progress merge. | Preserve the checkout and use an isolated clean checkout of the verified PR head for the conflict check and resolution. |
| One conflict requires a product decision while another finding is independently fixable. | Preserve unresolved merge work, complete the independent fix in a clean checkout, validate and verify its push, and report the decision blocker. Do not publish an unfinished merge. |
| Conflict resolution passes, but the base advances after validation. | Report the new base SHA and conflict status as outstanding for another pass; do not claim the earlier merge check covers the new base. |

## Repository identity

| Scenario | Required outcome |
| --- | --- |
| A fresh ticketing, implementation, merger, PR, or nested fix worker has no inherited shell environment. | Receive the identity reference, policy and checkout pointers, resolve the helper through its own common directory, and run each gh/Git operation with the policy account. |
| A scheduled tick resumes on a different machine without local setup, or its saved login disagrees with current policy. | Stop affected access/writes without a human fallback, preserve work, pause monitoring, and report the local setup blocker without attempting a GitHub label/comment. |
| Machine-authored PR reaches merge readiness or a blocked handoff. | Verify a request to or existing review from the configured human reviewer; assign that human only if assignment is needed and empty. Never assign the machine author. Missing eligibility leaves handoff incomplete. |
| Machine-authored PR reaches implementation readiness at `status/ready-for-review`. | Preserve the configured reviewer for later handoff; create no human review request yet. |
