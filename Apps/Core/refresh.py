#this belongs in Core/refresh.py - Version: 1
# X-Seti - September11 2025 - IMG Factory 1.5 - Core Refresh Functions

"""
Core Refresh Functions - Table and UI refresh operations
Handles refreshing IMG/COL tables, UI updates, and data synchronization
"""

import os
from typing import Optional, List, Dict, Any

# Import from new structure
from Shared.populate_img_table import populate_img_table_enhanced, refresh_table
from Shared.populate_col_table import populate_col_table_enhanced
from Shared.progress_functions import show_progress, hide_progress

##Methods list -
# refresh_current_table
# refresh_img_table
# refresh_col_table
# force_table_refresh
# refresh_ui_status
# refresh_file_info
# _detect_current_file_type
# _update_table_headers
# integrate_refresh_functions

def refresh_current_table(main_window) -> bool: #vers 1
    """Refresh current table based on loaded file type
    
    Args:
        main_window: Main window instance
        
    Returns:
        bool: True if refresh successful
    """
    try:
        # Detect current file type
        file_type = _detect_current_file_type(main_window)
        
        if file_type == 'IMG':
            return refresh_img_table(main_window)
        elif file_type == 'COL':
            return refresh_col_table(main_window)
        else:
            # No file loaded - clear table
            if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'table'):
                main_window.gui_layout.table.setRowCount(0)
                if hasattr(main_window, 'log_message'):
                    main_window.log_message("📋 Table cleared - no file loaded")
            return True

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Table refresh error: {str(e)}")
        return False

def refresh_img_table(main_window) -> bool: #vers 1
    """Refresh IMG table with current IMG data
    
    Args:
        main_window: Main window instance
        
    Returns:
        bool: True if refresh successful
    """
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("⚠️ No IMG file to refresh")
            return False

        img_file = main_window.current_img
        
        if not hasattr(img_file, 'entries') or not img_file.entries:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("⚠️ No IMG entries to refresh")
            # Clear table for empty IMG
            if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'table'):
                main_window.gui_layout.table.setRowCount(0)
            return True

        # Show progress for large IMG files
        entry_count = len(img_file.entries)
        if entry_count > 100:
            show_progress(main_window, 0, f"Refreshing IMG table ({entry_count} entries)...")

        # Use existing table population methods in order of preference
        success = False
        
        # Method 1: Use refresh_table function if available
        if hasattr(main_window, 'refresh_table'):
            try:
                main_window.refresh_table()
                success = True
            except Exception:
                pass

        # Method 2: Use populate_img_table_enhanced if available
        if not success and hasattr(main_window, 'populate_img_table_enhanced'):
            try:
                main_window.populate_img_table_enhanced(img_file)
                success = True
            except Exception:
                pass

        # Method 3: Use Shared populate function directly
        if not success:
            try:
                populate_img_table_enhanced(main_window, img_file)
                success = True
            except Exception:
                pass

        # Method 4: Force table refresh
        if not success:
            success = force_table_refresh(main_window, img_file, 'IMG')

        if entry_count > 100:
            hide_progress(main_window)

        if success:
            # Update UI status
            refresh_ui_status(main_window)
            refresh_file_info(main_window)
            
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"🔄 IMG table refreshed ({entry_count} entries)")
        else:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("❌ Failed to refresh IMG table")

        return success

    except Exception as e:
        hide_progress(main_window)
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ IMG table refresh error: {str(e)}")
        return False

def refresh_col_table(main_window) -> bool: #vers 1
    """Refresh COL table with current COL data
    
    Args:
        main_window: Main window instance
        
    Returns:
        bool: True if refresh successful
    """
    try:
        if not hasattr(main_window, 'current_col') or not main_window.current_col:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("⚠️ No COL file to refresh")
            return False

        col_file = main_window.current_col
        
        if not hasattr(col_file, 'models') or not col_file.models:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("⚠️ No COL models to refresh")
            # Clear table for empty COL
            if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'table'):
                main_window.gui_layout.table.setRowCount(0)
            return True

        model_count = len(col_file.models)
        
        # Show progress for large COL files
        if model_count > 50:
            show_progress(main_window, 0, f"Refreshing COL table ({model_count} models)...")

        # Use existing COL table population methods
        success = False
        
        # Method 1: Use populate_col_table_enhanced if available
        if hasattr(main_window, 'populate_col_table_enhanced'):
            try:
                main_window.populate_col_table_enhanced(col_file)
                success = True
            except Exception:
                pass

        # Method 2: Use Shared populate function directly
        if not success:
            try:
                populate_col_table_enhanced(main_window, col_file)
                success = True
            except Exception:
                pass

        # Method 3: Force table refresh
        if not success:
            success = force_table_refresh(main_window, col_file, 'COL')

        if model_count > 50:
            hide_progress(main_window)

        if success:
            # Update UI status
            refresh_ui_status(main_window)
            refresh_file_info(main_window)
            
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"🔄 COL table refreshed ({model_count} models)")
        else:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("❌ Failed to refresh COL table")

        return success

    except Exception as e:
        hide_progress(main_window)
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ COL table refresh error: {str(e)}")
        return False

