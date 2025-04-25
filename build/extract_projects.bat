@echo off
setlocal enabledelayedexpansion

:: Set Variables
set HOSTNAME_IP=liewfam.ignition.local
set PORT=
set SCRIPT_SOURCE=HomeAutomation
set MOVE_PROJECTS_URL=http://%HOSTNAME_IP%:%PORT%/system/webdev/%SCRIPT_SOURCE%/utility/projectControl/moveFiles
set TARGET_PROJECTS_FOLDER="C:\\Users\\rayzo\\Documents\\Source%%20Code\\001_Ignition%%20Build\\ignition_build\\projects"
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