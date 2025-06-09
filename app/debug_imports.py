#!/usr/bin/env python3
"""
Debug script to check what imports are failing
Run this to see exactly which files need content
"""

import os
import sys

def check_file_content(file_path):
    """Check if file exists and has content"""
    if not os.path.exists(file_path):
        return False, "File doesn't exist"
    
    file_size = os.path.getsize(file_path)
    if file_size == 0:
        return False, "File is empty"
    elif file_size < 100:
        return False, f"File too small ({file_size} bytes)"
    else:
        return True, f"OK ({file_size} bytes)"

def test_imports():
    """Test each import step by step"""
    print("Testing imports step by step...\n")
    
    # Test 1: Basic app import
    print("1. Testing: from app import ...")
    try:
        from app import __init__
        print("   ✅ app package imports OK")
    except Exception as e:
        print(f"   ❌ app package import failed: {e}")
        return False
    
    # Test 2: Core modules
    print("\n2. Testing: from app.core import ...")
    try:
        from app.core import bot
        print("   ✅ app.core.bot imports OK")
    except Exception as e:
        print(f"   ❌ app.core.bot import failed: {e}")
        print("   📝 Check: app/core/bot.py needs content")
    
    # Test 3: Utils modules
    print("\n3. Testing: from app.utils import ...")
    try:
        from app.utils import config
        print("   ✅ app.utils.config imports OK")
    except Exception as e:
        print(f"   ❌ app.utils.config import failed: {e}")
        print("   📝 Check: app/utils/config.py needs content")
    
    try:
        from app.utils import logger
        print("   ✅ app.utils.logger imports OK")
    except Exception as e:
        print(f"   ❌ app.utils.logger import failed: {e}")
        print("   📝 Check: app/utils/logger.py needs content")
    
    # Test 4: Web modules
    print("\n4. Testing: from app.web import ...")
    try:
        from app.web import app as web_app
        print("   ✅ app.web.app imports OK")
    except Exception as e:
        print(f"   ❌ app.web.app import failed: {e}")
        print("   📝 Check: app/web/app.py needs content")
    
    # Test 5: Web routes
    print("\n5. Testing: from app.web.routes import ...")
    try:
        from app.web.routes import api_routes
        print("   ✅ app.web.routes.api_routes imports OK")
    except Exception as e:
        print(f"   ❌ app.web.routes.api_routes import failed: {e}")
        print("   📝 Check: app/web/routes/api_routes.py needs content")
    
    try:
        from app.web.routes import websocket_routes
        print("   ✅ app.web.routes.websocket_routes imports OK")
    except Exception as e:
        print(f"   ❌ app.web.routes.websocket_routes import failed: {e}")
        print("   📝 Check: app/web/routes/websocket_routes.py needs content")

def check_file_sizes():
    """Check file sizes to see which need content"""
    print("\n" + "="*50)
    print("CHECKING FILE SIZES")
    print("="*50)
    
    important_files = [
        "main.py",
        "app/__init__.py",
        "app/core/__init__.py", 
        "app/core/bot.py",
        "app/utils/__init__.py",
        "app/utils/config.py",
        "app/utils/logger.py",
        "app/utils/technical_indicators.py",
        "app/web/__init__.py",
        "app/web/app.py",
        "app/web/routes/__init__.py",
        "app/web/routes/api_routes.py",
        "app/web/routes/websocket_routes.py",
        "app/api/__init__.py",
        "app/api/crypto_com_api.py",
        "app/strategies/__init__.py",
        "app/strategies/base_strategy.py",
        "app/strategies/rsi_strategy.py"
    ]
    
    files_need_content = []
    
    for file_path in important_files:
        has_content, status = check_file_content(file_path)
        status_icon = "✅" if has_content else "❌"
        print(f"{status_icon} {file_path:<40} {status}")
        
        if not has_content:
            files_need_content.append(file_path)
    
    if files_need_content:
        print(f"\n⚠️  {len(files_need_content)} files need content:")
        for file_path in files_need_content:
            print(f"   📝 {file_path}")
    else:
        print("\n🎉 All files have content!")

def main():
    """Main debug function"""
    print("CryptoBot Pro Import Debug Tool")
    print("="*50)
    
    # Check file sizes first
    check_file_sizes()
    
    # Test imports
    test_imports()
    
    print("\n" + "="*50)
    print("DIAGNOSIS COMPLETE")
    print("="*50)
    
    # Check the specific error
    print("\nTesting the exact import that's failing:")
    try:
        from app.web.app import create_app
        print("✅ from app.web.app import create_app - SUCCESS!")
    except Exception as e:
        print(f"❌ from app.web.app import create_app - FAILED: {e}")
        
        # Try to import step by step
        print("\nTrying step by step...")
        try:
            import app
            print("   ✅ import app")
        except Exception as e2:
            print(f"   ❌ import app: {e2}")
            return
        
        try:
            import app.web
            print("   ✅ import app.web")
        except Exception as e2:
            print(f"   ❌ import app.web: {e2}")
            return
            
        try:
            import app.web.app
            print("   ✅ import app.web.app")
        except Exception as e2:
            print(f"   ❌ import app.web.app: {e2}")
            return
    
    print("\n📋 NEXT STEPS:")
    print("1. Copy artifact content to any empty files shown above")
    print("2. Make sure all __init__.py files have proper imports")
    print("3. Run this script again to verify")
    print("4. Then try: python main.py --debug")

if __name__ == "__main__":
    main()