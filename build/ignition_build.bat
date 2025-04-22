@echo off
setlocal enabledelayedexpansion

:: Set Variables
set PARAM_FILE=.param

if not exist "%PARAM_FILE%" (
    echo .parameter file not found!
    exit /b 1
)

for /f "usebackq tokens=1,* delims==" %%A in ("%PARAM_FILE%") do (
    set "key=%%A"
    set "value=%%B"
    set "!key!=!value!"
)

set DEST_PROJECTS=%DEST_ROOT%\projects
set DEST_DB=%DEST_ROOT%\db
set DEST_IGNCONF_FOLDER=%DEST_ROOT%
set DEST_IGNCONF_FILE=%DEST_ROOT%\ignition.conf
set SRC_TAGFOLDER=%SRC_ROOT%\tags
set SRC_PROJECTS=%SRC_ROOT%\projects
set SRC_DB=%SRC_ROOT%\db
set SRC_IGNCONF_FOLDER=%SRC_ROOT%\config
set SRC_IGNCONF_FILE=ignition.conf
set GWCMD=%IGNROOT%\gwcmd.bat
set GWCMD_STOP=%IGNROOT%\stop-ignition.bat
set GWCMD_START=%IGNROOT%\start-ignition.bat


:: Change to your git repository directory
cd /d "%SRC_ROOT%"

echo git pull from remote repository
:: Perform git pull and get a clean state that is up-to-date with main branch.
git pull
git reset --hard

:: Check if git function was successful
if %ERRORLEVEL% NEQ 0 (
    echo Git pull failed. Exiting script.
    exit /b %ERRORLEVEL%
)

:: Make sure Ignition stopped before continue
echo Checking Ignition Gateway status...

%GWCMD% -i | findstr /I "RUNNING" >nul
if %errorlevel%==0 (
    echo Gateway is running. Attempting to stop...
    call %GWCMD_STOP%
    echo Waiting for Gateway to stop...
)

:: Step 1: Delete destination folders
echo Deleting destination folders...
rd /S /Q "%DEST_PROJECTS%"
rd /S /Q "%DEST_DB%"
del /F /Q "%DEST_IGNCONF_FILE%"

:: Step 2: Wait until both folders are gone
:check_deleted
if exist "%DEST_PROJECTS%" (
    echo Projects folder still exists, retrying deletion...
    rd /S /Q "%DEST_PROJECTS%"
    timeout /t 2 >nul
    goto check_deleted
)
if exist "%DEST_DB%" (
    echo DB folder still exists, retrying deletion...
    rd /S /Q "%DEST_DB%"
    timeout /t 2 >nul
    goto check_deleted
)

if exist "%DEST_IGNCONF_FILE%" (
    echo ignition.conf still exists, retrying deletion...
    del /F /Q "%DEST_IGNCONF_FILE%"
    timeout /t 2 >nul
    goto check_deleted
)

echo Both folders deleted, proceeding with file copy.

:: Step 3: Re-create destination folders
mkdir "%DEST_PROJECTS%"
mkdir "%DEST_DB%"

:: Step 4: Copy files using robocopy
echo Copying Projects folder...
robocopy "%SRC_PROJECTS%" "%DEST_PROJECTS%" /E /COPYALL /R:3 /W:5

if %ERRORLEVEL% GEQ 8 (
    echo Robocopy failed for projects. Exiting script.
    exit /b %ERRORLEVEL%
)

echo Copying DB folder...
robocopy "%SRC_DB%" "%DEST_DB%" /E /COPYALL /R:3 /W:5

if %ERRORLEVEL% GEQ 8 (
    echo Robocopy failed for db. Exiting script.
    exit /b %ERRORLEVEL%
)

echo Copying ignition.conf file...
robocopy "%SRC_IGNCONF_FOLDER%" "%DEST_IGNCONF_FOLDER%" %SRC_IGNCONF_FILE%

if %ERRORLEVEL% GEQ 8 (
    echo Robocopy failed for ignition.conf. Exiting script.
    exit /b %ERRORLEVEL%
)

:: Restart Ignition Gateway.
echo Attempting to start Ignition Gateway...
call %GWCMD_START%

echo Waiting for Gateway to report RUNNING...
:check_running
%GWCMD% -i | findstr /C:"Gateway Status: RUNNING" >nul
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

:: Build Gateway Backup
echo Bulding Ignition Gateway Backup File.
%GWCMD% -b %DEST_IGNBUILD_FILE% -y

:: Check if download gateway backup was successful
if %ERRORLEVEL% NEQ 0 (
    echo Gateway backup download failed. Exiting script.
    exit /b %ERRORLEVEL%
)

echo Script completed successfully.
timeout /t 5 >nul
exit /b 0
