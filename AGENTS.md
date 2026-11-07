<!-- BEGIN: Neene's Production-Quality Rules (do not remove) -->
# Production-Quality Development Rules — NON-NEGOTIABLE

These rules apply to **every agent** (Claude, Claude Code, Cursor, Codex, Copilot, or any other AI assistant) working on any Sacred Ground or client project. They are binding throughout planning, implementation, testing, and delivery.

## 1. Production-Quality Development Rule

**You are building production software for real clients, not experimenting with a prototype.**

Every feature, modification, and correction must be treated as part of an interconnected system. Your responsibility is not simply to make the requested change work. Your responsibility is to ensure that the entire application continues to function correctly after that change.

**Follow these rules without exception:**

1. **No Band-Aid Fixes.** Do not stack patches, workarounds, or temporary corrections on top of underlying problems. Identify the root cause and correct the architecture or implementation properly. Rebuild the affected component when necessary, while preserving working functionality.
2. **Understand Before Changing.** Before modifying anything, trace its dependencies, integrations, data flows, and interactions with other parts of the application. Understand what your change could potentially break.
3. **Walk Every Path.** After making changes, systematically test every affected workflow from beginning to end, including buttons, forms, navigation, calculations, data storage, integrations, error handling, and interactions between features. Test not only what should work but also what could go wrong.
4. **Regression Testing Is Mandatory.** Verify that previously working functionality still works. A successful new feature is not a success if it breaks an existing one.
5. **Think Like the Client.** Assume the client will use the application in unexpected ways. Test realistic user scenarios, unusual sequences, incomplete actions, repeated clicks, and edge cases.
6. **Take the Time Required.** If comprehensive verification takes an hour, take the hour. Speed is never more important than reliability. Do not skip testing to finish faster.
7. **Never Claim Something Works Without Evidence.** Clearly distinguish between functionality that has been tested successfully, functionality that has only been reviewed, and functionality that remains unverified. Never claim a complete test if you have not performed one.
8. **Deliver Stable Systems.** The client should receive a dependable, fully integrated application, not become an unpaid tester who repeatedly discovers problems after delivery.

**Your definition of DONE is not "the code runs." Your definition of DONE is "the requested functionality works, affected workflows have been verified, existing functionality has not regressed, and there are no known unresolved critical issues."**

**The goal is to build it correctly, verify it thoroughly, and deliver it confidently — not to enter an endless cycle of fixing one problem while creating another.**

**Before making any change, create an internal impact map of everything the change touches. Afterward, execute a complete regression checklist covering those dependencies and all critical end-to-end workflows. Do not rely on assumptions, code inspection alone, or a successful build. Actually exercise the application wherever testing tools are available. If a test cannot be performed, explicitly identify it as unverified. Do not deploy or declare completion when critical workflows remain unverified.**

> "You are not finished when the new feature works. You are finished when the new feature works, everything it touches still works, and you have verified that with evidence rather than assumptions."

## 2. Mandatory Rule Discovery and Compliance

**Before beginning ANY task, you must locate, read, and apply all applicable project rules and development standards.**

Do not assume you remember the rules from a previous conversation. Do not assume they have automatically loaded into your context.

At the beginning of every task:

1. Locate and read the project's governing instructions, including applicable Cursor rules, `AGENTS.md`, `CLAUDE.md`, and any project-specific standards maintained in the repository or GitHub.
2. Confirm which rules apply to the current task before making changes.
3. If a required rule file is missing, inaccessible, or contradictory, stop and report the issue rather than proceeding under assumptions.
4. Treat these instructions as binding throughout planning, implementation, testing, and delivery.
5. Before declaring the task complete, verify that the work complies with those rules and identify any exceptions.

**You are not permitted to begin implementation until the applicable rules have been reviewed.**

**Never claim you have read or followed a rule unless you actually accessed and reviewed it during the current task.**

Your responsibility includes discovering and following the rules without requiring the client to remind you that they exist.

## 3. Mandatory Sandbox Testing Before Deployment

**ALWAYS build, run, and thoroughly test all changes in the sandbox environment FIRST. NEVER deploy directly to production.**

Before deployment, verify that the application builds successfully, produces zero errors, passes all applicable tests, and that every affected feature, workflow, integration, and dependency functions correctly without breaking existing functionality.

**A successful build alone does NOT mean the application is ready.**

If ANY errors, failed tests, or regressions are discovered, resolve the root cause and repeat the entire verification process.

**Deployment is permitted ONLY after sandbox testing is complete, all required checks pass, and there are no known unresolved errors or critical issues. If anything remains untested, report it explicitly rather than assuming it works.**

**NO VERIFIED SANDBOX SUCCESS = NO DEPLOYMENT.**
<!-- END: Neene's Production-Quality Rules -->
