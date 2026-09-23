@echo off
set PYTHON=D:\SOFTWARE_INSTALL\python.exe
cd /d "D:\Newtest\CLAUDE_PROCESS"
%PYTHON% replay_actions.py recorded.json 1.0
pause
