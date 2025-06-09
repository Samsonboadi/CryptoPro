#!/usr/bin/env python3
"""
Find duplicate route definitions in the Flask application
"""

import os
import re
from pathlib import Path

def find_route_definitions():
    """Find all @app.route definitions in the project"""
    
    files_to_check = [
        "app/web/app.py",
        "app/web/routes/api_routes.py", 
        "app/web/routes/websocket_routes.py"
    ]
    
    print("🔍 SEARCHING FOR ROUTE DEFINITIONS")
    print("=" * 60)
    
    all_routes = {}  # route_path -> [(file, line_num, function_name)]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"\n📄 Checking {file_path}")
            print("-" * 40)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines, 1):
                line = line.strip()
                
                # Look for @app.route decorators
                route_match = re.search(r"@app\.route\(['\"]([^'\"]+)['\"]", line)
                if route_match:
                    route_path = route_match.group(1)
                    
                    # Look for the function definition on the next few lines
                    function_name = "unknown"
                    for j in range(i, min(i + 5, len(lines))):
                        func_line = lines[j].strip()
                        func_match = re.search(r"def\s+(\w+)\s*\(", func_line)
                        if func_match:
                            function_name = func_match.group(1)
                            break
                    
                    print(f"   Line {i:3d}: {route_path} -> {function_name}()")
                    
                    # Store in our tracking dict
                    if route_path not in all_routes:
                        all_routes[route_path] = []
                    all_routes[route_path].append((file_path, i, function_name))
        else:
            print(f"❌ {file_path} not found")
    
    print(f"\n🎯 DUPLICATE ROUTE ANALYSIS")
    print("=" * 60)
    
    duplicates_found = False
    for route_path, definitions in all_routes.items():
        if len(definitions) > 1:
            duplicates_found = True
            print(f"\n❌ DUPLICATE ROUTE: {route_path}")
            for file_path, line_num, func_name in definitions:
                print(f"   {file_path}:{line_num} -> {func_name}()")
    
    if not duplicates_found:
        print("✅ No duplicate routes found!")
    else:
        print(f"\n💡 SOLUTION:")
        print("Remove or rename one of the duplicate route definitions.")
        print("Each route path should only be defined once.")
    
    print(f"\n📊 SUMMARY")
    print("=" * 30)
    print(f"Total unique routes: {len(all_routes)}")
    print(f"Duplicate routes: {sum(1 for defs in all_routes.values() if len(defs) > 1)}")
    
    return all_routes

def suggest_fix():
    """Suggest how to fix the duplicate routes"""
    print(f"\n🔧 SUGGESTED FIXES:")
    print("=" * 30)
    print("1. Remove the health_check route from app/web/app.py")
    print("   (Keep it only in api_routes.py)")
    print("2. Or rename one of the functions to avoid conflicts")
    print("3. Or use different route paths (e.g., /health vs /api/health)")

def main():
    """Main function"""
    print("Flask Route Duplicate Finder")
    print("=" * 60)
    
    routes = find_route_definitions()
    suggest_fix()

if __name__ == "__main__":
    main()