@echo off
echo.
echo 🚀 Setting up CryptoBot Pro with pandas_ta on Windows...
echo ===========================================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found. Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)
echo ✅ Python found

REM Create virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)
echo ✅ Virtual environment ready

REM Activate virtual environment
call venv\Scripts\activate.bat
echo ✅ Virtual environment activated

REM Upgrade pip
python -m pip install --upgrade pip

REM Create requirements.txt
echo Creating requirements.txt...
(
echo numpy^>=1.24.0
echo pandas^>=2.0.0
echo requests^>=2.31.0
echo PyYAML^>=6.0.1
echo python-dotenv^>=1.0.0
echo pandas-ta^>=0.3.14b
echo Flask^>=2.3.2
echo Flask-SocketIO^>=5.3.4
echo colorlog^>=6.7.0
echo websocket-client^>=1.6.1
echo scipy^>=1.10.0
echo matplotlib^>=3.7.0
echo psutil^>=5.9.0
) > requirements.txt

REM Install dependencies
echo Installing dependencies...
python -m pip install -r requirements.txt

REM Create directories
mkdir data\logs 2>nul
mkdir config 2>nul

REM Create .env file
if not exist ".env" (
echo Creating .env file...
(
echo CRYPTO_COM_API_KEY=your_api_key_here
echo CRYPTO_COM_SECRET_KEY=your_secret_key_here
echo CRYPTO_COM_SANDBOX=true
echo WEB_PORT=5000
echo WEB_SECRET_KEY=change-this-secret-key
) > .env
)

REM Create start.bat
(
echo @echo off
echo call venv\Scripts\activate.bat
echo python main.py %%*
echo pause
) > start.bat

echo.
echo ✅ Setup complete!
echo.
echo Next steps:
echo 1. Edit .env file with your API keys
echo 2. Copy the updated Python files from the artifacts
echo 3. Run: start.bat
echo.
pause