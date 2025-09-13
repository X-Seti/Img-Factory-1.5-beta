#this belongs in Core/open.py - Version: 1
# X-Seti - September11 2025 - IMG Factory 1.5 - Core Open Functions

"""
Core Open Functions - File opening operations for IMG and COL files
Handles opening single files, multiple files, and file format detection with UI integration
"""

import os
from typing import Optional, List, Dict, Any, Tuple
from PyQt6.QtWidgets import QMessageBox, QFileDialog
from PyQt6.QtCore import QThread, pyqtSignal

# Import from new structure
from Core.rw_versions import detect_rw_file_format, get_rw_version_name, is_valid_rw_version
from Shared.progress_functions import show_progress, update_progress, hide_progress, start_operation, complete_operation
from Shared.populate_img_table import populate_img_table_enhanced
from Shared.populate_col_table import populate_col_table_enhanced

##Methods list -
# open_img_file
# open_multiple_img_files
# open_file_dialog
# detect_file_type
# validate_file_before_open
# get_file_info
# _load_img_file
# _load_col_file
# _update_ui_for_loaded_file
# _detect_and_open_file
# integrate_open_functions

##Classes -
# FileLoadThread

class FileLoadThread(QThread): #vers 1
    """Background thread for loading large IMG/COL files"""
    
    progress_updated = pyqtSignal(int, str)  # progress %, message
    loading_finished = pyqtSignal(object, str, str)  # file_object, file_type, file_path
    loading_error = pyqtSignal(str)  # error message
    
    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path
        self.file_object = None
        self.file_type = None
        
    def run(self):
        """Load file in background thread"""
        try:
            self.progress_updated.emit(10, "Detecting file type...")
            
            # Detect file type
            self.file_type = detect_file_type(None, self.file_path)
            
            if self.file_type == 'IMG':
                self.progress_updated.emit(30, "Loading IMG file...")
                self.file_object = self._load_img_file()
            elif self.file_type == 'COL':
                self.progress_updated.emit(30, "Loading COL file...")
                self.file_object = self._load_col_file()
            else:
                self.loading_error.emit(f"Unsupported file type: {self.file_type}")
                return
            
            if self.file_object:
                self.progress_updated.emit(100, "File loaded successfully")
                self.loading_finished.emit(self.file_object, self.file_type, self.file_path)
            else:
                self.loading_error.emit("Failed to load file")
                
        except Exception as e:
            self.loading_error.emit(f"Loading error: {str(e)}")
    
    def _load_img_file(self) -> Optional[object]:
        """Load IMG file using available methods"""
        try:
            # Try to use existing IMG loading functions
            from methods.img_core_classes import IMGFile
            
            img_file = IMGFile(self.file_path)
            if img_file.load():
                return img_file
            else:
                return None
                
        except ImportError:
            # Fallback to IMG Editor Tool
            try:
                from Tools.img_editor_tool import IMGEditorTool
                tool = IMGEditorTool()
                adapter = tool.get_adapter()
                if adapter.open_img(self.file_path):
                    return adapter.get_active_archive()
                else:
                    return None
            except Exception:
                return None
    
    def _load_col_file(self) -> Optional[object]:
        """Load COL file using available methods"""
        try:
            from methods.col_core_classes import COLFile
            
            col_file = COLFile(self.file_path)
            if col_file.load():
                return col_file
            else:
                return None
                
        except ImportError:
            return None

def open_img_file(main_window, file_path: str = None) -> bool: #vers 1
    """Open IMG or COL file
    
    Args:
        main_window: Main window instance
        file_path: Path to file to open (shows dialog if None)
        
    Returns:
        bool: True if file opened successfully
    """
    try:
        # Show file dialog if no path provided
        if file_path is None:
            file_path = open_file_dialog(main_window)
            if not file_path:
                return False

        # Validate file before opening
        if not validate_file_before_open(main_window, file_path):
            return False

        # Get file info for progress estimation
        file_info = get_file_info(main_window, file_path)
        file_size = file_info.get('size', 0)
        
        # For large files, use threaded loading
        if file_size > 50 * 1024 * 1024:  # 50MB threshold
            return _load_file_threaded(main_window, file_path)
        else:
            return _load_file_direct(main_window, file_path)

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Open file error: {str(e)}")
        return False

