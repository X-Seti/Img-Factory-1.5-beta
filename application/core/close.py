#this belongs in Core/close.py - Version: 1
# X-Seti - September11 2025 - IMG Factory 1.5 - Close Operations

"""
Close Operations - Handles closing IMG files and cleaning up resources
Core operations for single IMG close and close all functionality
"""

import os
from typing import Optional, List
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import Qt

##Methods list -
# close_img_file
# close_all_img
# cleanup_img_resources
# save_before_close_dialog
# _close_single_img_tab
# _update_ui_after_close
# validate_close_operation

def close_img_file(main_window) -> bool: #vers 1
    """Close the currently active IMG file"""
    try:
        if not hasattr(main_window, 'tab_widget') or main_window.tab_widget.count() == 0:
            main_window.log_message("❌ No IMG files to close")
            return False

        current_index = main_window.tab_widget.currentIndex()
        if current_index < 0:
            main_window.log_message("❌ No active tab to close")
            return False

        tab_data = main_window.tab_widget.widget(current_index)
        tab_title = main_window.tab_widget.tabText(current_index)
        
        # Check if file has unsaved changes
        if hasattr(tab_data, 'img_file') and hasattr(tab_data.img_file, 'modified'):
            if tab_data.img_file.modified:
                save_choice = save_before_close_dialog(main_window, tab_title)
                if save_choice == QMessageBox.StandardButton.Cancel:
                    return False
                elif save_choice == QMessageBox.StandardButton.Save:
                    # Save the file before closing
                    from application.core.save_entry import save_img_entry
                    if not save_img_entry(main_window):
                        return False

        # Close the specific tab
        success = _close_single_img_tab(main_window, current_index)
        
        if success:
            main_window.log_message(f"✅ Closed IMG: {tab_title}")
            _update_ui_after_close(main_window)
            return True
        else:
            main_window.log_message(f"❌ Failed to close IMG: {tab_title}")
            return False

    except Exception as e:
        main_window.log_message(f"❌ Close operation failed: {str(e)}")
        return False


