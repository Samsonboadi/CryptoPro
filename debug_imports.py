#!/usr/bin/env python3
"""
Complete Import Diagnosis and Fix Tool
This will help identify and fix all import issues in the CryptoPro project
"""

import os
import sys
import importlib
from pathlib import Path

def check_init_files():
    """Ensure all required __init__.py files exist and have content"""
    init_files = [
        "app/__init__.py",
        "app/core/__init__.py", 
        "app/utils/__init__.py",
        "app/web/__init__.py",
        "app/web/routes/__init__.py",
        "app/api/__init__.py",
        "app/strategies/__init__.py"
    ]
    
    print("🔍 CHECKING __init__.py FILES")
    print("=" * 50)
    
    for init_file in init_files:
        if os.path.exists(init_file):
            size = os.path.getsize(init_file)
            if size > 0:
                print(f"✅ {init_file:<35} OK ({size} bytes)")
            else:
                print(f"⚠️  {init_file:<35} EMPTY - This might cause issues")
        else:
            print(f"❌ {init_file:<35} MISSING")
            
def test_individual_modules():
    """Test importing each module individually"""
    print("\n🧪 TESTING INDIVIDUAL MODULE IMPORTS")
    print("=" * 50)
    
    modules_to_test = [
        "app",
        "app.core",
        "app.core.bot", 
        "app.utils",
        "app.utils.config",
        "app.utils.logger",
        "app.web",
        "app.web.routes",
        "app.web.routes.api_routes",
        "app.web.routes.websocket_routes",
        "app.web.app",
        "app.api",
        "app.api.crypto_com_api",
        "app.strategies",
        "app.strategies.base_strategy",
        "app.strategies.rsi_strategy"
    ]
    
    for module in modules_to_test:
        try:
            importlib.import_module(module)
            print(f"✅ {module:<35} SUCCESS")
        except ImportError as e:
            print(f"❌ {module:<35} FAILED: {e}")
        except Exception as e:
            print(f"⚠️  {module:<35} ERROR: {e}")

def analyze_specific_import_error():
    """Analyze the specific websocket_routes import error"""
    print("\n🎯 ANALYZING WEBSOCKET_ROUTES IMPORT")
    print("=" * 50)
    
    # Check if the file exists
    websocket_file = "app/web/routes/websocket_routes.py"
    if os.path.exists(websocket_file):
        print(f"✅ {websocket_file} exists")
        
        # Try to import it directly
        try:
            import app.web.routes.websocket_routes
            print("✅ Direct import of app.web.routes.websocket_routes works")
        except Exception as e:
            print(f"❌ Direct import failed: {e}")
            
        # Check what's in the file
        try:
            with open(websocket_file, 'r') as f:
                content = f.read()
                lines = len(content.split('\n'))
                print(f"📄 File has {lines} lines")
                
                # Check for syntax errors
                try:
                    compile(content, websocket_file, 'exec')
                    print("✅ File syntax is valid")
                except SyntaxError as e:
                    print(f"❌ Syntax error in file: {e}")
                    
        except Exception as e:
            print(f"❌ Error reading file: {e}")
    else:
        print(f"❌ {websocket_file} does not exist")

def check_app_web_app_imports():
    """Check the specific imports in app/web/app.py"""
    print("\n🔍 ANALYZING app/web/app.py IMPORTS")
    print("=" * 50)
    
    app_file = "app/web/app.py"
    if os.path.exists(app_file):
        try:
            with open(app_file, 'r') as f:
                content = f.read()
                
            # Find import lines
            import_lines = []
            for i, line in enumerate(content.split('\n'), 1):
                line = line.strip()
                if line.startswith('from ') or line.startswith('import '):
                    import_lines.append((i, line))
                    
            print("📋 Import statements found:")
            for line_num, import_stmt in import_lines:
                print(f"   Line {line_num:2d}: {import_stmt}")
                
                # Test each import
                if 'websocket_routes' in import_stmt or 'api_routes' in import_stmt:
                    print(f"   🧪 Testing: {import_stmt}")
                    try:
                        # This is a simplified test - we can't easily exec the import
                        # but we can check if the modules exist
                        if 'from app.web.routes.websocket_routes' in import_stmt:
                            import app.web.routes.websocket_routes
                            print("   ✅ websocket_routes import should work")
                        elif 'from app.web.routes.api_routes' in import_stmt:
                            import app.web.routes.api_routes
                            print("   ✅ api_routes import should work")
                    except Exception as e:
                        print(f"   ❌ Import test failed: {e}")
                        
        except Exception as e:
            print(f"❌ Error analyzing app.py: {e}")
    else:
        print(f"❌ {app_file} does not exist")

def suggest_fixes():
    """Provide specific fix suggestions"""
    print("\n💡 SUGGESTED FIXES")
    print("=" * 50)
    
    fixes = [
        "1. Ensure all __init__.py files exist and are not empty",
        "2. Use absolute imports throughout the project",
        "3. Remove any sys.path modifications", 
        "4. Check for circular imports",
        "5. Verify Python is run from the project root directory",
        "6. Check for syntax errors in route files"
    ]
    
    for fix in fixes:
        print(f"   {fix}")
        
    print("\n🔧 SPECIFIC ACTIONS TO TRY:")
    print("   A. Add content to empty __init__.py files")
    print("   B. Replace relative imports with absolute imports")
    print("   C. Run: python -c 'import app.web.routes.websocket_routes'")
    print("   D. Check if there are any circular import dependencies")

def main():
    """Run the complete diagnostic"""
    print("CryptoPro Complete Import Diagnostic Tool")
    print("=" * 60)
    print(f"Current directory: {os.getcwd()}")
    print(f"Python version: {sys.version}")
    print()
    
    # Run all checks
    check_init_files()
    test_individual_modules() 
    analyze_specific_import_error()
    check_app_web_app_imports()
    suggest_fixes()
    
    print("\n" + "=" * 60)
    print("DIAGNOSTIC COMPLETE")
    print("Run the suggested fixes and test again!")

if __name__ == "__main__":
    main()