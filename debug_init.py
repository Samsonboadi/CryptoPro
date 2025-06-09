#!/usr/bin/env python3
"""
Script to check and fix the app/web/__init__.py file
"""

import os

def check_web_init():
    """Check what's in app/web/__init__.py"""
    init_file = "app/web/__init__.py"
    
    print("🔍 CHECKING app/web/__init__.py CONTENT")
    print("=" * 50)
    
    if os.path.exists(init_file):
        with open(init_file, 'r') as f:
            content = f.read()
        
        print("Current content:")
        print("-" * 30)
        print(content)
        print("-" * 30)
        
        # Check for problematic imports
        lines = content.split('\n')
        problematic_lines = []
        
        for i, line in enumerate(lines, 1):
            if 'websocket_routes' in line and 'app.web.websocket_routes' in line:
                problematic_lines.append((i, line))
        
        if problematic_lines:
            print("\n❌ PROBLEMATIC IMPORTS FOUND:")
            for line_num, line in problematic_lines:
                print(f"   Line {line_num}: {line.strip()}")
                
            print("\n🔧 SUGGESTED FIXES:")
            for line_num, line in problematic_lines:
                if 'from app.web.websocket_routes' in line:
                    fixed_line = line.replace('app.web.websocket_routes', 'app.web.routes.websocket_routes')
                    print(f"   Line {line_num}: {fixed_line.strip()}")
                elif 'import app.web.websocket_routes' in line:
                    fixed_line = line.replace('app.web.websocket_routes', 'app.web.routes.websocket_routes')
                    print(f"   Line {line_num}: {fixed_line.strip()}")
        else:
            print("\n✅ No obvious problematic imports found")
            print("The issue might be more subtle...")
            
    else:
        print(f"❌ {init_file} does not exist!")

def generate_fixed_init():
    """Generate a corrected app/web/__init__.py"""
    print("\n🔧 GENERATING FIXED app/web/__init__.py")
    print("=" * 50)
    
    fixed_content = '''"""
Flask Web Interface Package
Provides web dashboard and API endpoints for the trading bot.
"""

from .app import create_app

__all__ = ['create_app']
'''
    
    print("Suggested content for app/web/__init__.py:")
    print("-" * 40)
    print(fixed_content)
    print("-" * 40)
    
    return fixed_content

def main():
    """Main function"""
    check_web_init()
    fixed_content = generate_fixed_init()
    
    print("\n💡 ACTION NEEDED:")
    print("Replace the content of app/web/__init__.py with the suggested content above.")
    print("This should fix the import error.")

if __name__ == "__main__":
    main()