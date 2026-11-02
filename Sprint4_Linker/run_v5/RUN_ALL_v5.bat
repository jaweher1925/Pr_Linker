@echo off
REM ===================================================================
REM  RUN EVERYTHING for linker_v5 - double-click this file.
REM  Time: about 10-20 min (step 1 skips files already downloaded).
REM ===================================================================
set PATH=%APPDATA%\Python\Python314\Scripts;%PATH%
set EA=C:\Users\GIGABYTE\Desktop\THESIS_Jaweher\00_CODE\evolution-assurance
set RUN=uv run --python 3.13 --project %EA%
cd /d "%~dp0"

echo.
echo === STEP 1/6: download AIDev v5 (skips tables already there) ===
%RUN% python step1_download_v5.py || goto :err

echo.
echo === STEP 2/6: rebuild the task type (title prefix + classifier) ===
%RUN% python step2_task_type_v5.py || goto :err

echo.
echo === STEP 3/6: build the v5 database (merged agent PRs, code files) ===
%RUN% python step3_build_lake_v5.py || goto :err

echo.
echo === STEP 4/6: run linker_v5 (all_changes + fix_only, 30/60 days) ===
%RUN% python step4_run_linker_v5.py || goto :err

echo.
echo === STEP 4b: net diff from GitHub (like the paper) + linker again (first time ~3 h, resumable) ===
%RUN% python step4b_netdiff_v5.py || goto :err

echo.
echo === STEP 5/6: results tables and charts (notebook -> step5_results_v5.html) ===
%RUN% --with nbconvert --with ipykernel --with openpyxl jupyter nbconvert --to html --execute step5_results_v5.ipynb || echo (step 5 failed - open step5_results_v5.ipynb in VS Code and click Run All)

echo.
echo === STEP 6/6: make the 30-PR test sheet (Test_30_PRs.xlsx) ===
%RUN% --with openpyxl python step6_test_30_prs.py || goto :err

echo.
echo ===================================================================
echo  DONE. Open:
echo    step5_results_v5.html  - the result tables and charts
echo    Test_30_PRs.xlsx       - the 30 PRs to check by hand
echo ===================================================================
pause
exit /b 0
:err
echo.
echo ERROR - take a screenshot of this window and check the error message.
pause
