@echo off
setlocal enabledelayedexpansion

:: Set Variables
set MOVE_PROJECTS_URL=http://onebiopdv05x373:8088/system/webdev/MAST_Connect/utility/projectControl/moveFiles
set TARGET_PROJECTS_FOLDER="C:\\Users\\sadm-X276512\\Documents\\MAST\\SourceCode\\sandbox\\projects"
set /p USER_INPUT=Enter project name: 

:: HTTPPost
echo Get projects from ignition server
curl -X POST ^
  -H "Accept: application/json" ^
  -H "Content-Type: application/json" ^
  -d "{\"project\":"%USER_INPUT%", \"dstFolder\":\"%TARGET_PROJECTS_FOLDER%\"}" ^
  -s -o nul -w "%%{http_code}" ^
   %MOVE_PROJECTS_URL% > tmp_httpResponse.txt
  set /p STATUS_CODE=<tmp_httpResponse.txt
  del tmp_httpResponse.txt

:: Check for success
if not "%STATUS_CODE%"=="200" (
    echo ERROR: HTTPPost failed. Status code: %STATUS_CODE%
) else (
    echo Success: Status code 200
)

timeout /t 5 >nul
exit /b 0