#this belongs in Shared/inverse.py - Version: 1
# X-Seti - September11 2025 - IMG Factory 1.5 - Inverse Selection Functions

"""
Inverse Selection Functions - Advanced selection inversion operations
Handles inverting selection, conditional inversion, and smart selection patterns
"""

import os
from typing import Optional, List, Dict, Any, Set
from PyQt6.QtWidgets import QTableWidget, QMessageBox
from PyQt6.QtCore import Qt

# Import from new structure
from Core.rw_versions import detect_rw_file_format, get_rw_version_name, is_valid_rw_version
from Shared.progress_functions import show_progress, update_progress, hide_progress

##Methods list -
# invert_selection
# invert_selection_by_type
# invert_selection_by_pattern
# invert_selection_by_rw_version
# smart_invert_selection
# get_inversion_preview
# _get_table_widget
# _get_current_selection
# _update_selection_status
# integrate_inverse_functions

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
            if hasattr(main_window, 'log_message'):
                main_window.log_message("❌ No table widget available")
            return 0

        # Get currently selected rows
        current_selection = _get_current_selection(main_window)
        total_rows = table.rowCount()
        
        if total_rows == 0:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("⚠️ No entries to invert selection")
            return 0

        # Clear current selection
        table.clearSelection()
        
        # Select all rows that weren't previously selected
        new_selection_count = 0
        for row in range(total_rows):
            if row not in current_selection:
                table.selectRow(row)
                new_selection_count += 1

        _update_selection_status(main_window, f"Selection inverted: {new_selection_count} entries selected")
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"🔄 Selection inverted: {len(current_selection)} → {new_selection_count} entries")
        
        return new_selection_count

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Invert selection error: {str(e)}")
        return 0

def invert_selection_by_type(main_window, file_types: List[str]) -> int: #vers 1
    """Invert selection only for specific file types
    
    Args:
        main_window: Main window instance
        file_types: List of file extensions to consider for inversion
        
    Returns:
        int: Number of entries affected by inversion
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
        
        # Get currently selected rows
        current_selection = _get_current_selection(main_window)
        affected_count = 0
        
        for row, entry in enumerate(entries):
            if row >= table.rowCount():
                break
                
            entry_ext = os.path.splitext(entry.name)[1].lower().lstrip('.')
            
            # Only process entries of specified types
            if entry_ext in file_types_lower:
                if row in current_selection:
                    # Was selected, now deselect
                    table.selectRow(row)  # This actually toggles in this context
                    table.clearSelection()
                    affected_count += 1
                else:
                    # Was not selected, now select
                    table.selectRow(row)
                    affected_count += 1

        _update_selection_status(main_window, f"Inverted selection for {', '.join(file_types)}: {affected_count} entries affected")
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"🔄 Inverted selection for {', '.join(file_types)}: {affected_count} entries")
        
        return affected_count

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Invert by type error: {str(e)}")
        return 0

def invert_selection_by_pattern(main_window, pattern: str, case_sensitive: bool = False) -> int: #vers 1
    """Invert selection only for entries matching name pattern
    
    Args:
        main_window: Main window instance
        pattern: Name pattern to match
        case_sensitive: Whether pattern matching is case sensitive
        
    Returns:
        int: Number of entries affected by inversion
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
        
        # Get currently selected rows
        current_selection = _get_current_selection(main_window)
        affected_count = 0
        new_selection = set(current_selection)  # Start with current selection
        
        for row, entry in enumerate(entries):
            if row >= table.rowCount():
                break
                
            entry_name = entry.name if case_sensitive else entry.name.lower()
            
            # Only process entries matching the pattern
            if search_pattern in entry_name:
                if row in current_selection:
                    # Was selected, now deselect
                    new_selection.discard(row)
                    affected_count += 1
                else:
                    # Was not selected, now select
                    new_selection.add(row)
                    affected_count += 1

        # Apply new selection
        table.clearSelection()
        for row in new_selection:
            table.selectRow(row)

        _update_selection_status(main_window, f"Inverted selection for pattern '{pattern}': {affected_count} entries affected")
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"🔄 Inverted selection for pattern '{pattern}': {affected_count} entries")
        
        return affected_count

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Invert by pattern error: {str(e)}")
        return 0

