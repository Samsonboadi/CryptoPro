@echo off
setlocal enabledelayedexpansion

echo.
echo 🚀 Starting CryptoBot Pro...
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo ❌ Virtual environment not found. Please run setup.bat first.
    echo.
    echo To setup CryptoBot Pro:
    echo 1. Run: setup.bat
    echo 2. Configure .env file with your API keys
    echo 3. Run: start.bat
    echo.
    pause
    exit /b 1
)

REM Check if main.py exists
if not exist "main.py" (
    echo ❌ main.py not found. Are you in the correct directory?
    echo Please make sure you're in the CryptoBot Pro root directory.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ❌ Failed to activate virtual environment
    pause
    exit /b 1
)

REM Load environment variables from .env file
if exist ".env" (
    echo Loading environment variables from .env...
    for /f "usebackq tokens=1,2 delims==" %%a in (".env") do (
        if not "%%a"=="" if not "%%a:~0,1"=="#" set %%a=%%b
    )
    echo ✅ Environment variables loaded
) else (
    echo ⚠️ .env file not found. Using default settings.
    echo You may want to create a .env file with your API credentials.
)

REM Check if config directory exists
if not exist "config" (
    echo Creating config directory...
    mkdir config
)

REM Check if data/logs directory exists  
if not exist "data\logs" (
    echo Creating logs directory...
    mkdir data\logs
)

REM Parse command line arguments
set "ARGS="
set "DEBUG_MODE=false"
set "NO_WEB=false"
set "CONFIG_FILE="

:parse_args
if "%~1"=="" goto start_app
if "%~1"=="--debug" (
    set "DEBUG_MODE=true"
    set "ARGS=%ARGS% --debug"
) else if "%~1"=="-d" (
    set "DEBUG_MODE=true"
    set "ARGS=%ARGS% --debug"
) else if "%~1"=="--no-web" (
    set "NO_WEB=true"
    set "ARGS=%ARGS% --no-web"
) else if "%~1"=="--config" (
    set "CONFIG_FILE=%~2"
    set "ARGS=%ARGS% --config %~2"
    shift
) else if "%~1"=="-c" (
    set "CONFIG_FILE=%~2"
    set "ARGS=%ARGS% --config %~2"
    shift
) else if "%~1"=="--port" (
    set "WEB_PORT=%~2"
    set "ARGS=%ARGS% --port %~2"
    shift
) else if "%~1"=="-p" (
    set "WEB_PORT=%~2"
    set "ARGS=%ARGS% --port %~2"
    shift
) else if "%~1"=="--host" (
    set "WEB_HOST=%~2"
    set "ARGS=%ARGS% --host %~2"
    shift
) else (
    set "ARGS=%ARGS% %~1"
)
shift
goto parse_args

:start_app
REM Display startup information
echo.
echo ======================================
echo   CryptoBot Pro Starting...
echo ======================================
echo.
if "%DEBUG_MODE%"=="true" echo 🐛 Debug mode: ENABLED
if "%NO_WEB%"=="true" (
    echo 🖥️ Web interface: DISABLED
) else (
    echo 🌐 Web interface: http://localhost:%WEB_PORT%
)
if not "%CONFIG_FILE%"=="" echo 📁 Config file: %CONFIG_FILE%
echo.

REM Check if pandas_ta is installed
echo Checking pandas_ta installation...
python -c "import pandas_ta; print('✅ pandas_ta ready')" 2>nul
if %errorlevel% neq 0 (
    echo ⚠️ pandas_ta not found. Installing...
    python -m pip install pandas-ta>=0.3.14b
    if %errorlevel% neq 0 (
        echo ❌ Failed to install pandas_ta
        echo Please run: pip install pandas-ta
        pause
        exit /b 1
    )
)

REM Start the application
echo ✅ Starting CryptoBot Pro with pandas_ta...
echo.

python main.py %ARGS%

REM Check exit code
if %errorlevel% neq 0 (
    echo.
    echo ❌ CryptoBot Pro stopped with an error (Exit Code: %errorlevel%)
    echo.
    echo Common solutions:
    echo 1. Check your .env file configuration
    echo 2. Verify API credentials are correct
    echo 3. Check logs in data/logs/ directory
    echo 4. Run: test.bat to verify installation
    echo.
    echo For help, check the README.md file or logs.
    echo.
) else (
    echo.
    echo ✅ CryptoBot Pro stopped normally
    echo.
)

pause