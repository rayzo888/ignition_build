@echo off
setlocal EnableDelayedExpansion

REM Prompt for tag provider
set /p TAG_PROVIDER=Enter Tag Provider (e.g., default): 

REM Define and encode tag path
set ENCODED_TAG_FOLDER=C:\\Users\\rayzo\\Documents\\Source%%20Code\\001_Ignition%%20Build\\ignition_build\\tags

REM Construct the URL safely
set "URL=http://centralhub.local:8088/system/webdev/HomeAutomation/utility/tagControl/exportTags?tagFileFolder=%ENCODED_TAG_FOLDER%&tagProvider=%TAG_PROVIDER%"

REM Output file and temp file
set "TMP_STATUS_FILE=tmp_statuscode.txt"

REM Perform curl request with safe variable expansion
echo Sending request to: !URL!
curl -s  -w "%%{http_code}" "!URL!" > "!TMP_STATUS_FILE!"

REM Read status code
set /p STATUS_CODE=<"!TMP_STATUS_FILE!"
del "!TMP_STATUS_FILE!"

echo HTTP Status Code: !STATUS_CODE!

:: Check for success
if not "%STATUS_CODE%"=="200" (
    echo ❌ Request failed with status code !STATUS_CODE!.
) else (
    echo ✅ Request successful. Output saved to !ENCODED_TAG_FOLDER!.
)

endlocal
pause