def invert_selection_by_rw_version(main_window, rw_versions: List[str]) -> int: #vers 1
    """Invert selection only for entries with specific RW versions
    
    Args:
        main_window: Main window instance
        rw_versions: List of RW versions to consider for inversion
        
    Returns:
        int: Number of entries affected by inversion
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

        # Get currently selected rows
        current_selection = _get_current_selection(main_window)
        affected_count = 0
        new_selection = set(current_selection)  # Start with current selection
        
        # Show progress for RW detection
        show_progress(main_window, 0, "Analyzing RW versions for inversion...")
        
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
                    
                    # Only process entries with specified RW versions
                    if version_desc in rw_versions or str(version_value) in rw_versions:
                        if i in current_selection:
                            # Was selected, now deselect
                            new_selection.discard(i)
                            affected_count += 1
                        else:
                            # Was not selected, now select
                            new_selection.add(i)
                            affected_count += 1
                        
            except Exception:
                continue  # Skip entries we can't analyze

        hide_progress(main_window)
        
        # Apply new selection
        table.clearSelection()
        for row in new_selection:
            table.selectRow(row)

        _update_selection_status(main_window, f"Inverted selection for RW versions {', '.join(rw_versions)}: {affected_count} entries affected")
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"🔄 Inverted selection for RW versions {', '.join(rw_versions)}: {affected_count} entries")
        
        return affected_count

    except Exception as e:
        hide_progress(main_window)
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Invert by RW version error: {str(e)}")
        return 0

def smart_invert_selection(main_window) -> int: #vers 1
    """Smart inversion that considers file relationships (DFF/TXD pairs)
    
    Args:
        main_window: Main window instance
        
    Returns:
        int: Number of entries selected after smart inversion
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

        # Get currently selected rows
        current_selection = _get_current_selection(main_window)
        
        # Build DFF/TXD relationship map
        model_pairs = {}  # base_name -> {'dff': row, 'txd': row}
        other_files = []  # Non-model files
        
        for row, entry in enumerate(entries):
            name_lower = entry.name.lower()
            base_name = os.path.splitext(entry.name)[0]
            
            if name_lower.endswith('.dff'):
                if base_name not in model_pairs:
                    model_pairs[base_name] = {}
                model_pairs[base_name]['dff'] = row
            elif name_lower.endswith('.txd'):
                if base_name not in model_pairs:
                    model_pairs[base_name] = {}
                model_pairs[base_name]['txd'] = row
            else:
                other_files.append(row)

        # Smart inversion logic
        new_selection = set()
        
        # For model pairs, invert as pairs when possible
        for base_name, pair_info in model_pairs.items():
            dff_row = pair_info.get('dff')
            txd_row = pair_info.get('txd')
            
            # Check current selection state of the pair
            dff_selected = dff_row is not None and dff_row in current_selection
            txd_selected = txd_row is not None and txd_row in current_selection
            
            # Smart inversion: if either is selected, select the other; if both selected, deselect both
            if dff_selected or txd_selected:
                # At least one is selected - invert the pair
                if dff_row is not None and not dff_selected:
                    new_selection.add(dff_row)
                if txd_row is not None and not txd_selected:
                    new_selection.add(txd_row)
            else:
                # Neither selected - select both
                if dff_row is not None:
                    new_selection.add(dff_row)
                if txd_row is not None:
                    new_selection.add(txd_row)

        # For other files, simple inversion
        for row in other_files:
            if row not in current_selection:
                new_selection.add(row)

        # Apply new selection
        table.clearSelection()
        for row in new_selection:
            table.selectRow(row)

        _update_selection_status(main_window, f"Smart inversion complete: {len(new_selection)} entries selected")
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"🧠 Smart inversion: {len(current_selection)} → {len(new_selection)} entries (considering DFF/TXD pairs)")
        
        return len(new_selection)

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Smart invert error: {str(e)}")
        return 0