def open_multiple_img_files(main_window) -> int: #vers 1
    """Open multiple IMG/COL files in tabs
    
    Args:
        main_window: Main window instance
        
    Returns:
        int: Number of files successfully opened
    """
    try:
        # Show multiple file selection dialog
        file_paths, _ = QFileDialog.getOpenFileNames(
            main_window,
            "Open Multiple Files",
            "",
            "IMG/COL Files (*.img *.col);;IMG Files (*.img);;COL Files (*.col);;All Files (*.*)"
        )

        if not file_paths:
            return 0

        opened_count = 0
        failed_count = 0

        # Start operation with progress
        start_operation(main_window, f"Opening {len(file_paths)} files", cancellable=True)

        for i, file_path in enumerate(file_paths):
            # Check for cancellation
            if hasattr(main_window, 'is_operation_cancelled') and main_window.is_operation_cancelled():
                if hasattr(main_window, 'log_message'):
                    main_window.log_message("⚠️ Multiple file open cancelled by user")
                break

            # Update progress
            progress = int((i / len(file_paths)) * 100)
            filename = os.path.basename(file_path)
            update_progress(main_window, progress, f"Opening {filename}...")

            # Open file
            if open_img_file(main_window, file_path):
                opened_count += 1
            else:
                failed_count += 1

        # Complete operation
        complete_operation(main_window, True, f"Opened {opened_count} files, {failed_count} failed")

        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"📁 Multiple file open: {opened_count} opened, {failed_count} failed")

        return opened_count

    except Exception as e:
        complete_operation(main_window, False, f"Multiple file open failed: {str(e)}")
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Multiple file open error: {str(e)}")
        return 0

def open_file_dialog(main_window) -> Optional[str]: #vers 1
    """Show file open dialog and return selected file path
    
    Args:
        main_window: Main window instance
        
    Returns:
        Optional[str]: Selected file path or None if cancelled
    """
    try:
        file_path, _ = QFileDialog.getOpenFileName(
            main_window,
            "Open IMG/COL File",
            "",
            "IMG/COL Files (*.img *.col);;IMG Files (*.img);;COL Files (*.col);;All Files (*.*)"
        )
        
        return file_path if file_path else None

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ File dialog error: {str(e)}")
        return None

def detect_file_type(main_window, file_path: str) -> str: #vers 1
    """Detect file type from extension and content
    
    Args:
        main_window: Main window instance (can be None)
        file_path: Path to file to analyze
        
    Returns:
        str: File type ('IMG', 'COL', 'UNKNOWN')
    """
    try:
        if not os.path.exists(file_path):
            return 'UNKNOWN'

        # Check extension first
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.img':
            return 'IMG'
        elif file_ext == '.col':
            return 'COL'
        
        # Check file signature for files without clear extensions
        try:
            with open(file_path, 'rb') as f:
                signature = f.read(4)
                
                # COL file signature
                if signature == b'COLL':
                    return 'COL'
                
                # IMG file detection (check for reasonable header)
                f.seek(0)
                header = f.read(8)
                if len(header) == 8:
                    # Basic IMG validation
                    return 'IMG'
                    
        except Exception:
            pass

        return 'UNKNOWN'

    except Exception as e:
        if main_window and hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ File type detection error: {str(e)}")
        return 'UNKNOWN'

