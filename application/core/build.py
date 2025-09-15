#this belongs in Core/build.py - Version: 1
# X-Seti - September11 2025 - IMG Factory 1.5 - Single IMG Rebuild

"""
Single IMG Rebuild - Handles rebuilding individual IMG files
Core operations for rebuilding current IMG file with progress tracking
"""

import os
import tempfile
import shutil
from typing import Optional, Callable
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import Qt

##Methods list -
# rebuild_img
# rebuild_current_img
# validate_rebuild_operation
# create_rebuild_backup
# perform_img_rebuild
# _calculate_rebuild_requirements
# _write_rebuilt_img_data
# finalize_rebuild_operation

def rebuild_img(main_window) -> bool: #vers 1
    """Rebuild the currently active IMG file"""
    try:
        if not validate_rebuild_operation(main_window):
            return False

        # Get current tab and IMG file
        current_tab = main_window.tab_widget.currentWidget()
        if not current_tab or not hasattr(current_tab, 'img_file'):
            main_window.log_message("❌ No active IMG file to rebuild")
            return False

        img_file = current_tab.img_file
        file_path = getattr(img_file, 'file_path', None)
        
        if not file_path:
            main_window.log_message("❌ IMG file path not available")
            return False

        file_name = os.path.basename(file_path)
        main_window.log_message(f"🔨 Starting rebuild of: {file_name}")

        # Check if rebuild is necessary
        if not hasattr(img_file, 'modified') or not img_file.modified:
            reply = QMessageBox.question(
                main_window,
                "Rebuild IMG",
                f"'{file_name}' has no modifications.\n\nRebuild anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply != QMessageBox.StandardButton.Yes:
                main_window.log_message("❌ Rebuild cancelled by user")
                return False

        # Create backup before rebuild
        backup_created = create_rebuild_backup(main_window, file_path)
        if not backup_created:
            main_window.log_message("⚠️ Failed to create backup, continuing anyway...")

        # Perform the rebuild with progress tracking
        success = perform_img_rebuild(main_window, img_file, file_path)
        
        if success:
            # Finalize rebuild operation
            finalize_rebuild_operation(main_window, img_file)
            main_window.log_message(f"✅ Successfully rebuilt: {file_name}")
            return True
        else:
            main_window.log_message(f"❌ Failed to rebuild: {file_name}")
            return False

    except Exception as e:
        main_window.log_message(f"❌ Rebuild operation failed: {str(e)}")
        return False


def rebuild_current_img(main_window) -> bool: #vers 1
    """Alias for rebuild_img - maintains compatibility"""
    return rebuild_img(main_window)


def validate_rebuild_operation(main_window) -> bool: #vers 1
    """Validate if rebuild operation can proceed"""
    try:
        if not hasattr(main_window, 'tab_widget') or main_window.tab_widget.count() == 0:
            main_window.log_message("❌ No IMG files to rebuild")
            return False

        # Check if any operations are running
        if hasattr(main_window, 'progress_dialog') and main_window.progress_dialog.isVisible():
            QMessageBox.warning(
                main_window,
                "Operation in Progress",
                "Cannot rebuild while another operation is in progress.\n"
                "Please wait for the current operation to complete."
            )
            return False

        # Get current IMG file
        current_tab = main_window.tab_widget.currentWidget()
        if not current_tab or not hasattr(current_tab, 'img_file'):
            return False

        img_file = current_tab.img_file
        
        # Check if file has entries
        if not hasattr(img_file, 'entries') or not img_file.entries:
            main_window.log_message("❌ IMG file has no entries to rebuild")
            return False

        # Check file path accessibility
        file_path = getattr(img_file, 'file_path', None)
        if not file_path or not os.path.exists(file_path):
            main_window.log_message("❌ IMG file path not accessible")
            return False

        # Check write permissions
        if not os.access(file_path, os.W_OK):
            main_window.log_message("❌ No write permission for IMG file")
            return False

        return True

    except Exception as e:
        main_window.log_message(f"❌ Rebuild validation failed: {str(e)}")
        return False


def create_rebuild_backup(main_window, file_path: str) -> bool: #vers 1
    """Create backup of IMG file before rebuild"""
    try:
        if not os.path.exists(file_path):
            return False

        backup_path = f"{file_path}.backup"
        
        # Remove old backup if exists
        if os.path.exists(backup_path):
            try:
                os.remove(backup_path)
            except:
                pass

        # Create new backup
        shutil.copy2(file_path, backup_path)
        
        if os.path.exists(backup_path):
            main_window.log_message(f"💾 Created backup: {os.path.basename(backup_path)}")
            return True
        else:
            return False

    except Exception as e:
        main_window.log_message(f"⚠️ Backup creation failed: {str(e)}")
        return False


def perform_img_rebuild(main_window, img_file, file_path: str) -> bool: #vers 1
    """Perform the actual IMG rebuild operation"""
    try:
        # Use existing rebuild system if available
        if hasattr(main_window, 'rebuild_img_file'):
            return main_window.rebuild_img_file(img_file)
        
        # Import rebuild functionality
        try:
            from application.core.rebuild import rebuild_img_file_core
            return rebuild_img_file_core(main_window, img_file)
        except ImportError:
            pass

        # Fallback to basic rebuild
        return _basic_img_rebuild(main_window, img_file, file_path)

    except Exception as e:
        main_window.log_message(f"❌ IMG rebuild failed: {str(e)}")
        return False


def _basic_img_rebuild(main_window, img_file, file_path: str) -> bool: #vers 1
    """Basic IMG rebuild implementation"""
    try:
        # Calculate rebuild requirements
        requirements = _calculate_rebuild_requirements(main_window, img_file)
        if not requirements:
            return False

        # Create temporary file for rebuild
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, f"rebuild_{os.path.basename(file_path)}")

        try:
            # Write rebuilt data to temporary file
            success = _write_rebuilt_img_data(main_window, img_file, temp_path, requirements)
            
            if success:
                # Replace original file with rebuilt version
                shutil.move(temp_path, file_path)
                return True
            else:
                return False

        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass

    except Exception as e:
        main_window.log_message(f"❌ Basic rebuild failed: {str(e)}")
        return False


