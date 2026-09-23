# Development quota stop rule

User clarification (2026-09-22 / 23, Asia/Shanghai): stop development when the account quota has **40% remaining**, i.e. **60% used**. The earlier interpretation of stopping at 40% used is superseded.

- Read current account usage with the official Codex usage tool periodically during active work. This is an account-wide weekly window, not a task-specific token counter.
- Reserve enough capacity for a complete handoff. Near 60% used, stop assigning new work, collect parallel agents' checkpoints, write the handoff, then pause development until the user explicitly resumes it.
- Do not redeem a reset credit, change subscriptions or create a recurring task to avoid the stop.
- The stop rule supersedes the earlier instruction to work without stopping until finished. It does not make unfinished work complete.
- Latest observed sample before this note: 42% used / 58% remaining. Samples are discrete, so a precise 60.0% cutoff cannot be guaranteed.

Current implementation status is tracked in WORKBOARD.md. A final quota handoff will distinguish code written, tests actually passed, code loaded into DSH, live UI acceptance and outstanding issues.
