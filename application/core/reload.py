#this belongs in Core/reload.py - Version: 1
# X-Seti - September11 2025 - IMG Factory 1.5 - Reload Operations

"""
Reload Operations - Handles reloading current IMG file and refreshing table display
Core operations for refreshing file data and updating UI components
"""

import os
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import Qt

##Methods list -
# reload_table
# reload_current_file
# refresh_table_display
# reload_img_from_disk
# validate_reload_operation
# _backup_current_state
# _restore_selection_after_reload
# update_table_after_reload

def reload_table(main_window) -> bool: #vers 1
    """Reload the current IMG file and refresh table display (main function)"""
    try:
        if not validate_reload_operation(main_window):
            return False

        main_window.log_message("🔄 Reloading current file...")
        
        # Get current tab and IMG file
        current_tab = main_window.tab_widget.currentWidget()
        if not current_tab or not hasattr(current_tab, 'img_file'):
            main_window.log_message("❌ No active IMG file to reload")
            return False

        img_file = current_tab.img_file
        file_path = getattr(img_file, 'file_path', None)
        
        if not file_path or not os.path.exists(file_path):
            main_window.log_message("❌ IMG file path not found or file doesn't exist")
            return False

        # Check for unsaved changes
        if hasattr(img_file, 'modified') and img_file.modified:
            reply = QMessageBox.question(
                main_window,
                "Unsaved Changes",
                f"The file '{os.path.basename(file_path)}' has unsaved changes.\n\n"
                "Reloading will discard these changes. Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply != QMessageBox.StandardButton.Yes:
                main_window.log_message("❌ Reload cancelled by user")
                return False

        # Backup current selection state
        selected_entries = _backup_current_state(main_window)

        # Reload IMG from disk
        success = reload_img_from_disk(main_window, img_file, file_path)
        
        if success:
            # Update table display
            refresh_table_display(main_window)
            
            # Restore selection if possible
            _restore_selection_after_reload(main_window, selected_entries)
            
            main_window.log_message(f"✅ Reloaded: {os.path.basename(file_path)}")
            return True
        else:
            main_window.log_message(f"❌ Failed to reload: {os.path.basename(file_path)}")
            return False

    except Exception as e:
        main_window.log_message(f"❌ Reload operation failed: {str(e)}")
        return False


def reload_current_file(main_window) -> bool: #vers 1
    """Alias for reload_table - maintains compatibility"""
    return reload_table(main_window)


def refresh_table_display(main_window) -> bool: #vers 1
    """Refresh the table display with current IMG data"""
    try:
        if not hasattr(main_window, 'gui_layout') or not hasattr(main_window.gui_layout, 'table'):
            main_window.log_message("❌ No table widget available")
            return False

        current_tab = main_window.tab_widget.currentWidget()
        if not current_tab or not hasattr(current_tab, 'img_file'):
            # Clear table if no IMG file
            main_window.gui_layout.table.setRowCount(0)
            return True

        img_file = current_tab.img_file
        
        # Use existing table population system
        if hasattr(main_window, 'populate_img_table'):
            return main_window.populate_img_table(img_file)
        else:
            # Fallback to basic table update
            return update_table_after_reload(main_window, img_file)

    except Exception as e:
        main_window.log_message(f"❌ Table refresh failed: {str(e)}")
        return False


def reload_img_from_disk(main_window, img_file, file_path: str) -> bool: #vers 1
    """Reload IMG file data from disk"""
    try:
        # Close current file handle if open
        if hasattr(img_file, 'file_handle') and img_file.file_handle:
            try:
                img_file.file_handle.close()
                img_file.file_handle = None
            except:
                pass

        # Clear existing data
        if hasattr(img_file, 'entries'):
            img_file.entries.clear()
        
        if hasattr(img_file, 'deleted_entries'):
            img_file.deleted_entries.clear()

        # Reset modification flag
        if hasattr(img_file, 'modified'):
            img_file.modified = False

        # Reload file using existing IMG loading system
        if hasattr(main_window, 'load_img_file'):
            # Use main window's load function
            success = main_window.load_img_file(file_path, img_file)
        elif hasattr(img_file, 'load_from_file'):
            # Use IMG file's own load method
            success = img_file.load_from_file(file_path)
        else:
            # Fallback to basic loading
            success = _basic_img_reload(main_window, img_file, file_path)

        if success:
            # Update file path reference
            img_file.file_path = file_path
            return True
        else:
            main_window.log_message(f"❌ Failed to reload IMG data from: {file_path}")
            return False

    except Exception as e:
        main_window.log_message(f"❌ IMG reload from disk failed: {str(e)}")
        return False


def _basic_img_reload(main_window, img_file, file_path: str) -> bool: #vers 1
    """Basic IMG file reload fallback"""
    try:
        # Import IMG core classes for basic loading
        from methods.img_core_classes import IMGFile
        
        # Create temporary IMG object to load data
        temp_img = IMGFile()
        success = temp_img.load_from_file(file_path)
        
        if success:
            # Copy data to existing img_file object
            img_file.entries = temp_img.entries
            img_file.version = getattr(temp_img, 'version', None)
            img_file.file_path = file_path
            return True
        else:
            return False

    except Exception as e:
        main_window.log_message(f"❌ Basic IMG reload failed: {str(e)}")
        return False


def validate_reload_operation(main_window) -> bool: #vers 1
    """Validate if reload operation can proceed"""
    try:
        if not hasattr(main_window, 'tab_widget') or main_window.tab_widget.count() == 0:
            main_window.log_message("❌ No IMG files to reload")
            return False

        # Check if any critical operations are running
        if hasattr(main_window, 'progress_dialog') and main_window.progress_dialog.isVisible():
            QMessageBox.warning(
                main_window,
                "Operation in Progress",
                "Cannot reload while an operation is in progress.\n"
                "Please wait for the current operation to complete."
            )
            return False

        return True

    except Exception as e:
        main_window.log_message(f"❌ Reload validation failed: {str(e)}")
        return False


def _backup_current_state(main_window) -> list: #vers 1
    """Backup current selection state before reload"""
    try:
        selected_entries = []
        
        if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'table'):
            table = main_window.gui_layout.table
            selected_rows = set()
            
            for item in table.selectedItems():
                selected_rows.add(item.row())
            
            # Get entry names from selected rows
            for row in selected_rows:
                if row < table.rowCount():
                    name_item = table.item(row, 0)  # Assuming name is in first column
                    if name_item:
                        selected_entries.append(name_item.text())

        return selected_entries

    except Exception as e:
        main_window.log_message(f"⚠️ Failed to backup selection state: {str(e)}")
        return []


