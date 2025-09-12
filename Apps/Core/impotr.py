#this belongs in Core/import.py - Version: 1
# X-Seti - September11 2025 - IMG Factory 1.5 - Core Import Functions

"""
Core Import Functions - Essential file import operations extracted from img_editor_tool
Handles single file, multiple file, and folder import with RW detection and validation
"""

import os
from typing import Optional, List, Dict, Any, Tuple
from PyQt6.QtWidgets import QMessageBox, QFileDialog

# Import from new structure
from Core.rw_versions import detect_rw_file_format, get_rw_version_name, is_valid_rw_version
from Shared.progress_functions import show_progress, update_progress, hide_progress, start_operation, complete_operation
from Shared.populate_img_table import populate_img_table_enhanced, refresh_table

##Methods list -
# import_file_to_img
# import_multiple_files
# import_folder_contents
# import_files_function
# get_import_preview
# validate_import_files
# _process_single_import
# _detect_file_format
# _add_entry_to_img
# integrate_import_functions

def import_file_to_img(main_window, file_path: str, entry_name: str = None) -> bool: #vers 1
    """Import single file to current IMG
    
    Args:
        main_window: Main window instance
        file_path: Path to file to import
        entry_name: Optional custom entry name (uses filename if None)
        
    Returns:
        bool: True if import successful
    """
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("❌ No IMG file open")
            return False

        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"❌ File not found: {file_path}")
            return False

        # Use filename if no entry name provided
        if entry_name is None:
            entry_name = os.path.basename(file_path)

        # Read file data
        try:
            with open(file_path, 'rb') as f:
                file_data = f.read()
        except Exception as e:
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"❌ Error reading file {entry_name}: {str(e)}")
            return False

        # Detect RW format
        file_format, version_desc, version_value = detect_rw_file_format(file_data, entry_name)
        rw_info = f" ({file_format} {version_desc})" if is_valid_rw_version(version_value) else ""

        # Import to IMG
        success = _add_entry_to_img(main_window, entry_name, file_data)
        
        if success:
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"✅ Imported: {entry_name}{rw_info}")
            return True
        else:
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"❌ Failed to import: {entry_name}")
            return False

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Import error: {str(e)}")
        return False

def import_multiple_files(main_window, file_paths: List[str], entry_names: List[str] = None) -> Tuple[int, int]: #vers 1
    """Import multiple files to current IMG
    
    Args:
        main_window: Main window instance
        file_paths: List of file paths to import
        entry_names: Optional list of custom entry names
        
    Returns:
        Tuple[int, int]: (imported_count, failed_count)
    """
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("❌ No IMG file open")
            return 0, len(file_paths)

        if not file_paths:
            return 0, 0

        total_files = len(file_paths)
        imported_count = 0
        failed_count = 0

        # Start operation with progress
        start_operation(main_window, f"Importing {total_files} files", cancellable=True)

        for i, file_path in enumerate(file_paths):
            # Check for cancellation
            if hasattr(main_window, 'is_operation_cancelled') and main_window.is_operation_cancelled():
                if hasattr(main_window, 'log_message'):
                    main_window.log_message("⚠️ Import cancelled by user")
                break

            # Get entry name
            if entry_names and i < len(entry_names):
                entry_name = entry_names[i]
            else:
                entry_name = os.path.basename(file_path)

            # Update progress
            progress = int((i / total_files) * 100)
            update_progress(main_window, progress, f"Importing {entry_name}...")

            # Import file
            if import_file_to_img(main_window, file_path, entry_name):
                imported_count += 1
            else:
                failed_count += 1

        # Complete operation
        complete_operation(main_window, True, f"Import complete: {imported_count} imported, {failed_count} failed")

        # Refresh table if any imports succeeded
        if imported_count > 0:
            _refresh_img_table(main_window)

        return imported_count, failed_count

    except Exception as e:
        complete_operation(main_window, False, f"Import failed: {str(e)}")
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Multiple import error: {str(e)}")
        return 0, len(file_paths) if file_paths else 0

