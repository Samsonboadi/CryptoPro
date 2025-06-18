@echo off
setlocal

echo.
echo 🧪 Testing CryptoBot Pro Installation...
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo ❌ Virtual environment not found. Please run setup.bat first.
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

REM Test Python version
echo [TEST] Python Version:
python --version
echo.

REM Test pip
echo [TEST] Pip Version:
python -m pip --version
echo.

REM Test core dependencies
echo [TEST] Testing Core Dependencies:
echo ================================

REM Test NumPy
python -c "import numpy; print('✅ NumPy:', numpy.__version__)" 2>nul
if %errorlevel% neq 0 echo ❌ NumPy - FAILED

REM Test Pandas
python -c "import pandas; print('✅ Pandas:', pandas.__version__)" 2>nul
if %errorlevel% neq 0 echo ❌ Pandas - FAILED

REM Test pandas_ta (most important)
python -c "import pandas_ta; print('✅ pandas_ta:', pandas_ta.version)" 2>nul
if %errorlevel% neq 0 (
    echo ❌ pandas_ta - FAILED
    echo.
    echo Trying to install pandas_ta...
    python -m pip install pandas-ta
    python -c "import pandas_ta; print('✅ pandas_ta:', pandas_ta.version)" 2>nul
    if %errorlevel% neq 0 echo ❌ pandas_ta installation failed
)

REM Test Requests
python -c "import requests; print('✅ Requests:', requests.__version__)" 2>nul
if %errorlevel% neq 0 echo ❌ Requests - FAILED

REM Test PyYAML
python -c "import yaml; print('✅ PyYAML: OK')" 2>nul
if %errorlevel% neq 0 echo ❌ PyYAML - FAILED

REM Test Flask
python -c "import flask; print('✅ Flask:', flask.__version__)" 2>nul
if %errorlevel% neq 0 echo ❌ Flask - FAILED

REM Test Flask-SocketIO
python -c "import flask_socketio; print('✅ Flask-SocketIO: OK')" 2>nul
if %errorlevel% neq 0 echo ❌ Flask-SocketIO - FAILED

REM Test WebSocket
python -c "import websocket; print('✅ WebSocket Client: OK')" 2>nul
if %errorlevel% neq 0 echo ❌ WebSocket Client - FAILED

REM Test SciPy
python -c "import scipy; print('✅ SciPy:', scipy.__version__)" 2>nul
if %errorlevel% neq 0 echo ❌ SciPy - FAILED

REM Test Matplotlib
python -c "import matplotlib; print('✅ Matplotlib:', matplotlib.__version__)" 2>nul
if %errorlevel% neq 0 echo ❌ Matplotlib - FAILED

echo.
echo [TEST] Testing Technical Indicators:
echo ===================================

REM Test technical indicators functionality
python -c "
import pandas_ta as ta
import pandas as pd
import numpy as np

# Create sample data
dates = pd.date_range('2023-01-01', periods=100, freq='H')
prices = pd.Series(np.random.randn(100).cumsum() + 100, index=dates)

try:
    # Test RSI
    rsi = ta.rsi(prices, length=14)
    print('✅ RSI calculation: OK')
    
    # Test SMA  
    sma = ta.sma(prices, length=20)
    print('✅ SMA calculation: OK')
    
    # Test EMA
    ema = ta.ema(prices, length=20)  
    print('✅ EMA calculation: OK')
    
    # Test MACD
    macd = ta.macd(prices)
    print('✅ MACD calculation: OK')
    
    print('✅ All technical indicators working!')
    
except Exception as e:
    print(f'❌ Technical indicators failed: {e}')
" 2>nul

if %errorlevel% neq 0 (
    echo ❌ Technical indicators test failed
    echo.
    echo Trying manual test...
    python -c "
try:
    import pandas_ta as ta
    import numpy as np
    
    # Simple test
    data = np.random.random(50) * 100
    rsi_result = ta.rsi(data, length=14)
    print('✅ Basic pandas_ta test passed')
except Exception as e:
    print(f'❌ Basic pandas_ta test failed: {e}')
"
)

echo.
echo [TEST] Testing File Structure:
echo =============================

if exist "main.py" (
    echo ✅ main.py found
) else (
    echo ❌ main.py not found
)

if exist "requirements.txt" (
    echo ✅ requirements.txt found
) else (
    echo ❌ requirements.txt not found
)

if exist ".env" (
    echo ✅ .env file found
) else (
    echo ⚠️ .env file not found - you'll need to create one
)

if exist "app" (
    echo ✅ app directory found
) else (
    echo ❌ app directory not found
)

if exist "config" (
    echo ✅ config directory found
) else (
    echo ⚠️ config directory not found - will be created automatically
)

echo.
echo [TEST] Testing Bot Import:
echo =========================

python -c "
try:
    # Test if we can import the main components
    from app.utils.config import Config
    print('✅ Config import: OK')
    
    from app.strategies.rsi_strategy import RSIStrategy
    print('✅ RSI Strategy import: OK')
    
    from app.utils.technical_indicators import TechnicalIndicators
    print('✅ Technical Indicators import: OK')
    
    from app.core.bot import TradingBot
    print('✅ Trading Bot import: OK')
    
    print('✅ All core components can be imported!')
    
except ImportError as e:
    print(f'❌ Import failed: {e}')
    print('Some files may be missing. Please copy all updated files.')
except Exception as e:
    print(f'❌ Unexpected error: {e}')
" 2>nul

if %errorlevel% neq 0 (
    echo ❌ Bot import test failed
    echo ⚠️ You may need to copy the updated Python files from the artifacts
)

echo.
echo =========================================
echo 📊 Test Summary
echo =========================================
echo.

REM Final recommendations
echo 🎯 Recommendations:
echo.
if not exist ".env" (
    echo 1. Create .env file with your API credentials
)
echo 2. Copy all updated Python files from the artifacts
echo 3. Configure your Crypto.com API keys  
echo 4. Run: start.bat to launch the application
echo.

echo ✅ Testing completed!
echo.
echo If all tests passed, you can start CryptoBot Pro with:
echo   start.bat
echo.
pause