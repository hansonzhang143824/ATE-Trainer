@echo off
echo Searching for python.exe ...
echo.

REM Search C: drive for Python (limit depth)
for /d %%d in (C:\*) do (
    if exist "%%d\python.exe" (
        echo FOUND: %%d\python.exe
    )
)

echo.
echo Searching subdirectories of C:\AccoTEST ...
for /r "C:\AccoTEST" %%f in (python.exe) do (
    if exist "%%f" echo FOUND: %%f
)

echo.
echo Checking PATH ...
for %%p in (python.exe py.exe python3.exe) do (
    where %%p 2>nul
)

echo.
echo Done.
pause