def validate_file_before_open(main_window, file_path: str) -> bool: #vers 1
    """Validate file before attempting to open
    
    Args:
        main_window: Main window instance
        file_path: Path to file to validate
        
    Returns:
        bool: True if file is valid for opening
    """
    try:
        # Check file exists
        if not os.path.exists(file_path):
            QMessageBox.warning(main_window, "File Not Found", f"File does not exist:\n{file_path}")
            return False

        # Check file is readable
        if not os.access(file_path, os.R_OK):
            QMessageBox.warning(main_window, "Access Denied", f"Cannot read file:\n{file_path}")
            return False

        # Check file size (reasonable limits)
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            QMessageBox.warning(main_window, "Empty File", f"File is empty:\n{file_path}")
            return False

        if file_size > 2 * 1024 * 1024 * 1024:  # 2GB limit
            reply = QMessageBox.question(
                main_window,
                "Large File",
                f"File is very large ({file_size // (1024*1024)} MB).\n"
                f"Opening may take a long time and use significant memory.\n\n"
                f"Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return False

        # Detect and validate file type
        file_type = detect_file_type(main_window, file_path)
        if file_type == 'UNKNOWN':
            reply = QMessageBox.question(
                main_window,
                "Unknown File Type",
                f"Cannot determine file type for:\n{file_path}\n\n"
                f"Attempt to open anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return False

        return True

    except Exception as e:
        QMessageBox.critical(main_window, "Validation Error", f"Error validating file:\n{str(e)}")
        return False

def get_file_info(main_window, file_path: str) -> Dict[str, Any]: #vers 1
    """Get file information for display and processing
    
    Args:
        main_window: Main window instance
        file_path: Path to file to analyze
        
    Returns:
        Dict: File information
    """
    try:
        info = {
            'path': file_path,
            'name': os.path.basename(file_path),
            'size': 0,
            'type': 'UNKNOWN',
            'exists': False,
            'readable': False
        }

        if os.path.exists(file_path):
            info['exists'] = True
            info['size'] = os.path.getsize(file_path)
            info['readable'] = os.access(file_path, os.R_OK)
            info['type'] = detect_file_type(main_window, file_path)

        return info

    except Exception as e:
        if main_window and hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ File info error: {str(e)}")
        return {'path': file_path, 'name': '', 'size': 0, 'type': 'UNKNOWN', 'exists': False, 'readable': False}

def _load_file_direct(main_window, file_path: str) -> bool: #vers 1
    """Load file directly (for smaller files)"""
    try:
        show_progress(main_window, 0, "Loading file...")
        
        file_type = detect_file_type(main_window, file_path)
        
        if file_type == 'IMG':
            update_progress(main_window, 50, "Loading IMG file...")
            file_object = _load_img_file(main_window, file_path)
        elif file_type == 'COL':
            update_progress(main_window, 50, "Loading COL file...")
            file_object = _load_col_file(main_window, file_path)
        else:
            hide_progress(main_window)
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"❌ Unsupported file type: {file_type}")
            return False

        if file_object:
            update_progress(main_window, 90, "Updating UI...")
            success = _update_ui_for_loaded_file(main_window, file_object, file_type, file_path)
            hide_progress(main_window)
            return success
        else:
            hide_progress(main_window)
            return False

    except Exception as e:
        hide_progress(main_window)
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Direct load error: {str(e)}")
        return False

def _load_file_threaded(main_window, file_path: str) -> bool: #vers 1
    """Load file using background thread (for larger files)"""
    try:
        # Create loading thread
        load_thread = FileLoadThread(file_path)
        
        # Connect signals
        load_thread.progress_updated.connect(lambda progress, message: update_progress(main_window, progress, message))
        load_thread.loading_finished.connect(lambda file_obj, file_type, path: _on_file_loaded(main_window, file_obj, file_type, path))
        load_thread.loading_error.connect(lambda error: _on_file_load_error(main_window, error))
        
        # Start loading
        start_operation(main_window, "Loading large file...", cancellable=False)
        load_thread.start()
        
        # Store thread reference to prevent garbage collection
        main_window._load_thread = load_thread
        
        return True  # Thread started successfully

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Threaded load error: {str(e)}")
        return False

def _load_img_file(main_window, file_path: str) -> Optional[object]: #vers 1
    """Load IMG file using available methods"""
    try:
        # Try to use existing IMG loading functions
        try:
            from methods.img_core_classes import IMGFile
            
            img_file = IMGFile(file_path)
            if img_file.load():
                return img_file
        except ImportError:
            pass
        
        # Fallback to IMG Editor Tool
        try:
            if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'img_editor_tool'):
                adapter = main_window.gui_layout.img_editor_tool.get_adapter()
                if adapter.open_img(file_path):
                    return adapter.get_active_archive()
        except Exception:
            pass
        
        return None

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ IMG load error: {str(e)}")
        return None

def _load_col_file(main_window, file_path: str) -> Optional[object]: #vers 1
    """Load COL file using available methods"""
    try:
        from methods.col_core_classes import COLFile
        
        col_file = COLFile(file_path)
        if col_file.load():
            return col_file
        else:
            return None
            
    except ImportError:
        if hasattr(main_window, 'log_message'):
            main_window.log_message("❌ COL loading not available - missing col_core_classes")
        return None
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ COL load error: {str(e)}")
        return None