def force_table_refresh(main_window, file_object, file_type: str) -> bool: #vers 1
    """Force table refresh by directly updating table widget
    
    Args:
        main_window: Main window instance
        file_object: IMG or COL file object
        file_type: 'IMG' or 'COL'
        
    Returns:
        bool: True if refresh successful
    """
    try:
        if not hasattr(main_window, 'gui_layout') or not hasattr(main_window.gui_layout, 'table'):
            return False

        table = main_window.gui_layout.table
        
        # Clear existing data
        table.setRowCount(0)
        table.clearContents()

        if file_type == 'IMG':
            # Set IMG headers
            headers = ["Index", "Name", "Offset", "Size", "Data Size", "Type", "RW Ver", "Info"]
            table.setColumnCount(len(headers))
            table.setHorizontalHeaderLabels(headers)
            
            # Populate with IMG entries
            if hasattr(file_object, 'entries') and file_object.entries:
                from PyQt6.QtWidgets import QTableWidgetItem
                table.setRowCount(len(file_object.entries))
                
                for row, entry in enumerate(file_object.entries):
                    # Basic entry info
                    table.setItem(row, 0, QTableWidgetItem(str(row)))
                    table.setItem(row, 1, QTableWidgetItem(entry.name))
                    table.setItem(row, 2, QTableWidgetItem(f"0x{getattr(entry, 'offset', 0):08X}"))
                    table.setItem(row, 3, QTableWidgetItem(str(getattr(entry, 'size', 0))))
                    table.setItem(row, 4, QTableWidgetItem(str(getattr(entry, 'uncompressed_size', getattr(entry, 'size', 0)))))
                    
                    # File type
                    file_ext = os.path.splitext(entry.name)[1].upper().lstrip('.')
                    table.setItem(row, 5, QTableWidgetItem(file_ext))
                    
                    # RW version (simplified)
                    table.setItem(row, 6, QTableWidgetItem(getattr(entry, 'rw_version_name', 'Unknown')))
                    table.setItem(row, 7, QTableWidgetItem(""))

        elif file_type == 'COL':
            # Set COL headers
            headers = ["Model Name", "Type", "Version", "Size", "Spheres", "Boxes", "Faces", "Info"]
            table.setColumnCount(len(headers))
            table.setHorizontalHeaderLabels(headers)
            
            # Populate with COL models
            if hasattr(file_object, 'models') and file_object.models:
                from PyQt6.QtWidgets import QTableWidgetItem
                table.setRowCount(len(file_object.models))
                
                for row, model in enumerate(file_object.models):
                    table.setItem(row, 0, QTableWidgetItem(getattr(model, 'name', f'Model_{row}')))
                    table.setItem(row, 1, QTableWidgetItem('COL'))
                    table.setItem(row, 2, QTableWidgetItem(getattr(model, 'version', 'Unknown')))
                    table.setItem(row, 3, QTableWidgetItem(str(getattr(model, 'size', 0))))
                    table.setItem(row, 4, QTableWidgetItem(str(len(getattr(model, 'spheres', [])))))
                    table.setItem(row, 5, QTableWidgetItem(str(len(getattr(model, 'boxes', [])))))
                    table.setItem(row, 6, QTableWidgetItem(str(len(getattr(model, 'faces', [])))))
                    table.setItem(row, 7, QTableWidgetItem(""))

        # Update table headers
        _update_table_headers(main_window, file_type)
        
        return True

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Force refresh error: {str(e)}")
        return False