def get_inversion_preview(main_window, inversion_type: str = "standard", **kwargs) -> Dict[str, Any]: #vers 1
    """Get preview of what inversion would select
    
    Args:
        main_window: Main window instance
        inversion_type: Type of inversion ('standard', 'by_type', 'by_pattern', 'by_rw', 'smart')
        **kwargs: Additional arguments for specific inversion types
        
    Returns:
        Dict: Preview information
    """
    try:
        table = _get_table_widget(main_window)
        if not table:
            return {'current_selected': 0, 'would_select': 0, 'affected': 0}

        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            return {'current_selected': 0, 'would_select': 0, 'affected': 0}

        entries = main_window.current_img.entries
        if not entries:
            return {'current_selected': 0, 'would_select': 0, 'affected': 0}

        current_selection = _get_current_selection(main_window)
        total_rows = table.rowCount()
        
        preview = {
            'current_selected': len(current_selection),
            'total_entries': total_rows,
            'would_select': 0,
            'affected': 0,
            'inversion_type': inversion_type
        }

        if inversion_type == "standard":
            # Standard inversion - all non-selected become selected
            preview['would_select'] = total_rows - len(current_selection)
            preview['affected'] = total_rows

        elif inversion_type == "by_type":
            file_types = kwargs.get('file_types', [])
            file_types_lower = [ft.lower() for ft in file_types]
            
            affected_rows = []
            for row, entry in enumerate(entries):
                if row >= total_rows:
                    break
                entry_ext = os.path.splitext(entry.name)[1].lower().lstrip('.')
                if entry_ext in file_types_lower:
                    affected_rows.append(row)
            
            # Count how many would be selected after inversion
            would_select = len(current_selection)  # Start with current
            for row in affected_rows:
                if row in current_selection:
                    would_select -= 1  # Would be deselected
                else:
                    would_select += 1  # Would be selected
            
            preview['would_select'] = would_select
            preview['affected'] = len(affected_rows)

        elif inversion_type == "by_pattern":
            pattern = kwargs.get('pattern', '')
            case_sensitive = kwargs.get('case_sensitive', False)
            
            if pattern:
                search_pattern = pattern if case_sensitive else pattern.lower()
                affected_rows = []
                
                for row, entry in enumerate(entries):
                    if row >= total_rows:
                        break
                    entry_name = entry.name if case_sensitive else entry.name.lower()
                    if search_pattern in entry_name:
                        affected_rows.append(row)
                
                # Count how many would be selected after inversion
                would_select = len(current_selection)  # Start with current
                for row in affected_rows:
                    if row in current_selection:
                        would_select -= 1  # Would be deselected
                    else:
                        would_select += 1  # Would be selected
                
                preview['would_select'] = would_select
                preview['affected'] = len(affected_rows)

        elif inversion_type == "smart":
            # This would require the same logic as smart_invert_selection
            # For preview, we'll estimate
            preview['would_select'] = total_rows - len(current_selection)  # Simplified estimate
            preview['affected'] = total_rows

        return preview

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Inversion preview error: {str(e)}")
        return {'current_selected': 0, 'would_select': 0, 'affected': 0}

def _get_table_widget(main_window) -> Optional[QTableWidget]: #vers 1
    """Get table widget from main window"""
    try:
        if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'table'):
            return main_window.gui_layout.table
        return None
    except Exception:
        return None

def _get_current_selection(main_window) -> Set[int]: #vers 1
    """Get set of currently selected row numbers"""
    try:
        table = _get_table_widget(main_window)
        if not table:
            return set()

        selected_items = table.selectedItems()
        selected_rows = set(item.row() for item in selected_items)
        return selected_rows

    except Exception:
        return set()

def _update_selection_status(main_window, message: str): #vers 1
    """Update selection status message"""
    try:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"🔄 {message}")
        
        # Also update status bar if available
        if hasattr(main_window, 'show_status'):
            main_window.show_status(message, 3000)  # Show for 3 seconds
            
    except Exception:
        pass  # Don't fail inversion operations on status update errors

def integrate_inverse_functions(main_window) -> bool: #vers 1
    """Integrate inverse selection functions into main window"""
    try:
        # Add inverse methods
        main_window.invert_selection = lambda: invert_selection(main_window)
        main_window.invert_selection_by_type = lambda file_types: invert_selection_by_type(main_window, file_types)
        main_window.invert_selection_by_pattern = lambda pattern, case_sensitive=False: invert_selection_by_pattern(main_window, pattern, case_sensitive)
        main_window.invert_selection_by_rw_version = lambda rw_versions: invert_selection_by_rw_version(main_window, rw_versions)
        main_window.smart_invert_selection = lambda: smart_invert_selection(main_window)
        main_window.get_inversion_preview = lambda inversion_type="standard", **kwargs: get_inversion_preview(main_window, inversion_type, **kwargs)

        # Aliases for backward compatibility
        main_window.select_inverse = main_window.invert_selection
        main_window.inverse_selection = main_window.invert_selection

        if hasattr(main_window, 'log_message'):
            main_window.log_message("✅ Inverse Selection functions integrated")
            main_window.log_message("   • Standard selection inversion")
            main_window.log_message("   • Type-based inversion")
            main_window.log_message("   • Pattern-based inversion")
            main_window.log_message("   • RW version-based inversion")
            main_window.log_message("   • Smart inversion (DFF/TXD pairs)")
            main_window.log_message("   • Inversion preview capability")

        return True

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Inverse Selection integration failed: {str(e)}")
        return False

# Export functions
__all__ = [
    'invert_selection',
    'invert_selection_by_type',
    'invert_selection_by_pattern',
    'invert_selection_by_rw_version',
    'smart_invert_selection',
    'get_inversion_preview',
    'integrate_inverse_functions'
]