def close_all_img(main_window) -> bool: #vers 1
    """Close all open IMG files"""
    try:
        if not hasattr(main_window, 'tab_widget') or main_window.tab_widget.count() == 0:
            main_window.log_message("ℹ️ No IMG files to close")
            return True

        total_tabs = main_window.tab_widget.count()
        closed_count = 0
        
        # Check for unsaved changes across all tabs
        unsaved_tabs = []
        for i in range(total_tabs):
            tab_data = main_window.tab_widget.widget(i)
            tab_title = main_window.tab_widget.tabText(i)
            if hasattr(tab_data, 'img_file') and hasattr(tab_data.img_file, 'modified'):
                if tab_data.img_file.modified:
                    unsaved_tabs.append((i, tab_title))

        # If there are unsaved changes, ask user
        if unsaved_tabs:
            reply = QMessageBox.question(
                main_window,
                "Unsaved Changes",
                f"There are {len(unsaved_tabs)} file(s) with unsaved changes:\n"
                + "\n".join([f"• {title}" for _, title in unsaved_tabs]) +
                "\n\nDo you want to close all files anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply != QMessageBox.StandardButton.Yes:
                return False

        # Close all tabs (from last to first to avoid index shifting)
        for i in range(total_tabs - 1, -1, -1):
            try:
                success = _close_single_img_tab(main_window, i)
                if success:
                    closed_count += 1
            except Exception as e:
                main_window.log_message(f"⚠️ Failed to close tab {i}: {str(e)}")

        # Update UI after closing all
        _update_ui_after_close(main_window)
        
        main_window.log_message(f"✅ Closed {closed_count} IMG file(s)")
        return closed_count == total_tabs

    except Exception as e:
        main_window.log_message(f"❌ Close all operation failed: {str(e)}")
        return False


def save_before_close_dialog(main_window, filename: str) -> QMessageBox.StandardButton: #vers 1
    """Show save before close dialog"""
    try:
        reply = QMessageBox.question(
            main_window,
            "Unsaved Changes",
            f"The file '{filename}' has unsaved changes.\n\n"
            "Do you want to save before closing?",
            QMessageBox.StandardButton.Save | 
            QMessageBox.StandardButton.Discard | 
            QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Save
        )
        return reply

    except Exception as e:
        main_window.log_message(f"❌ Save dialog failed: {str(e)}")
        return QMessageBox.StandardButton.Cancel


def _close_single_img_tab(main_window, tab_index: int) -> bool: #vers 1
    """Close a single IMG tab and cleanup resources"""
    try:
        if tab_index < 0 or tab_index >= main_window.tab_widget.count():
            return False

        tab_data = main_window.tab_widget.widget(tab_index)
        
        # Cleanup IMG file resources
        if hasattr(tab_data, 'img_file'):
            cleanup_img_resources(main_window, tab_data.img_file)

        # Remove the tab
        main_window.tab_widget.removeTab(tab_index)
        
        return True

    except Exception as e:
        main_window.log_message(f"❌ Failed to close tab {tab_index}: {str(e)}")
        return False


def cleanup_img_resources(main_window, img_file) -> bool: #vers 1
    """Cleanup resources associated with an IMG file"""
    try:
        if not img_file:
            return True

        # Close file handle if open
        if hasattr(img_file, 'file_handle') and img_file.file_handle:
            try:
                img_file.file_handle.close()
                img_file.file_handle = None
            except:
                pass

        # Clear file data
        if hasattr(img_file, 'entries'):
            img_file.entries.clear()
        
        if hasattr(img_file, 'deleted_entries'):
            img_file.deleted_entries.clear()

        # Reset modification flag
        if hasattr(img_file, 'modified'):
            img_file.modified = False

        return True

    except Exception as e:
        main_window.log_message(f"⚠️ Resource cleanup failed: {str(e)}")
        return False


def _update_ui_after_close(main_window) -> bool: #vers 1
    """Update UI elements after closing IMG files"""
    try:
        # Update window title
        if main_window.tab_widget.count() == 0:
            main_window.setWindowTitle("IMG Factory 1.5")
            
            # Clear table if no tabs remain
            if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'table'):
                main_window.gui_layout.table.setRowCount(0)
                
            # Update info bar
            if hasattr(main_window, 'info_bar'):
                main_window.info_bar.setText("No IMG file loaded")
        else:
            # Switch to remaining tab and refresh
            current_tab = main_window.tab_widget.currentWidget()
            if current_tab and hasattr(current_tab, 'img_file'):
                # Refresh table for current tab
                if hasattr(main_window, 'refresh_table'):
                    main_window.refresh_table()

        return True

    except Exception as e:
        main_window.log_message(f"⚠️ UI update after close failed: {str(e)}")
        return False


def validate_close_operation(main_window) -> bool: #vers 1
    """Validate if close operation is safe to perform"""
    try:
        if not hasattr(main_window, 'tab_widget'):
            return False

        # Check if any critical operations are running
        if hasattr(main_window, 'progress_dialog') and main_window.progress_dialog.isVisible():
            QMessageBox.warning(
                main_window,
                "Operation in Progress",
                "Cannot close IMG files while an operation is in progress.\n"
                "Please wait for the current operation to complete."
            )
            return False

        return True

    except Exception as e:
        main_window.log_message(f"❌ Close validation failed: {str(e)}")
        return False


def integrate_close_functions(main_window) -> bool: #vers 1
    """Integrate close functions into main window"""
    try:
        # Add close functions to main window
        main_window.close_img_file = lambda: close_img_file(main_window)
        main_window.close_all_img = lambda: close_all_img(main_window)
        main_window.cleanup_img_resources = lambda img_file: cleanup_img_resources(main_window, img_file)
        main_window.validate_close_operation = lambda: validate_close_operation(main_window)
        
        main_window.log_message("✅ Close functions integrated")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Failed to integrate close functions: {str(e)}")
        return False