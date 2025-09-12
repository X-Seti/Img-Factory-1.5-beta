#this belongs in Apps/Debug/import_patcher.py - Version: 1
# X-Seti - September12 2025 - IMG Factory 1.5 - Debug Import Patcher

"""
Debug Import Patcher - Makes Apps/Debug accessible as 'debug' module
Patches Python's import system to redirect debug imports to Apps/Debug
Call setup_debug_imports() early in your application startup
"""

import sys
import os
from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec
from importlib.machinery import ModuleSpec

##Methods list -
# setup_debug_imports
# create_debug_module_redirect
# patch_debug_imports
# _create_debug_finder

class DebugImportFinder: #vers 1
    """Custom import finder to redirect debug module imports"""
    
    def __init__(self, apps_debug_path):
        self.apps_debug_path = apps_debug_path
    
    def find_spec(self, fullname, path, target=None): #vers 1
        """Find module spec for debug imports"""
        if fullname == 'debug':
            # Redirect 'debug' import to Apps/Debug
            init_file = self.apps_debug_path / '__init__.py'
            if init_file.exists():
                spec = spec_from_file_location('debug', init_file)
                return spec
        
        elif fullname == 'debug.img_debug_functions':
            # Redirect 'debug.img_debug_functions' import to Apps/Debug/img_debug_functions.py
            functions_file = self.apps_debug_path / 'img_debug_functions.py'
            if functions_file.exists():
                spec = spec_from_file_location('debug.img_debug_functions', functions_file)
                return spec
        
        return None

def setup_debug_imports(apps_dir_path=None): #vers 1
    """Setup debug import redirection from Apps/Debug"""
    try:
        # Determine Apps directory path
        if apps_dir_path is None:
            # Try to find Apps directory
            current_dir = Path.cwd()
            
            # Check common locations
            possible_paths = [
                current_dir / 'Apps',
                current_dir.parent / 'Apps',
                Path(__file__).parent.parent,  # Apps/ (since we're in Apps/Debug/)
            ]
            
            apps_dir = None
            for path in possible_paths:
                if path.exists() and path.is_dir():
                    apps_dir = path
                    break
            
            if not apps_dir:
                print("[WARNING] Could not find Apps directory for debug imports")
                return False
        else:
            apps_dir = Path(apps_dir_path)
        
        # Check if Apps/Debug exists
        debug_dir = apps_dir / 'Debug'
        if not debug_dir.exists():
            print(f"[WARNING] Debug directory not found: {debug_dir}")
            return False
        
        # Add Apps directory to Python path if not already there
        apps_str = str(apps_dir)
        if apps_str not in sys.path:
            sys.path.insert(0, apps_str)
            print(f"[DEBUG] Added {apps_str} to Python path")
        
        # Install custom import finder
        finder = DebugImportFinder(debug_dir)
        if finder not in sys.meta_path:
            sys.meta_path.insert(0, finder)
            print(f"[DEBUG] Installed debug import finder for {debug_dir}")
        
        # Test the import
        try:
            from debug.img_debug_functions import img_debugger
            img_debugger.info("Debug import system successfully configured")
            return True
        except ImportError as e:
            print(f"[ERROR] Debug import test failed: {e}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Failed to setup debug imports: {e}")
        return False

def create_debug_module_redirect(): #vers 1
    """Alternative approach: Create debug module that redirects to Apps/Debug"""
    try:
        # Find Apps/Debug directory
        current_dir = Path.cwd()
        debug_dir = None
        
        # Check possible locations
        possible_paths = [
            current_dir / 'Apps' / 'Debug',
            current_dir.parent / 'Apps' / 'Debug',
            Path(__file__).parent,  # We're in Apps/Debug/
        ]
        
        for path in possible_paths:
            if path.exists() and (path / 'img_debug_functions.py').exists():
                debug_dir = path
                break
        
        if not debug_dir:
            print("[ERROR] Could not find Apps/Debug directory")
            return False
        
        # Import the actual debug module
        spec = spec_from_file_location('apps_debug', debug_dir / '__init__.py')
        if spec and spec.loader:
            apps_debug_module = module_from_spec(spec)
            spec.loader.exec_module(apps_debug_module)
            
            # Create debug module in sys.modules
            sys.modules['debug'] = apps_debug_module
            
            # Also create the img_debug_functions submodule
            img_spec = spec_from_file_location('debug.img_debug_functions', 
                                             debug_dir / 'img_debug_functions.py')
            if img_spec and img_spec.loader:
                img_module = module_from_spec(img_spec)
                img_spec.loader.exec_module(img_module)
                sys.modules['debug.img_debug_functions'] = img_module
                
                print("[DEBUG] Successfully created debug module redirects")
                return True
        
        return False
        
    except Exception as e:
        print(f"[ERROR] Failed to create debug module redirect: {e}")
        return False

def patch_debug_imports(): #vers 1
    """Patch debug imports - call this early in application startup"""
    print("[DEBUG] Patching debug imports...")
    
    # Try the finder approach first
    if setup_debug_imports():
        print("[DEBUG] Debug import finder approach successful")
        return True
    
    # Fallback to module redirect approach
    if create_debug_module_redirect():
        print("[DEBUG] Debug module redirect approach successful")
        return True
    
    print("[WARNING] All debug import patching approaches failed")
    return False

# Auto-patch when this module is imported
if __name__ != "__main__":
    # Only auto-patch if not being run directly
    patch_debug_imports()

# Export main functions
__all__ = [
    'setup_debug_imports',
    'create_debug_module_redirect', 
    'patch_debug_imports'
]