@echo off
REM Double-click this file (or run it in CMD) to run every step.
set PATH=%APPDATA%\Python\Python314\Scripts;%PATH%
set EA=C:\Users\GIGABYTE\Desktop\THESIS_Jaweher\00_CODE\evolution-assurance
cd /d "%~dp0"
echo === Step 1: download AIDev v3 tables (skips files already there) ===
uv run --project %EA% python step1_download_data.py || goto :err
echo === Step 2: load the tables in the linker database ===
uv run --project %EA% python step2_load_tables.py || goto :err
echo === Step 3: changed files from GitHub (already done: 5,781 PRs - only fetches missing ones) ===
uv run --project %EA% python step3_fetch_changed_files.py || goto :err
echo === Step 4: run the ORIGINAL linker.py ===
uv run --project %EA% python step4_run_linker.py || goto :err
echo.
echo DONE. Now open step5_results.ipynb and click Run All.
pause
exit /b 0
:err
echo ERROR - send a screenshot of this window.
pause
