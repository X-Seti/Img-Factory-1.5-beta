#this belongs in Core/replace.py - Version: 1
# X-Seti - September11 2025 - IMG Factory 1.5 - Replace Entry Operations

"""
Replace Entry Operations - Handles replacing selected entries in IMG files
Core operations for replacing existing entries with new file data
"""

import os
import shutil
from typing import Optional, List, Dict, Any
from pathlib import Path
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PyQt6.QtCore import Qt

##Methods list -
# replace_selected
# replace_entries_with_files
# replace_single_entry
# get_replacement_files
# validate_replace_operation
# _backup_original_entry
# _update_entry_data
# _verify_replacement_success

def replace_selected(main_window) -> bool: #vers 1
    """Replace selected IMG entries with new files"""
    try:
        if not validate_replace_operation(main_window):
            return False

        # Get current tab and IMG file
        current_tab = main_window.tab_widget.currentWidget()
        if not current_tab or not hasattr(current_tab, 'img_file'):
            main_window.log_message("❌ No active IMG file")
            return False

        img_file = current_tab.img_file
        
        # Get selected entries from table
        selected_entries = []
        if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'table'):
            table = main_window.gui_layout.table
            selected_rows = set()
            
            for item in table.selectedItems():
                selected_rows.add(item.row())
            
            if not selected_rows:
                main_window.log_message("❌ No entries selected for replacement")
                return False

            # Get entry objects from selected rows
            for row in selected_rows:
                if row < table.rowCount():
                    name_item = table.item(row, 0)  # Assuming name is in first column
                    if name_item:
                        entry_name = name_item.text()
                        # Find matching entry in IMG file
                        for entry in img_file.entries:
                            if entry.name.lower() == entry_name.lower():
                                selected_entries.append(entry)
                                break

        if not selected_entries:
            main_window.log_message("❌ No valid entries found for replacement")
            return False

        main_window.log_message(f"🔄 Replacing {len(selected_entries)} selected entries")

        # Get replacement files
        replacement_files = get_replacement_files(main_window, selected_entries)
        if not replacement_files:
            main_window.log_message("❌ No replacement files selected")
            return False

        # Perform replacements
        success = replace_entries_with_files(main_window, img_file, replacement_files)
        
        if success:
            # Mark IMG as modified
            if hasattr(img_file, 'modified'):
                img_file.modified = True
            
            # Refresh table display
            if hasattr(main_window, 'refresh_table_display'):
                main_window.refresh_table_display()
            
            main_window.log_message(f"✅ Successfully replaced {len(replacement_files)} entries")
            return True
        else:
            main_window.log_message("❌ Entry replacement failed")
            return False

    except Exception as e:
        main_window.log_message(f"❌ Replace operation failed: {str(e)}")
        return False


