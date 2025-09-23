#this belongs in application/Tools/IMG_Factory/core/__init__.py - Version: 2
# X-Seti - September23 2025 - IMG Factory 1.5 - Core Tools Package Init

"""
IMG Factory Core Tools Package Initialization - Actual file structure paths
"""

import sys
from pathlib import Path

# Try to import existing core files
try:
    from .IMG_Operations import IMGArchive, IMGEntry, IMGVersion
    from .File_Operations import FileOperations  
    from .Entries_and_Selection import EntriesAndSelection
    from .Core import *
    IMG_OPERATIONS_AVAILABLE = True
except ImportError as e:
    print(f"[INIT] Core operations import failed: {e}")
    IMG_OPERATIONS_AVAILABLE = False
    
    # Create fallback classes
    class IMGArchive:
        def __init__(self):
            pass
    
    class IMGEntry:
        def __init__(self):
            pass
            
    class IMGVersion:
        pass
        
    class FileOperations:
        def __init__(self):
            pass
            
    class EntriesAndSelection:
        def __init__(self):
            pass

# Import the bridge import_export
try:
    from .import_export import import_export, get_debug_logger, LogCategory
    BRIDGE_AVAILABLE = True
except ImportError as e:
    print(f"[INIT] Import/Export bridge not available: {e}")
    BRIDGE_AVAILABLE = False
    
    class import_export:
        pass
    
    def get_debug_logger():
        class SimpleLogger:
            def debug(self, *args): pass
            def info(self, *args): pass
            def error(self, *args): pass
            def warning(self, *args): pass
        return SimpleLogger()
    
    class LogCategory:
        FILE_IO = "FILE_IO"
        TOOL = "TOOL"
        SYSTEM = "SYSTEM"

# The missing 'cd' function that's causing the error
def cd(path):
    """Change directory function - missing from original error"""
    try:
        import os
        os.chdir(path)
        return True
    except Exception as e:
        print(f"[ERROR] cd failed: {e}")
        return False

# Export all available functions  
__all__ = [
    'IMGArchive', 'IMGEntry', 'IMGVersion', 
    'FileOperations', 'EntriesAndSelection',
    'import_export', 'get_debug_logger', 'LogCategory',
    'cd'
]

print(f"[INIT] application.Tools.IMG_Factory.core package initialized")
print(f"   IMG Operations: {'✅' if IMG_OPERATIONS_AVAILABLE else '❌'}")  
print(f"   Bridge: {'✅' if BRIDGE_AVAILABLE else '❌'}")
print(f"   cd function: ✅")