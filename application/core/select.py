#this belongs in Core/select.py - Version: 1
# X-Seti - September11 2025 - IMG Factory 1.5 - Selection Functions

"""
Selection Functions - Table selection operations and entry management
Handles select all, invert selection, select by type, select by pattern, etc.
"""

import os
from typing import Optional, List, Dict, Any, Set
from PyQt6.QtWidgets import QTableWidget
from PyQt6.QtCore import Qt

# Import from new structure
from application.core.rw_versions import detect_rw_file_format, get_rw_version_name, is_valid_rw_version
from shared.progress_functions import show_progress, update_progress, hide_progress

##Methods list -
# select_all_entries
# select_none_entries
# invert_selection
# select_by_type
# select_by_name_pattern
# select_by_rw_version
# get_selected_entries
# get_selection_info
# _get_table_widget
# _update_selection_status
# integrate_selection_functions

def select_all_entries(main_window) -> int: #vers 1
    """Select all entries in the table
    
    Args:
        main_window: Main window instance
        
    Returns:
        int: Number of entries selected
    """
    try:
        table = _get_table_widget(main_window)
        if not table:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("❌ No table widget available")
            return 0

        # Select all rows
        table.selectAll()
        
        selected_count = table.rowCount()
        _update_selection_status(main_window, f"Selected all {selected_count} entries")
        
        return selected_count

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Select all error: {str(e)}")
        return 0

def select_none_entries(main_window) -> int: #vers 1
    """Clear all selections in the table
    
    Args:
        main_window: Main window instance
        
    Returns:
        int: Number of entries that were previously selected
    """
    try:
        table = _get_table_widget(main_window)
        if not table:
            return 0

        # Get current selection count
        selected_items = table.selectedItems()
        selected_rows = set(item.row() for item in selected_items)
        previous_count = len(selected_rows)

        # Clear selection
        table.clearSelection()
        
        _update_selection_status(main_window, "Selection cleared")
        
        return previous_count

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Clear selection error: {str(e)}")
        return 0

def invert_selection(main_window) -> int: #vers 1
    """Invert current selection in the table
    
    Args:
        main_window: Main window instance
        
    Returns:
        int: Number of entries selected after inversion
    """
    try:
        table = _get_table_widget(main_window)
        if not table:
            return 0

        # Get currently selected rows
        selected_items = table.selectedItems()
        selected_rows = set(item.row() for item in selected_items)
        
        # Clear current selection
        table.clearSelection()
        
        # Select all rows that weren't previously selected
        new_selection_count = 0
        for row in range(table.rowCount()):
            if row not in selected_rows:
                table.selectRow(row)
                new_selection_count += 1

        _update_selection_status(main_window, f"Selection inverted: {new_selection_count} entries selected")
        
        return new_selection_count

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Invert selection error: {str(e)}")
        return 0

def select_by_type(main_window, file_types: List[str], add_to_selection: bool = False) -> int: #vers 1
    """Select entries by file type
    
    Args:
        main_window: Main window instance
        file_types: List of file extensions to select (e.g., ['dff', 'txd'])
        add_to_selection: Whether to add to current selection or replace it
        
    Returns:
        int: Number of entries selected
    """
    try:
        table = _get_table_widget(main_window)
        if not table:
            return 0

        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            return 0

        entries = main_window.current_img.entries
        if not entries:
            return 0

        # Convert types to lowercase for comparison
        file_types_lower = [ft.lower() for ft in file_types]

        # Clear current selection if not adding
        if not add_to_selection:
            table.clearSelection()

        selected_count = 0
        
        for row, entry in enumerate(entries):
            if row >= table.rowCount():
                break
                
            entry_ext = os.path.splitext(entry.name)[1].lower().lstrip('.')
            if entry_ext in file_types_lower:
                table.selectRow(row)
                selected_count += 1

        action = "Added to selection" if add_to_selection else "Selected"
        _update_selection_status(main_window, f"{action}: {selected_count} {', '.join(file_types)} files")
        
        return selected_count

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Select by type error: {str(e)}")
        return 0