def get_replacement_files(main_window, selected_entries: List[Any]) -> Dict[str, str]: #vers 1
    """Get replacement files for selected entries"""
    try:
        replacement_files = {}
        
        if len(selected_entries) == 1:
            # Single file replacement
            entry = selected_entries[0]
            entry_name = getattr(entry, 'name', 'unknown')
            
            # Get file extension for filter
            ext = os.path.splitext(entry_name)[1].lower()
            file_filter = _get_file_filter_for_extension(ext)
            
            file_path, _ = QFileDialog.getOpenFileName(
                main_window,
                f"Select replacement file for: {entry_name}",
                os.path.expanduser("~/Desktop"),
                file_filter
            )
            
            if file_path:
                replacement_files[entry_name] = file_path
                
        else:
            # Multiple file replacement
            reply = QMessageBox.question(
                main_window,
                "Multiple Entry Replacement",
                f"Replace {len(selected_entries)} entries.\n\n"
                "Select replacement files one by one?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                for entry in selected_entries:
                    entry_name = getattr(entry, 'name', 'unknown')
                    ext = os.path.splitext(entry_name)[1].lower()
                    file_filter = _get_file_filter_for_extension(ext)
                    
                    file_path, _ = QFileDialog.getOpenFileName(
                        main_window,
                        f"Select replacement for: {entry_name}",
                        os.path.expanduser("~/Desktop"),
                        file_filter
                    )
                    
                    if file_path:
                        replacement_files[entry_name] = file_path
                    else:
                        # User cancelled, ask if they want to continue
                        continue_reply = QMessageBox.question(
                            main_window,
                            "Continue Replacement",
                            f"No file selected for '{entry_name}'.\n\nContinue with remaining entries?",
                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                            QMessageBox.StandardButton.Yes
                        )
                        
                        if continue_reply != QMessageBox.StandardButton.Yes:
                            break

        return replacement_files

    except Exception as e:
        main_window.log_message(f"❌ Failed to get replacement files: {str(e)}")
        return {}


def replace_entries_with_files(main_window, img_file, replacement_files: Dict[str, str]) -> bool: #vers 1
    """Replace entries with corresponding files"""
    try:
        success_count = 0
        failure_count = 0
        
        for entry_name, file_path in replacement_files.items():
            try:
                # Find the entry to replace
                target_entry = None
                for entry in img_file.entries:
                    if entry.name.lower() == entry_name.lower():
                        target_entry = entry
                        break
                
                if not target_entry:
                    main_window.log_message(f"⚠️ Entry not found: {entry_name}")
                    failure_count += 1
                    continue
                
                # Replace the entry
                if replace_single_entry(main_window, target_entry, file_path):
                    main_window.log_message(f"✅ Replaced: {entry_name}")
                    success_count += 1
                else:
                    main_window.log_message(f"❌ Failed to replace: {entry_name}")
                    failure_count += 1
                    
            except Exception as e:
                main_window.log_message(f"❌ Error replacing {entry_name}: {str(e)}")
                failure_count += 1

        # Report results
        main_window.log_message(f"📊 Replacement complete: {success_count} successful, {failure_count} failed")
        return success_count > 0

    except Exception as e:
        main_window.log_message(f"❌ Batch replacement failed: {str(e)}")
        return False


def replace_single_entry(main_window, entry, replacement_file_path: str) -> bool: #vers 1
    """Replace a single entry with new file data"""
    try:
        if not os.path.exists(replacement_file_path):
            main_window.log_message(f"❌ Replacement file not found: {replacement_file_path}")
            return False

        # Read replacement file data
        try:
            with open(replacement_file_path, 'rb') as f:
                new_data = f.read()
        except Exception as e:
            main_window.log_message(f"❌ Failed to read replacement file: {str(e)}")
            return False

        if not new_data:
            main_window.log_message(f"❌ Replacement file is empty: {replacement_file_path}")
            return False

        # Backup original entry data (optional)
        _backup_original_entry(main_window, entry)

        # Update entry with new data
        success = _update_entry_data(main_window, entry, new_data)
        
        if success:
            # Verify replacement
            if _verify_replacement_success(main_window, entry, len(new_data)):
                return True
            else:
                main_window.log_message(f"❌ Replacement verification failed for: {entry.name}")
                return False
        else:
            return False

    except Exception as e:
        main_window.log_message(f"❌ Single entry replacement failed: {str(e)}")
        return False


def _update_entry_data(main_window, entry, new_data: bytes) -> bool: #vers 1
    """Update entry with new data"""
    try:
        # Update entry size
        if hasattr(entry, 'size'):
            entry.size = len(new_data)
        
        # Store new data in entry (method depends on IMG implementation)
        if hasattr(entry, 'set_data'):
            entry.set_data(new_data)
        elif hasattr(entry, 'data'):
            entry.data = new_data
        else:
            # Fallback: store data as attribute
            entry._replacement_data = new_data
        
        # Mark entry as modified
        if hasattr(entry, 'modified'):
            entry.modified = True
        
        return True

    except Exception as e:
        main_window.log_message(f"❌ Failed to update entry data: {str(e)}")
        return False


def _backup_original_entry(main_window, entry) -> bool: #vers 1
    """Create backup of original entry data"""
    try:
        # This is optional - could store original data for undo functionality
        if hasattr(entry, 'data') and not hasattr(entry, '_original_data'):
            entry._original_data = entry.data
        elif hasattr(entry, 'get_data') and not hasattr(entry, '_original_data'):
            entry._original_data = entry.get_data()
        
        return True

    except Exception as e:
        main_window.log_message(f"⚠️ Failed to backup original entry: {str(e)}")
        return False


def _verify_replacement_success(main_window, entry, expected_size: int) -> bool: #vers 1
    """Verify that entry replacement was successful"""
    try:
        # Check size matches
        if hasattr(entry, 'size') and entry.size != expected_size:
            return False
        
        # Check data availability
        if hasattr(entry, 'data') and not entry.data:
            return False
        elif hasattr(entry, '_replacement_data') and not entry._replacement_data:
            return False
        
        return True

    except Exception as e:
        main_window.log_message(f"⚠️ Replacement verification failed: {str(e)}")
        return False


def _get_file_filter_for_extension(ext: str) -> str: #vers 1
    """Get file filter based on extension"""
    try:
        filter_map = {
            '.dff': "DFF Models (*.dff);;All Files (*.*)",
            '.txd': "TXD Textures (*.txd);;All Files (*.*)",
            '.col': "COL Collision (*.col);;All Files (*.*)",
            '.ide': "IDE Definition (*.ide);;All Files (*.*)",
            '.ipl': "IPL Placement (*.ipl);;All Files (*.*)",
            '.dat': "DAT Data (*.dat);;All Files (*.*)",
            '.wav': "WAV Audio (*.wav);;All Files (*.*)",
            '.mp3': "MP3 Audio (*.mp3);;All Files (*.*)",
        }
        
        return filter_map.get(ext.lower(), "All Files (*.*)")

    except:
        return "All Files (*.*)"


def validate_replace_operation(main_window) -> bool: #vers 1
    """Validate if replace operation can proceed"""
    try:
        if not hasattr(main_window, 'tab_widget') or main_window.tab_widget.count() == 0:
            main_window.log_message("❌ No IMG file loaded")
            return False

        # Check if any operations are running
        if hasattr(main_window, 'progress_dialog') and main_window.progress_dialog.isVisible():
            QMessageBox.warning(
                main_window,
                "Operation in Progress",
                "Cannot replace entries while another operation is in progress.\n"
                "Please wait for the current operation to complete."
            )
            return False

        return True

    except Exception as e:
        main_window.log_message(f"❌ Replace validation failed: {str(e)}")
        return False


def integrate_replace_functions(main_window) -> bool: #vers 1
    """Integrate replace functions into main window"""
    try:
        # Add replace functions to main window
        main_window.replace_selected = lambda: replace_selected(main_window)
        main_window.replace_entries_with_files = lambda img_file, replacement_files: replace_entries_with_files(main_window, img_file, replacement_files)
        main_window.replace_single_entry = lambda entry, file_path: replace_single_entry(main_window, entry, file_path)
        main_window.validate_replace_operation = lambda: validate_replace_operation(main_window)
        
        main_window.log_message("✅ Replace functions integrated")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Failed to integrate replace functions: {str(e)}")
        return False