def _update_ui_for_loaded_file(main_window, file_object, file_type: str, file_path: str) -> bool: #vers 1
    """Update UI after file is loaded"""
    try:
        # Set current file in main window
        if file_type == 'IMG':
            main_window.current_img = file_object
            if hasattr(main_window, 'current_col'):
                main_window.current_col = None
        elif file_type == 'COL':
            main_window.current_col = file_object
            if hasattr(main_window, 'current_img'):
                main_window.current_img = None

        # Update window title
        filename = os.path.basename(file_path)
        main_window.setWindowTitle(f"IMG Factory 1.5 - {filename}")

        # Populate table
        if file_type == 'IMG':
            if hasattr(main_window, 'populate_img_table_enhanced'):
                main_window.populate_img_table_enhanced(file_object)
            else:
                populate_img_table_enhanced(main_window, file_object)
        elif file_type == 'COL':
            if hasattr(main_window, 'populate_col_table_enhanced'):
                main_window.populate_col_table_enhanced(file_object)
            else:
                populate_col_table_enhanced(main_window, file_object)

        # Update status
        if hasattr(main_window, 'refresh_ui_status'):
            main_window.refresh_ui_status()

        # Log success
        if hasattr(main_window, 'log_message'):
            if file_type == 'IMG':
                entry_count = len(getattr(file_object, 'entries', []))
                main_window.log_message(f"📁 IMG file opened: {filename} ({entry_count} entries)")
            elif file_type == 'COL':
                model_count = len(getattr(file_object, 'models', []))
                main_window.log_message(f"📁 COL file opened: {filename} ({model_count} models)")

        return True

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ UI update error: {str(e)}")
        return False

def _on_file_loaded(main_window, file_object, file_type: str, file_path: str): #vers 1
    """Handle file loaded from background thread"""
    try:
        success = _update_ui_for_loaded_file(main_window, file_object, file_type, file_path)
        complete_operation(main_window, success, "File loaded successfully" if success else "Failed to update UI")
        
        # Clean up thread reference
        if hasattr(main_window, '_load_thread'):
            delattr(main_window, '_load_thread')

    except Exception as e:
        complete_operation(main_window, False, f"Load completion error: {str(e)}")

def _on_file_load_error(main_window, error_message: str): #vers 1
    """Handle file load error from background thread"""
    try:
        complete_operation(main_window, False, f"File load failed: {error_message}")
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ {error_message}")
        
        # Clean up thread reference
        if hasattr(main_window, '_load_thread'):
            delattr(main_window, '_load_thread')

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Error handler error: {str(e)}")

def integrate_open_functions(main_window) -> bool: #vers 1
    """Integrate open functions into main window"""
    try:
        # Add open methods
        main_window.open_img_file = lambda file_path=None: open_img_file(main_window, file_path)
        main_window.open_multiple_img_files = lambda: open_multiple_img_files(main_window)
        main_window.open_file_dialog = lambda: open_file_dialog(main_window)
        main_window.detect_file_type = lambda file_path: detect_file_type(main_window, file_path)
        main_window.validate_file_before_open = lambda file_path: validate_file_before_open(main_window, file_path)
        main_window.get_file_info = lambda file_path: get_file_info(main_window, file_path)

        # Aliases for backward compatibility
        main_window.open_file = main_window.open_img_file
        main_window.load_file = main_window.open_img_file

        if hasattr(main_window, 'log_message'):
            main_window.log_message("✅ Open functions integrated")
            main_window.log_message("   • IMG/COL file opening")
            main_window.log_message("   • Multiple file support")
            main_window.log_message("   • Background loading for large files")
            main_window.log_message("   • File validation and type detection")
            main_window.log_message("   • Progress tracking and cancellation")

        return True

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Open integration failed: {str(e)}")
        return False

# Export functions
__all__ = [
    'FileLoadThread',
    'open_img_file',
    'open_multiple_img_files',
    'open_file_dialog',
    'detect_file_type',
    'validate_file_before_open',
    'get_file_info',
    'integrate_open_functions'
]