def refresh_ui_status(main_window): #vers 1
    """Refresh UI status elements"""
    try:
        # Update status bar if available
        if hasattr(main_window, 'update_img_status'):
            if hasattr(main_window, 'current_img') and main_window.current_img:
                img_file = main_window.current_img
                filename = os.path.basename(getattr(img_file, 'file_path', 'Unknown.img'))
                entry_count = len(getattr(img_file, 'entries', []))
                file_size = getattr(img_file, 'file_size', 0)
                
                main_window.update_img_status(
                    img_file=img_file,
                    filename=filename,
                    entry_count=entry_count,
                    file_size=file_size
                )
        
        # Update window title
        if hasattr(main_window, 'current_img') and main_window.current_img:
            filename = os.path.basename(getattr(main_window.current_img, 'file_path', 'Unknown.img'))
            main_window.setWindowTitle(f"IMG Factory 1.5 - {filename}")
        elif hasattr(main_window, 'current_col') and main_window.current_col:
            filename = os.path.basename(getattr(main_window.current_col, 'file_path', 'Unknown.col'))
            main_window.setWindowTitle(f"IMG Factory 1.5 - {filename}")
        else:
            main_window.setWindowTitle("IMG Factory 1.5")

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"⚠️ UI status refresh error: {str(e)}")

def refresh_file_info(main_window): #vers 1
    """Refresh file information displays"""
    try:
        # Update file info in GUI layout
        if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'update_img_info'):
            if hasattr(main_window, 'current_img') and main_window.current_img:
                entry_count = len(getattr(main_window.current_img, 'entries', []))
                main_window.gui_layout.update_img_info(f"IMG: {entry_count} entries")
            elif hasattr(main_window, 'current_col') and main_window.current_col:
                model_count = len(getattr(main_window.current_col, 'models', []))
                main_window.gui_layout.update_img_info(f"COL: {model_count} models")
            else:
                main_window.gui_layout.update_img_info("No file loaded")

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"⚠️ File info refresh error: {str(e)}")

def _detect_current_file_type(main_window) -> Optional[str]: #vers 1
    """Detect current loaded file type"""
    try:
        if hasattr(main_window, 'current_img') and main_window.current_img:
            return 'IMG'
        elif hasattr(main_window, 'current_col') and main_window.current_col:
            return 'COL'
        else:
            return None
    except Exception:
        return None

def _update_table_headers(main_window, file_type: str): #vers 1
    """Update table column headers and widths"""
    try:
        if not hasattr(main_window, 'gui_layout') or not hasattr(main_window.gui_layout, 'table'):
            return

        table = main_window.gui_layout.table

        if file_type == 'IMG':
            # Set IMG column widths
            table.setColumnWidth(0, 60)   # Index
            table.setColumnWidth(1, 200)  # Name
            table.setColumnWidth(2, 80)   # Offset
            table.setColumnWidth(3, 80)   # Size
            table.setColumnWidth(4, 80)   # Data Size
            table.setColumnWidth(5, 60)   # Type
            table.setColumnWidth(6, 80)   # RW Ver
            table.setColumnWidth(7, 100)  # Info

        elif file_type == 'COL':
            # Set COL column widths
            table.setColumnWidth(0, 200)  # Model Name
            table.setColumnWidth(1, 80)   # Type
            table.setColumnWidth(2, 80)   # Version
            table.setColumnWidth(3, 100)  # Size
            table.setColumnWidth(4, 80)   # Spheres
            table.setColumnWidth(5, 80)   # Boxes
            table.setColumnWidth(6, 80)   # Faces
            table.setColumnWidth(7, 150)  # Info

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"⚠️ Header update error: {str(e)}")

def integrate_refresh_functions(main_window) -> bool: #vers 1
    """Integrate refresh functions into main window"""
    try:
        # Add refresh methods
        main_window.refresh_current_table = lambda: refresh_current_table(main_window)
        main_window.refresh_img_table = lambda: refresh_img_table(main_window)
        main_window.refresh_col_table = lambda: refresh_col_table(main_window)
        main_window.force_table_refresh = lambda file_object, file_type: force_table_refresh(main_window, file_object, file_type)
        main_window.refresh_ui_status = lambda: refresh_ui_status(main_window)
        main_window.refresh_file_info = lambda: refresh_file_info(main_window)

        # Aliases for backward compatibility
        main_window.refresh_table = main_window.refresh_current_table
        main_window.update_table = main_window.refresh_current_table

        if hasattr(main_window, 'log_message'):
            main_window.log_message("✅ Refresh functions integrated")
            main_window.log_message("   • IMG/COL table refresh")
            main_window.log_message("   • UI status updates")
            main_window.log_message("   • File info updates")
            main_window.log_message("   • Force refresh capability")

        return True

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Refresh integration failed: {str(e)}")
        return False

# Export functions
__all__ = [
    'refresh_current_table',
    'refresh_img_table',
    'refresh_col_table',
    'force_table_refresh',
    'refresh_ui_status',
    'refresh_file_info',
    'integrate_refresh_functions'
]