def _calculate_rebuild_requirements(main_window, img_file) -> Optional[dict]: #vers 1
    """Calculate requirements for IMG rebuild"""
    try:
        if not hasattr(img_file, 'entries'):
            return None

        entries = img_file.entries
        
        # Calculate total data size
        total_data_size = sum(getattr(entry, 'size', 0) for entry in entries)
        
        # Calculate directory size (32 bytes per entry typically)
        directory_size = len(entries) * 32
        
        # IMG header size (typically 8 bytes)
        header_size = 8
        
        # Calculate data start offset
        data_start = header_size + directory_size
        
        requirements = {
            'entries': entries,
            'total_entries': len(entries),
            'header_size': header_size,
            'directory_size': directory_size,
            'data_start': data_start,
            'total_data_size': total_data_size,
            'total_file_size': data_start + total_data_size
        }

        main_window.log_message(f"📊 Rebuild requirements: {len(entries)} entries, {total_data_size:,} bytes data")
        return requirements

    except Exception as e:
        main_window.log_message(f"❌ Failed to calculate rebuild requirements: {str(e)}")
        return None


def _write_rebuilt_img_data(main_window, img_file, temp_path: str, requirements: dict) -> bool: #vers 1
    """Write rebuilt IMG data to temporary file"""
    try:
        entries = requirements['entries']
        data_start = requirements['data_start']
        
        with open(temp_path, 'wb') as temp_file:
            # Write IMG header
            temp_file.write(b'VER2')  # Version signature
            temp_file.write(len(entries).to_bytes(4, 'little'))  # Entry count

            # Write directory entries
            current_offset = data_start
            for entry in entries:
                entry_size = getattr(entry, 'size', 0)
                
                # Write directory entry (simplified format)
                temp_file.write(current_offset.to_bytes(4, 'little'))  # Offset
                temp_file.write(entry_size.to_bytes(4, 'little'))      # Size
                
                # Write entry name (24 bytes, null-padded)
                name = getattr(entry, 'name', '').encode('ascii', errors='ignore')[:23]
                name_padded = name.ljust(24, b'\x00')
                temp_file.write(name_padded)
                
                current_offset += entry_size

            # Write file data
            original_file_path = getattr(img_file, 'file_path', '')
            if os.path.exists(original_file_path):
                with open(original_file_path, 'rb') as source_file:
                    for entry in entries:
                        if hasattr(entry, 'offset') and hasattr(entry, 'size'):
                            source_file.seek(entry.offset)
                            data = source_file.read(entry.size)
                            temp_file.write(data)

        # Verify rebuilt file
        if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
            return True
        else:
            return False

    except Exception as e:
        main_window.log_message(f"❌ Failed to write rebuilt data: {str(e)}")
        return False


def finalize_rebuild_operation(main_window, img_file) -> bool: #vers 1
    """Finalize rebuild operation and update state"""
    try:
        # Clear modification flag
        if hasattr(img_file, 'modified'):
            img_file.modified = False

        # Clear deleted entries
        if hasattr(img_file, 'deleted_entries'):
            img_file.deleted_entries.clear()

        # Update any modification tracking
        if hasattr(img_file, 'clear_modification_tracking'):
            img_file.clear_modification_tracking()

        # Refresh table display
        if hasattr(main_window, 'refresh_table_display'):
            main_window.refresh_table_display()

        # Update UI state
        if hasattr(main_window, 'update_ui_after_operation'):
            main_window.update_ui_after_operation()

        return True

    except Exception as e:
        main_window.log_message(f"⚠️ Failed to finalize rebuild: {str(e)}")
        return False


def integrate_build_functions(main_window) -> bool: #vers 1
    """Integrate build functions into main window"""
    try:
        # Add build functions to main window
        main_window.rebuild_img = lambda: rebuild_img(main_window)
        main_window.rebuild_current_img = lambda: rebuild_current_img(main_window)
        main_window.validate_rebuild_operation = lambda: validate_rebuild_operation(main_window)
        main_window.create_rebuild_backup = lambda file_path: create_rebuild_backup(main_window, file_path)
        
        main_window.log_message("✅ Build functions integrated")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Failed to integrate build functions: {str(e)}")
        return False