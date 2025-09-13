#this belongs in Core/import_via.py - Version: 1
# X-Seti - September11 2025 - IMG Factory 1.5 - Import Via Functions

"""
Import Via Functions - Enhanced import operations using IDE parser, RW detection and GUI dialogs
Uses existing components: methods/ide_parser_functions.py, core/rw_versions.py, gui/ide_dialog.py
"""

import os
from typing import Optional, List, Dict, Any, Tuple
from PyQt6.QtWidgets import QMessageBox, QFileDialog, QProgressDialog
from PyQt6.QtCore import Qt

# Import existing components - updated paths
from Shared.ide_parser_functions import IDEParser, parse_ide_file
from Core.rw_versions import detect_rw_file_format, get_rw_version_name, is_valid_rw_version
from Gui.ide_dialog import IDEDialog, create_ide_dialog
from Shared.progress_functions import show_progress, hide_progress
from Shared.populate_img_table import refresh_table, populate_img_table_enhanced
from Shared.populate_col_table import populate_col_table_enhanced

##Methods list -
# import_files_via_function
# import_via_ide_dialog
# import_via_file_list
# import_via_folder_scan
# _validate_import_files
# _process_import_with_rw_detection
# _update_import_progress
# integrate_import_via_functions

def import_files_via_function(main_window): #vers 1
    """Main import via function - shows dialog for import method selection"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first")
            return False

        # Create IDE dialog for import operation
        dialog = create_ide_dialog(main_window, "import")
        if not dialog:
            main_window.log_message("❌ Failed to create import dialog")
            return False

        # Show dialog and get result
        if dialog.exec() == dialog.DialogCode.Accepted:
            parser = dialog.get_ide_parser()
            if parser and parser.models:
                return import_via_ide_dialog(main_window, parser, dialog.get_export_folder())
            else:
                main_window.log_message("⚠️ No files found in IDE or invalid selection")
                return False
        
        return False

    except Exception as e:
        main_window.log_message(f"❌ Import via failed: {str(e)}")
        return False

def import_via_ide_dialog(main_window, ide_parser: IDEParser, source_folder: str) -> bool: #vers 1
    """Import files using IDE parser results and RW detection"""
    try:
        if not ide_parser.models:
            main_window.log_message("⚠️ No models found in IDE file")
            return False

        # Validate source folder
        if not source_folder or not os.path.exists(source_folder):
            main_window.log_message("❌ Invalid source folder selected")
            return False

        # Get list of files to import from IDE
        files_to_import = []
        
        for model in ide_parser.models:
            # Add DFF file
            dff_path = os.path.join(source_folder, f"{model['name']}.dff")
            if os.path.exists(dff_path):
                files_to_import.append({
                    'path': dff_path,
                    'name': f"{model['name']}.dff",
                    'type': 'DFF',
                    'model_id': model.get('id', 'unknown')
                })

            # Add TXD file
            txd_path = os.path.join(source_folder, f"{model['name']}.txd")
            if os.path.exists(txd_path):
                files_to_import.append({
                    'path': txd_path,
                    'name': f"{model['name']}.txd",
                    'type': 'TXD',
                    'model_id': model.get('id', 'unknown')
                })

        if not files_to_import:
            main_window.log_message(f"⚠️ No matching files found in {source_folder}")
            return False

        # Validate files before import
        validated_files = _validate_import_files(main_window, files_to_import)
        if not validated_files:
            return False

        # Process import with RW detection
        return _process_import_with_rw_detection(main_window, validated_files)

    except Exception as e:
        main_window.log_message(f"❌ IDE import failed: {str(e)}")
        return False

def import_via_file_list(main_window, file_list_path: str) -> bool: #vers 1
    """Import files from a text file list"""
    try:
        if not os.path.exists(file_list_path):
            main_window.log_message("❌ File list not found")
            return False

        # Read file list
        with open(file_list_path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]

        if not lines:
            main_window.log_message("⚠️ Empty file list")
            return False

        # Get base directory from file list location
        base_dir = os.path.dirname(file_list_path)
        
        # Process files
        files_to_import = []
        for line in lines:
            file_path = os.path.join(base_dir, line) if not os.path.isabs(line) else line
            if os.path.exists(file_path):
                file_name = os.path.basename(file_path)
                file_ext = os.path.splitext(file_name)[1].upper().lstrip('.')
                
                files_to_import.append({
                    'path': file_path,
                    'name': file_name,
                    'type': file_ext,
                    'model_id': 'list_import'
                })

        if not files_to_import:
            main_window.log_message("⚠️ No valid files found in list")
            return False

        # Validate and import
        validated_files = _validate_import_files(main_window, files_to_import)
        if validated_files:
            return _process_import_with_rw_detection(main_window, validated_files)

        return False

    except Exception as e:
        main_window.log_message(f"❌ File list import failed: {str(e)}")
        return False

def import_via_folder_scan(main_window, folder_path: str, recursive: bool = False) -> bool: #vers 1
    """Import files by scanning folder for supported formats"""
    try:
        if not os.path.exists(folder_path):
            main_window.log_message("❌ Folder not found")
            return False

        supported_extensions = {'.dff', '.txd', '.col', '.ifp', '.wav', '.mp3'}
        files_to_import = []

        # Scan folder
        if recursive:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    if os.path.splitext(file)[1].lower() in supported_extensions:
                        file_path = os.path.join(root, file)
                        file_ext = os.path.splitext(file)[1].upper().lstrip('.')
                        
                        files_to_import.append({
                            'path': file_path,
                            'name': file,
                            'type': file_ext,
                            'model_id': 'folder_scan'
                        })
        else:
            for file in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file)
                if os.path.isfile(file_path) and os.path.splitext(file)[1].lower() in supported_extensions:
                    file_ext = os.path.splitext(file)[1].upper().lstrip('.')
                    
                    files_to_import.append({
                        'path': file_path,
                        'name': file,
                        'type': file_ext,
                        'model_id': 'folder_scan'
                    })

        if not files_to_import:
            main_window.log_message("⚠️ No supported files found in folder")
            return False

        # Validate and import
        validated_files = _validate_import_files(main_window, files_to_import)
        if validated_files:
            return _process_import_with_rw_detection(main_window, validated_files)

        return False

    except Exception as e:
        main_window.log_message(f"❌ Folder scan import failed: {str(e)}")
        return False

def _validate_import_files(main_window, files_to_import: List[Dict]) -> Optional[List[Dict]]: #vers 1
    """Validate files before import with RW detection"""
    try:
        validated_files = []
        
        for file_info in files_to_import:
            file_path = file_info['path']
            
            # Check file exists and is readable
            if not os.path.exists(file_path) or not os.path.isfile(file_path):
                main_window.log_message(f"⚠️ Skipping invalid file: {file_info['name']}")
                continue

            # Check file size
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                main_window.log_message(f"⚠️ Skipping empty file: {file_info['name']}")
                continue

            # Read file header for RW detection
            try:
                with open(file_path, 'rb') as f:
                    header_data = f.read(min(1024, file_size))  # Read first 1KB
                
                # Detect RW format
                file_format, version_desc, version_value = detect_rw_file_format(header_data, file_info['name'])
                
                # Add RW info to file info
                file_info.update({
                    'size': file_size,
                    'rw_format': file_format,
                    'rw_version': version_desc,
                    'rw_value': version_value,
                    'is_valid_rw': is_valid_rw_version(version_value) if version_value else False
                })
                
                validated_files.append(file_info)
                
            except Exception as e:
                main_window.log_message(f"⚠️ Error reading {file_info['name']}: {str(e)}")
                continue

        return validated_files if validated_files else None

    except Exception as e:
        main_window.log_message(f"❌ File validation failed: {str(e)}")
        return None

def _process_import_with_rw_detection(main_window, validated_files: List[Dict]) -> bool: #vers 1
    """Process import with progress and RW version logging"""
    try:
        total_files = len(validated_files)
        imported_count = 0
        failed_count = 0

        # Show progress
        show_progress(main_window, 0, f"Importing {total_files} files...")

        for i, file_info in enumerate(validated_files):
            try:
                # Update progress
                progress = int((i / total_files) * 100)
                _update_import_progress(main_window, progress, f"Importing {file_info['name']}...")

                # Read file data
                with open(file_info['path'], 'rb') as f:
                    file_data = f.read()

                # Import using existing IMG functions
                if hasattr(main_window, 'add_entry_safe'):
                    success = main_window.add_entry_safe(main_window.current_img, file_info['name'], file_data)
                elif hasattr(main_window, 'current_img') and hasattr(main_window.current_img, 'add_entry'):
                    success = main_window.current_img.add_entry(file_info['name'], file_data)
                else:
                    main_window.log_message("❌ No import method available")
                    return False

                if success:
                    imported_count += 1
                    # Log with RW info
                    rw_info = f" ({file_info['rw_format']} {file_info['rw_version']})" if file_info.get('is_valid_rw') else ""
                    main_window.log_message(f"✅ Imported: {file_info['name']}{rw_info}")
                else:
                    failed_count += 1
                    main_window.log_message(f"❌ Failed: {file_info['name']}")

            except Exception as e:
                failed_count += 1
                main_window.log_message(f"❌ Error importing {file_info['name']}: {str(e)}")

        # Hide progress
        hide_progress(main_window)

        # Summary
        main_window.log_message(f"📋 Import complete: {imported_count} imported, {failed_count} failed")

        # Refresh table if successful imports
        if imported_count > 0:
            # Use existing table population functions
            if hasattr(main_window, 'refresh_table'):
                main_window.refresh_table()
            elif hasattr(main_window, 'populate_img_table_enhanced'):
                main_window.populate_img_table_enhanced(main_window.current_img)
            return True

        return imported_count > 0

    except Exception as e:
        hide_progress(main_window)
        main_window.log_message(f"❌ Import processing failed: {str(e)}")
        return False

def _update_import_progress(main_window, progress: int, message: str): #vers 1
    """Update import progress display"""
    try:
        show_progress(main_window, progress, message)
        # Also update any GUI progress elements
        if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'show_progress'):
            main_window.gui_layout.show_progress(progress, message)
    except Exception:
        pass  # Don't fail import on progress update errors

def integrate_import_via_functions(main_window) -> bool: #vers 1
    """Integrate import via functions into main window"""
    try:
        # Add import via methods
        main_window.import_files_via_function = lambda: import_files_via_function(main_window)
        main_window.import_via_ide = lambda parser, folder: import_via_ide_dialog(main_window, parser, folder)
        main_window.import_via_file_list = lambda path: import_via_file_list(main_window, path)
        main_window.import_via_folder_scan = lambda folder, recursive=False: import_via_folder_scan(main_window, folder, recursive)

        # Aliases for backward compatibility
        main_window.import_via_function = main_window.import_files_via_function
        main_window.import_via = main_window.import_files_via_function

        if hasattr(main_window, 'log_message'):
            main_window.log_message("✅ Import Via functions integrated")
            main_window.log_message("   • IDE parser integration")
            main_window.log_message("   • RW version detection")
            main_window.log_message("   • GUI dialog support")
            main_window.log_message("   • File list and folder scan")

        return True

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Import Via integration failed: {str(e)}")
        return False

# Export functions
__all__ = [
    'import_files_via_function',
    'import_via_ide_dialog',
    'import_via_file_list', 
    'import_via_folder_scan',
    'integrate_import_via_functions'
]
