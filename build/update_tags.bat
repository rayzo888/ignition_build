@echo off
setlocal

::set variables
set UPDATE_TAGS_URL=http://liewfam.ignition.local/system/webdev/HomeAutomation/utility/tagControl/updateTags
set TAGFOLDER=/usr/local/bin/ignition/data/tags
set CHECK_GWINFO_URL=http://liewfam.ignition.local/system/gwinfo
set check_status=curl -X GET %CHECK_GWINFO_URL%

echo Waiting for Gateway to report RUNNING...

:check_running
%check_status% -i | findstr /C:"ContextStatus=RUNNING" >nul
if %ERRORLEVEL%==0 (
    echo OK: Gateway is RUNNING.  Continuing...
) else (
    echo waiting Gateway Status to fully Running
    timeout /t 3 >nul
    goto check_running
)

:: HTTPPost
echo Updating tags from tag folder.
curl -X POST ^
  -H "Accept: application/json" ^
  -H "Content-Type: application/json" ^
  -d "{\"tagFileFolder\":\"%TAGFOLDER%\"}" ^
  %UPDATE_TAGS_URL%


echo Script completed successfully.
timeout /t 5 >nul
exit /b 0