def _restore_selection_after_reload(main_window, selected_entries: list) -> bool: #vers 1
    """Restore selection state after reload"""
    try:
        if not selected_entries:
            return True

        if not hasattr(main_window, 'gui_layout') or not hasattr(main_window.gui_layout, 'table'):
            return False

        table = main_window.gui_layout.table
        restored_count = 0

        # Find and select matching entries
        for row in range(table.rowCount()):
            name_item = table.item(row, 0)
            if name_item and name_item.text() in selected_entries:
                table.selectRow(row)
                restored_count += 1

        if restored_count > 0:
            main_window.log_message(f"🔄 Restored selection for {restored_count} entries")

        return True

    except Exception as e:
        main_window.log_message(f"⚠️ Failed to restore selection: {str(e)}")
        return False


def update_table_after_reload(main_window, img_file) -> bool: #vers 1
    """Update table with IMG file data after reload"""
    try:
        if not hasattr(main_window, 'gui_layout') or not hasattr(main_window.gui_layout, 'table'):
            return False

        table = main_window.gui_layout.table
        
        if not hasattr(img_file, 'entries'):
            table.setRowCount(0)
            return True

        entries = img_file.entries
        table.setRowCount(len(entries))

        # Basic table population
        for row, entry in enumerate(entries):
            try:
                # Name column
                name_item = table.item(row, 0)
                if not name_item:
                    from PyQt6.QtWidgets import QTableWidgetItem
                    name_item = QTableWidgetItem()
                    table.setItem(row, 0, name_item)
                name_item.setText(getattr(entry, 'name', f'Entry_{row}'))

                # Size column (if exists)
                if table.columnCount() > 1:
                    size_item = table.item(row, 1)
                    if not size_item:
                        from PyQt6.QtWidgets import QTableWidgetItem
                        size_item = QTableWidgetItem()
                        table.setItem(row, 1, size_item)
                    
                    size = getattr(entry, 'size', 0)
                    if hasattr(main_window, 'format_file_size'):
                        size_text = main_window.format_file_size(size)
                    else:
                        size_text = f"{size:,} bytes"
                    size_item.setText(size_text)

            except Exception as e:
                main_window.log_message(f"⚠️ Failed to update row {row}: {str(e)}")

        # Update info bar
        if hasattr(main_window, 'info_bar'):
            main_window.info_bar.setText(f"Entries: {len(entries)}")

        return True

    except Exception as e:
        main_window.log_message(f"❌ Table update failed: {str(e)}")
        return False


def integrate_reload_functions(main_window) -> bool: #vers 1
    """Integrate reload functions into main window"""
    try:
        # Add reload functions to main window
        main_window.reload_table = lambda: reload_table(main_window)
        main_window.reload_current_file = lambda: reload_current_file(main_window)
        main_window.refresh_table_display = lambda: refresh_table_display(main_window)
        main_window.reload_img_from_disk = lambda img_file, file_path: reload_img_from_disk(main_window, img_file, file_path)
        
        main_window.log_message("✅ Reload functions integrated")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Failed to integrate reload functions: {str(e)}")
        return False