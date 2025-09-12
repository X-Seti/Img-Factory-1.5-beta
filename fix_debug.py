# Quick fix script to resolve debug import issues
# Run this before launching IMG Factory

import sys
import os
from pathlib import Path

def fix_debug_imports():
    """Fix debug import issues by adding proper paths"""
    
    # Get current directory
    current_dir = Path.cwd()
    
    # Add Apps directory to Python path if not already there
    apps_dir = current_dir / "Apps"
    if apps_dir.exists() and str(apps_dir) not in sys.path:
        sys.path.insert(0, str(apps_dir))
        print(f"✅ Added {apps_dir} to Python path")
    
    # Try to create debug module at root level with fallback
    debug_dir = current_dir / "debug"
    if not debug_dir.exists():
        debug_dir.mkdir()
        print(f"✅ Created {debug_dir}")
    
    # Create __init__.py
    init_file = debug_dir / "__init__.py"
    if not init_file.exists():
        init_file.write_text('# Debug package init\n__version__ = "1.0.0"\n')
        print(f"✅ Created {init_file}")
    
    # Create img_debug_functions.py with simple fallback
    debug_functions_file = debug_dir / "img_debug_functions.py"
    if not debug_functions_file.exists():
        debug_functions_content = '''# Simple debug fallback
class ImgDebugger:
    def __init__(self):
        self.enabled = True
    
    def debug(self, message): print(f"[DEBUG] {message}")
    def info(self, message): print(f"[INFO] {message}")
    def warning(self, message): print(f"[WARNING] {message}")
    def error(self, message): print(f"[ERROR] {message}")
    def success(self, message): print(f"[SUCCESS] {message}")

img_debugger = ImgDebugger()

_col_debug_enabled = False

def set_col_debug_enabled(enabled):
    global _col_debug_enabled
    _col_debug_enabled = enabled

def is_col_debug_enabled():
    return _col_debug_enabled

def debug(message): img_debugger.debug(message)
def info(message): img_debugger.info(message)
def warning(message): img_debugger.warning(message)
def error(message): img_debugger.error(message)
def success(message): img_debugger.success(message)

__all__ = ['img_debugger', 'set_col_debug_enabled', 'is_col_debug_enabled', 'debug', 'info', 'warning', 'error', 'success']
'''
        debug_functions_file.write_text(debug_functions_content)
        print(f"✅ Created {debug_functions_file}")
    
    print("✅ Debug import fix complete!")

if __name__ == "__main__":
    fix_debug_imports()