def import_folder_contents(main_window, folder_path: str, recursive: bool = False, 
                          filter_extensions: List[str] = None) -> Tuple[int, int]: #vers 1
    """Import folder contents to current IMG
    
    Args:
        main_window: Main window instance
        folder_path: Path to folder to import
        recursive: Whether to include subdirectories
        filter_extensions: List of extensions to include (e.g., ['dff', 'txd'])
        
    Returns:
        Tuple[int, int]: (imported_count, failed_count)
    """
    try:
        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"❌ Folder not found: {folder_path}")
            return 0, 0

        # Default supported extensions
        if filter_extensions is None:
            filter_extensions = ['dff', 'txd', 'col', 'ifp', 'wav', 'mp3', 'dat', 'ipl']

        # Convert to lowercase for comparison
        filter_extensions = [ext.lower().lstrip('.') for ext in filter_extensions]

        # Collect files
        files_to_import = []

        if recursive:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_ext = os.path.splitext(file)[1].lower().lstrip('.')
                    if file_ext in filter_extensions:
                        files_to_import.append(os.path.join(root, file))
        else:
            for file in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file)
                if os.path.isfile(file_path):
                    file_ext = os.path.splitext(file)[1].lower().lstrip('.')
                    if file_ext in filter_extensions:
                        files_to_import.append(file_path)

        if not files_to_import:
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"⚠️ No supported files found in folder")
            return 0, 0

        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"📁 Found {len(files_to_import)} files in folder")

        # Import all found files
        return import_multiple_files(main_window, files_to_import)

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Folder import error: {str(e)}")
        return 0, 0

