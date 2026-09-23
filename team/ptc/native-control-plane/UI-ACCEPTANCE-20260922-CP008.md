# CP008 native UI acceptance — 2026-09-22

Workspace: `D:\Newtest\DSH\ATE-Coding-Flow`; browser: existing DSH 3080 tab.

- Official restart: gates A/B/C passed; service boot succeeded. Evidence folder: `C:\Users\nvt10241\AppData\Local\Temp\dsh-plugin-restart-20260922-232944`.
- Used Computer Use to reload the page, fill the visible test-item field with `TM109`, and click `创建单专家训练`.
- Created `training-20260922t153154z-fa40e64f`; UI showed `running / MODEL / 已派发训练专家` and its private artifact directory.
- Clicked the visible run-specific `停止` button. UI changed to `blocked / BLOCKED` with the explicit user-stop reason.
- Expanded `执行与清理记录`: cancellation requested at approximately 15:32:53 UTC; child.result settled at 15:32:53.506; parent disposal completed at .496; child disposal completed at .509.
- Lifecycle evidence shows parent creation .033 s, parent idle .003 s, subagent creation .015 s. Private input preparation and preflight happened before these intervals.

This proves real browser-triggered dispatch and stop/cleanup for this run, not successful semantic generation or complete workflow/publication. The current turn continues with stronger policy fingerprint binding, draft editing and full-pipeline integration. No active release was created.
