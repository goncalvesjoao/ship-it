---
name: spec-it
description: "Publish a GitHub spec issue using Matt Pocock's to-spec skill, adding spec and defaulting to status/todo when no status/ label exists."
disable-model-invocation: true
metadata:
  dependency: "to-spec"
  credits-author: Matt Pocock
  credits-url: https://github.com/mattpocock/skills
---

# Spec it

## User questions

Before asking or relaying any user question, read and follow [the user question rules](references/user-questions.md).

Requires Matt Pocock's `to-spec` skill, its prerequisites, and authenticated GitHub CLI (`gh`).

1. Locate and read the installed `to-spec` skill. Invoke it using the Skill tool when available; otherwise follow its `SKILL.md`. Preserve its exploration, test-seam confirmation, spec template, and triage labels, with GitHub as the publishing destination. If a prerequisite is missing or the target repository is ambiguous, report the blocker before publishing.
2. Retain the published issue URL and resolve its repository and issue number. Continue only when `to-spec` has published a GitHub issue. On a resumed labeling attempt, reuse that issue instead of publishing another spec.
3. Read the issue's current labels:

   ```sh
   gh issue view <issue-number> --repo <owner/repo> --json url,labels
   ```

   Add `spec` only if it is missing. Add `status/todo` only if no current label starts with `status/`. Preserve all existing labels, including any existing status and upstream triage labels.
4. For each label that needs adding, check whether it exists in the repository. Create missing repository labels with `gh label create <label> --repo <owner/repo>`, preserving existing label settings. Add only the missing issue labels with `gh issue edit <issue-number> --repo <owner/repo> --add-label <label>`. Use explicit repository arguments and quote values safely.
5. Fetch the issue labels again. Verify that `spec` is present and at least one label starts with `status/`. Return the issue URL and the resulting labels only after verification succeeds.

If labeling or verification fails, report the issue URL and incomplete operation. Inspect the current labels before retrying so recovery updates the existing issue without replacing its status or creating a duplicate.
