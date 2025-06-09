#!/usr/bin/env python3
"""
Debug the create_app function to see why it's returning None
"""

import os
import sys

def test_create_app():
    """Test the create_app function step by step"""
    
    print("🔍 DEBUGGING create_app FUNCTION")
    print("=" * 50)
    
    try:
        # Import required modules
        print("1️⃣ Importing modules...")
        from app.utils.config import Config
        from app.core.bot import TradingBot
        from app.web.app import create_app
        print("   ✅ All modules imported successfully")
        
        # Load config
        print("\n2️⃣ Loading configuration...")
        config = Config('config/config.yaml')
        print("   ✅ Configuration loaded")
        
        # Create bot
        print("\n3️⃣ Creating bot instance...")
        bot = TradingBot(config)
        print("   ✅ Bot created")
        
        # Test create_app
        print("\n4️⃣ Testing create_app function...")
        app = create_app(config, bot)
        
        print(f"   📊 create_app returned: {type(app)}")
        print(f"   📊 Value: {app}")
        
        if app is None:
            print("   ❌ create_app returned None!")
            print("   🔍 This means there's an error in the create_app function")
        else:
            print("   ✅ create_app returned a valid Flask app")
            print(f"   📊 App name: {app.name}")
            print(f"   📊 App config keys: {list(app.config.keys())[:5]}...")
            
    except Exception as e:
        print(f"   ❌ Error during testing: {e}")
        import traceback
        print(f"   📋 Full traceback:")
        traceback.print_exc()

def check_create_app_source():
    """Check the create_app function source code"""
    
    print("\n🔍 CHECKING create_app FUNCTION SOURCE")
    print("=" * 50)
    
    app_file = "app/web/app.py"
    if os.path.exists(app_file):
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the create_app function
        lines = content.split('\n')
        in_create_app = False
        create_app_lines = []
        indent_level = 0
        
        for i, line in enumerate(lines, 1):
            if 'def create_app(' in line:
                in_create_app = True
                indent_level = len(line) - len(line.lstrip())
                create_app_lines.append(f"{i:3d}: {line}")
            elif in_create_app:
                current_indent = len(line) - len(line.lstrip()) if line.strip() else indent_level + 1
                
                if line.strip() and current_indent <= indent_level:
                    # We've left the function
                    break
                    
                create_app_lines.append(f"{i:3d}: {line}")
        
        if create_app_lines:
            print("📋 create_app function:")
            for line in create_app_lines[-20:]:  # Show last 20 lines
                if 'return' in line:
                    print(f"🎯 {line}")  # Highlight return statements
                else:
                    print(f"   {line}")
        else:
            print("❌ create_app function not found")
    else:
        print(f"❌ {app_file} not found")

def main():
    """Main function"""
    test_create_app()
    check_create_app_source()
    
    print(f"\n💡 LIKELY ISSUES:")
    print("=" * 30)
    print("1. create_app function has an exception and returns None")
    print("2. Missing 'return app' statement at the end of create_app")
    print("3. Early return with None due to an error condition")

if __name__ == "__main__":
    main()