def import_files_function(main_window) -> bool: #vers 1
    """Main import function with file dialog"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first")
            return False

        # Show file dialog
        file_paths, _ = QFileDialog.getOpenFileNames(
            main_window,
            "Import Files",
            "",
            "All Supported (*.dff *.txd *.col *.ifp *.wav *.mp3 *.dat *.ipl);;"
            "Models (*.dff);;"
            "Textures (*.txd);;"
            "Collision (*.col);;"
            "Animations (*.ifp);;"
            "Audio (*.wav *.mp3);;"
            "Data (*.dat *.ipl);;"
            "All Files (*.*)"
        )

        if not file_paths:
            return False

        # Import selected files
        imported, failed = import_multiple_files(main_window, file_paths)
        
        return imported > 0

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Import dialog error: {str(e)}")
        return False

def get_import_preview(main_window, file_paths: List[str]) -> Dict[str, Any]: #vers 1
    """Get preview information for files to be imported
    
    Args:
        main_window: Main window instance
        file_paths: List of file paths to analyze
        
    Returns:
        Dict with preview information
    """
    try:
        preview = {
            'total_files': len(file_paths),
            'valid_files': 0,
            'total_size': 0,
            'file_types': {},
            'rw_versions': {},
            'files': []
        }

        for file_path in file_paths:
            if not os.path.exists(file_path):
                continue

            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            file_ext = os.path.splitext(file_name)[1].upper().lstrip('.')

            # Read file header for RW detection
            try:
                with open(file_path, 'rb') as f:
                    header_data = f.read(min(1024, file_size))

                file_format, version_desc, version_value = detect_rw_file_format(header_data, file_name)

                file_info = {
                    'name': file_name,
                    'path': file_path,
                    'size': file_size,
                    'type': file_ext,
                    'rw_format': file_format,
                    'rw_version': version_desc,
                    'is_valid_rw': is_valid_rw_version(version_value) if version_value else False
                }

                preview['files'].append(file_info)
                preview['valid_files'] += 1
                preview['total_size'] += file_size

                # Track file types
                if file_ext not in preview['file_types']:
                    preview['file_types'][file_ext] = 0
                preview['file_types'][file_ext] += 1

                # Track RW versions
                if version_desc not in preview['rw_versions']:
                    preview['rw_versions'][version_desc] = 0
                preview['rw_versions'][version_desc] += 1

            except Exception:
                # Skip files we can't read
                continue

        return preview

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Import preview error: {str(e)}")
        return {'total_files': 0, 'valid_files': 0, 'files': []}

def validate_import_files(main_window, file_paths: List[str]) -> Tuple[List[str], List[str]]: #vers 1
    """Validate files for import
    
    Args:
        main_window: Main window instance
        file_paths: List of file paths to validate
        
    Returns:
        Tuple[List[str], List[str]]: (valid_files, invalid_files)
    """
    valid_files = []
    invalid_files = []

    for file_path in file_paths:
        try:
            # Check file exists
            if not os.path.exists(file_path):
                invalid_files.append(file_path)
                continue

            # Check file is readable
            if not os.path.isfile(file_path):
                invalid_files.append(file_path)
                continue

            # Check file size
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                invalid_files.append(file_path)
                continue

            # Check we can read the file
            try:
                with open(file_path, 'rb') as f:
                    f.read(100)  # Try to read first 100 bytes
                valid_files.append(file_path)
            except Exception:
                invalid_files.append(file_path)

        except Exception:
            invalid_files.append(file_path)

    return valid_files, invalid_files

def _add_entry_to_img(main_window, entry_name: str, file_data: bytes) -> bool: #vers 1
    """Add entry to IMG using available methods"""
    try:
        # Method 1: Use add_entry_safe if available
        if hasattr(main_window, 'add_entry_safe'):
            return main_window.add_entry_safe(main_window.current_img, entry_name, file_data)
        
        # Method 2: Use IMG object add_entry method
        elif hasattr(main_window.current_img, 'add_entry'):
            return main_window.current_img.add_entry(entry_name, file_data)
        
        # Method 3: Direct entry creation (fallback)
        else:
            # This would need to be implemented based on your IMG structure
            if hasattr(main_window, 'log_message'):
                main_window.log_message("⚠️ No add_entry method available")
            return False

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Error adding entry {entry_name}: {str(e)}")
        return False

def _refresh_img_table(main_window): #vers 1
    """Refresh IMG table after import"""
    try:
        # Use existing table population functions
        if hasattr(main_window, 'refresh_table'):
            main_window.refresh_table()
        elif hasattr(main_window, 'populate_img_table_enhanced'):
            main_window.populate_img_table_enhanced(main_window.current_img)
        elif hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'table'):
            # Force table refresh by repopulating
            populate_img_table_enhanced(main_window, main_window.current_img)
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"⚠️ Table refresh failed: {str(e)}")

def integrate_import_functions(main_window) -> bool: #vers 1
    """Integrate core import functions into main window"""
    try:
        # Add core import methods
        main_window.import_file_to_img = lambda file_path, entry_name=None: import_file_to_img(main_window, file_path, entry_name)
        main_window.import_multiple_files = lambda file_paths, entry_names=None: import_multiple_files(main_window, file_paths, entry_names)
        main_window.import_folder_contents = lambda folder_path, recursive=False, filter_extensions=None: import_folder_contents(main_window, folder_path, recursive, filter_extensions)
        main_window.import_files_function = lambda: import_files_function(main_window)
        main_window.get_import_preview = lambda file_paths: get_import_preview(main_window, file_paths)
        main_window.validate_import_files = lambda file_paths: validate_import_files(main_window, file_paths)

        # Aliases for backward compatibility
        main_window.import_files = main_window.import_files_function
        main_window.import_file = main_window.import_file_to_img

        if hasattr(main_window, 'log_message'):
            main_window.log_message("✅ Core Import functions integrated")
            main_window.log_message("   • Single file import")
            main_window.log_message("   • Multiple file import") 
            main_window.log_message("   • Folder import with filters")
            main_window.log_message("   • RW version detection")
            main_window.log_message("   • Import preview and validation")

        return True

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Core Import integration failed: {str(e)}")
        return False

# Export functions
__all__ = [
    'import_file_to_img',
    'import_multiple_files',
    'import_folder_contents',
    'import_files_function',
    'get_import_preview',
    'validate_import_files',
    'integrate_import_functions'
]