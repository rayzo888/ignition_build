@echo off
setlocal enabledelayedexpansion

:: Set Variables
set HOSTNAME_IP=ignition.local
set PORT=
set SCRIPT_SOURCE=HomeAutomation
set EXPORT_TAGS_URL=http://%HOSTNAME_IP%/system/webdev/%SCRIPT_SOURCE%/utility/tagControl/exportTags
set SRC_TAGFOLDER=/usr/local/bin/ignition/data/tags

:: Prompt user for input (string value)
set /p USER_INPUT=Enter tag provider name: 
set FULL_URL="%EXPORT_TAGS_URL%?tagFileFolder=%SRC_TAGFOLDER%&tagProvider=%USER_INPUT%"

:: HTTPGet
echo Extracting tags from ignition server.
curl -X GET -s -o nul -w "%%{http_code}" %FULL_URL% > tmp_httpResponse.txt
set /p STATUS_CODE=<tmp_httpResponse.txt
del tmp_httpResponse.txt

:: Check for success
if not "%STATUS_CODE%"=="200" (
    echo ERROR: Request failed. Status code: %STATUS_CODE%
) else (
    echo Success: Status code 200
)

timeout /t 5 >nul
exit /b 0