def select_by_name_pattern(main_window, pattern: str, case_sensitive: bool = False, 
                          add_to_selection: bool = False) -> int: #vers 1
    """Select entries by name pattern
    
    Args:
        main_window: Main window instance
        pattern: Name pattern to match
        case_sensitive: Whether pattern matching is case sensitive
        add_to_selection: Whether to add to current selection or replace it
        
    Returns:
        int: Number of entries selected
    """
    try:
        table = _get_table_widget(main_window)
        if not table:
            return 0

        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            return 0

        entries = main_window.current_img.entries
        if not entries:
            return 0

        # Prepare pattern for comparison
        search_pattern = pattern if case_sensitive else pattern.lower()

        # Clear current selection if not adding
        if not add_to_selection:
            table.clearSelection()

        selected_count = 0
        
        for row, entry in enumerate(entries):
            if row >= table.rowCount():
                break
                
            entry_name = entry.name if case_sensitive else entry.name.lower()
            if search_pattern in entry_name:
                table.selectRow(row)
                selected_count += 1

        action = "Added to selection" if add_to_selection else "Selected"
        _update_selection_status(main_window, f"{action}: {selected_count} entries matching '{pattern}'")
        
        return selected_count

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Select by pattern error: {str(e)}")
        return 0

def select_by_rw_version(main_window, rw_versions: List[str], add_to_selection: bool = False) -> int: #vers 1
    """Select entries by RenderWare version
    
    Args:
        main_window: Main window instance
        rw_versions: List of RW versions to select (e.g., ['3.4.0.3', 'SA Mobile'])
        add_to_selection: Whether to add to current selection or replace it
        
    Returns:
        int: Number of entries selected
    """
    try:
        table = _get_table_widget(main_window)
        if not table:
            return 0

        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            return 0

        entries = main_window.current_img.entries
        if not entries:
            return 0

        # Clear current selection if not adding
        if not add_to_selection:
            table.clearSelection()

        selected_count = 0
        
        # Show progress for RW detection
        show_progress(main_window, 0, "Analyzing RW versions...")
        
        for i, entry in enumerate(entries):
            if i >= table.rowCount():
                break
            
            # Update progress
            if i % 10 == 0:  # Update every 10 entries
                progress = int((i / len(entries)) * 100)
                update_progress(main_window, progress, f"Analyzing {entry.name}...")
            
            try:
                # Get entry data for RW detection
                entry_data = entry.get_data()
                if entry_data and len(entry_data) >= 12:
                    file_format, version_desc, version_value = detect_rw_file_format(entry_data, entry.name)
                    
                    # Check if this version matches our criteria
                    if version_desc in rw_versions or str(version_value) in rw_versions:
                        table.selectRow(i)
                        selected_count += 1
                        
            except Exception:
                continue  # Skip entries we can't analyze

        hide_progress(main_window)
        
        action = "Added to selection" if add_to_selection else "Selected"
        _update_selection_status(main_window, f"{action}: {selected_count} entries with RW versions {', '.join(rw_versions)}")
        
        return selected_count

    except Exception as e:
        hide_progress(main_window)
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Select by RW version error: {str(e)}")
        return 0

def get_selected_entries(main_window) -> List: #vers 1
    """Get list of currently selected entries
    
    Args:
        main_window: Main window instance
        
    Returns:
        List: Selected entry objects
    """
    try:
        selected_entries = []

        # Method 1: Use IMG Editor Tool adapter
        if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'img_editor_tool'):
            adapter = main_window.gui_layout.img_editor_tool.get_adapter()
            if hasattr(adapter, 'selected_entries'):
                selected_entries = adapter.selected_entries

        # Method 2: Get from table selection
        elif hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'table'):
            table = main_window.gui_layout.table
            selected_rows = set()
            
            for item in table.selectedItems():
                selected_rows.add(item.row())
            
            if selected_rows and hasattr(main_window, 'current_img'):
                img_entries = main_window.current_img.entries
                for row in selected_rows:
                    if row < len(img_entries):
                        selected_entries.append(img_entries[row])

        return selected_entries

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Error getting selected entries: {str(e)}")
        return []

