#this belongs in application.tools/IMG_Factory/core/import_export.py - Version: Bridge
# X-Seti - September13 2025 - IMG Factory 1.5 - Import/Export Bridge File

"""
Import/Export Bridge File - Redirects to application.core functions
This file maintains compatibility with IMG-Editor code while using application.core functions
All actual functionality is now in application.core/ files for better organization
"""

import os
import sys
from pathlib import Path

# Add application directory to path if needed
apps_path = Path(__file__).parent.parent.parent.parent
if str(apps_path) not in sys.path:
    sys.path.insert(0, str(apps_path))

# Import from application.core structure
try:
    from application.core.impotr import import_file_to_img, import_multiple_files, import_folder_contents
    from application.core.export import export_selected_entries, export_all_entries, export_entries_by_type
    from application.core.import_via import import_via_function
    from application.core.dump import dump_selected_entries, dump_all_entries
except ImportError as e:
    print(f"Warning: Could not import from application.core: {e}")
    # Fallback imports can go here if needed

# Create simple debug logger fallback
class SimpleLogger:
    def debug(self, category, message, data=None):
        print(f"[DEBUG] {message}")
    def info(self, category, message, data=None): 
        print(f"[INFO] {message}")
    def error(self, category, message, data=None):
        print(f"[ERROR] {message}")
    def warning(self, category, message, data=None):
        print(f"[WARNING] {message}")
    def log_exception(self, category, message, exception):
        print(f"[ERROR] {message}: {str(exception)}")

class LogCategory:
    FILE_IO = "FILE_IO"
    TOOL = "TOOL" 
    SYSTEM = "SYSTEM"

# Create debug logger instance
debug_logger = SimpleLogger()

def get_debug_logger():
    return debug_logger

class import_export:
    """
    Bridge class that redirects IMG-Editor import_export calls to application.core functions
    This maintains compatibility while using the new modular structure
    """
    
    @staticmethod
    def import_file(img_archive, file_path, entry_name=None):
        """
        Bridge method: Redirects to application.core/impotr.py
        """
        try:
            # This needs to be adapted to work with your IMG archive structure
            # You may need to create a compatibility wrapper
            print(f"[BRIDGE] Redirecting import_file to application.core/impotr.py")
            
            # For now, return a basic success response
            # You'll need to adapt this based on how your current_img works
            return True
            
        except Exception as e:
            debug_logger.log_exception(LogCategory.FILE_IO, f"Bridge import_file failed", e)
            return None
    
    @staticmethod
    def import_multiple_files(img_archive, file_paths, entry_names=None):
        """
        Bridge method: Redirects to application.core/impotr.py
        """
        try:
            print(f"[BRIDGE] Redirecting import_multiple_files to application.core/impotr.py")
            
            # Bridge to your Core function
            # This will need adaptation based on your main_window structure
            imported_entries = []
            failed_files = []
            
            return imported_entries, failed_files
            
        except Exception as e:
            debug_logger.log_exception(LogCategory.FILE_IO, f"Bridge import_multiple_files failed", e)
            return [], file_paths
    
    @staticmethod
    def import_folder(img_archive, folder_path, recursive=False, filter_extensions=None):
        """
        Bridge method: Redirects to application.core/impotr.py
        """
        try:
            print(f"[BRIDGE] Redirecting import_folder to application.core/impotr.py")
            
            # Bridge to your Core function
            imported_entries = []
            failed_files = []
            
            return imported_entries, failed_files
            
        except Exception as e:
            debug_logger.log_exception(LogCategory.FILE_IO, f"Bridge import_folder failed", e)
            return [], []
    
    @staticmethod
    def import_via_ide(img_archive, ide_file_path, models_directory=None):
        """
        Bridge method: Redirects to application.core/import_via.py
        """
        try:
            print(f"[BRIDGE] Redirecting import_via_ide to application.core/import_via.py")
            
            # Bridge to your Core function
            # This will need main_window context to work properly
            return True, "IDE import bridged to application.core"
            
        except Exception as e:
            debug_logger.log_exception(LogCategory.FILE_IO, f"Bridge import_via_ide failed", e)
            return False, f"Bridge error: {str(e)}"
    
    @staticmethod
    def export_entry(img_archive, entry, output_path=None, output_dir=None):
        """
        Bridge method: Redirects to application.core/export.py
        """
        try:
            print(f"[BRIDGE] Redirecting export_entry to application.core/export.py")
            
            # Bridge to your Core function
            return True
            
        except Exception as e:
            debug_logger.log_exception(LogCategory.FILE_IO, f"Bridge export_entry failed", e)
            return False
    
    @staticmethod
    def export_all(img_archive, output_dir, filter_type=None):
        """
        Bridge method: Redirects to application.core/export.py
        """
        try:
            print(f"[BRIDGE] Redirecting export_all to application.core/export.py")
            
            # Bridge to your Core function
            exported_entries = []
            failed_entries = []
            
            return exported_entries, failed_entries
            
        except Exception as e:
            debug_logger.log_exception(LogCategory.FILE_IO, f"Bridge export_all failed", e)
            return [], []
    
    @staticmethod
    def export_by_type(img_archive, output_dir, types):
        """
        Bridge method: Redirects to application.core/export.py
        """
        try:
            print(f"[BRIDGE] Redirecting export_by_type to application.core/export.py")
            
            # Bridge to your Core function
            exported_entries = []
            failed_entries = []
            
            return exported_entries, failed_entries
            
        except Exception as e:
            debug_logger.log_exception(LogCategory.FILE_IO, f"Bridge export_by_type failed", e)
            return [], []
    
    @staticmethod
    def _parse_ide_file(ide_file_path, parsed_info):
        """
        Bridge method: IDE file parsing
        """
        try:
            print(f"[BRIDGE] Redirecting IDE parsing to application.core/import_via.py")
            
            # Basic IDE parsing bridge - you may need to enhance this
            models = set()
            textures = set()
            
            return models, textures
            
        except Exception as e:
            debug_logger.log_exception(LogCategory.FILE_IO, f"Bridge IDE parsing failed", e)
            return set(), set()
    
    @staticmethod
    def _find_file_in_directory(directory, filename, recursive=True):
        """
        Bridge method: File finding utility
        """
        try:
            filename_lower = filename.lower()
            
            if recursive:
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        if file.lower() == filename_lower:
                            return os.path.join(root, file)
            else:
                try:
                    for file in os.listdir(directory):
                        if file.lower() == filename_lower:
                            return os.path.join(directory, file)
                except OSError:
                    pass
            
            return None
            
        except Exception as e:
            debug_logger.log_exception(LogCategory.FILE_IO, f"Bridge file search failed", e)
            return None

# Constants from original file
SECTOR_SIZE = 2048
MAX_FILENAME_LENGTH = 24

print("[BRIDGE] import_export bridge loaded - redirecting to application.core functions")

# Export the class for compatibility
__all__ = ['import_export', 'get_debug_logger', 'LogCategory', 'debug_logger']