def get_selection_info(main_window) -> Dict[str, Any]: #vers 1
    """Get detailed information about current selection
    
    Args:
        main_window: Main window instance
        
    Returns:
        Dict: Selection information including counts, types, sizes, etc.
    """
    try:
        selected_entries = get_selected_entries(main_window)
        
        info = {
            'total_selected': len(selected_entries),
            'total_size': 0,
            'file_types': {},
            'rw_versions': {},
            'entries': []
        }

        if not selected_entries:
            return info

        # Analyze selected entries
        for entry in selected_entries:
            try:
                # Get entry data
                entry_data = entry.get_data()
                if not entry_data:
                    continue

                entry_size = len(entry_data)
                entry_ext = os.path.splitext(entry.name)[1].upper().lstrip('.')

                # Detect RW version
                file_format, version_desc, version_value = detect_rw_file_format(entry_data, entry.name)

                entry_info = {
                    'name': entry.name,
                    'size': entry_size,
                    'type': entry_ext,
                    'rw_format': file_format,
                    'rw_version': version_desc,
                    'is_valid_rw': is_valid_rw_version(version_value) if version_value else False
                }

                info['entries'].append(entry_info)
                info['total_size'] += entry_size

                # Track file types
                if entry_ext not in info['file_types']:
                    info['file_types'][entry_ext] = 0
                info['file_types'][entry_ext] += 1

                # Track RW versions
                if version_desc not in info['rw_versions']:
                    info['rw_versions'][version_desc] = 0
                info['rw_versions'][version_desc] += 1

            except Exception:
                continue

        return info

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Selection info error: {str(e)}")
        return {'total_selected': 0, 'total_size': 0, 'file_types': {}, 'rw_versions': {}, 'entries': []}

def _get_table_widget(main_window) -> Optional[QTableWidget]: #vers 1
    """Get table widget from main window"""
    try:
        if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'table'):
            return main_window.gui_layout.table
        return None
    except Exception:
        return None

def _update_selection_status(main_window, message: str): #vers 1
    """Update selection status message"""
    try:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"🔍 {message}")
        
        # Also update status bar if available
        if hasattr(main_window, 'show_status'):
            main_window.show_status(message, 3000)  # Show for 3 seconds
            
    except Exception:
        pass  # Don't fail selection operations on status update errors

def integrate_selection_functions(main_window) -> bool: #vers 1
    """Integrate selection functions into main window"""
    try:
        # Add selection methods
        main_window.select_all_entries = lambda: select_all_entries(main_window)
        main_window.select_none_entries = lambda: select_none_entries(main_window)
        main_window.invert_selection = lambda: invert_selection(main_window)
        main_window.select_by_type = lambda file_types, add_to_selection=False: select_by_type(main_window, file_types, add_to_selection)
        main_window.select_by_name_pattern = lambda pattern, case_sensitive=False, add_to_selection=False: select_by_name_pattern(main_window, pattern, case_sensitive, add_to_selection)
        main_window.select_by_rw_version = lambda rw_versions, add_to_selection=False: select_by_rw_version(main_window, rw_versions, add_to_selection)
        main_window.get_selected_entries = lambda: get_selected_entries(main_window)
        main_window.get_selection_info = lambda: get_selection_info(main_window)

        # Aliases for backward compatibility
        main_window.select_all = main_window.select_all_entries
        main_window.select_inverse = main_window.invert_selection
        main_window.clear_selection = main_window.select_none_entries

        if hasattr(main_window, 'log_message'):
            main_window.log_message("✅ Selection functions integrated")
            main_window.log_message("   • Select all/none/invert")
            main_window.log_message("   • Select by type/pattern/RW version")
            main_window.log_message("   • Selection info and analysis")

        return True

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Selection integration failed: {str(e)}")
        return False

# Export functions
__all__ = [
    'select_all_entries',
    'select_none_entries',
    'invert_selection',
    'select_by_type',
    'select_by_name_pattern',
    'select_by_rw_version',
    'get_selected_entries',
    'get_selection_info',
    'integrate_selection_functions'
]
