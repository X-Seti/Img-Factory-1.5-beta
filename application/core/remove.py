#this belongs in Core/remove.py - Version: 1
# X-Seti - September11 2025 - IMG Factory 1.5 - Core Remove Functions

"""
Core Remove Functions - Essential entry removal operations extracted from img_editor_tool
Handles single entry, multiple entry, and filtered removal with RW detection and tracking
"""

import os
from typing import Optional, List, Dict, Any, Tuple
from PyQt6.QtWidgets import QMessageBox

# Import from new structure
from Core.rw_versions import detect_rw_file_format, get_rw_version_name, is_valid_rw_version
from Shared.progress_functions import show_progress, update_progress, hide_progress, start_operation, complete_operation
from Shared.populate_img_table import populate_img_table_enhanced, refresh_table

##Methods list -
# remove_selected_entries
# remove_entries_by_type
# remove_entries_by_name
# remove_all_entries
# remove_entries_function
# get_removal_preview
# confirm_removal
# _process_entries_removal
# _process_single_removal
# _get_selected_entries
# _create_removal_summary
# _refresh_img_table
# integrate_remove_functions

def remove_selected_entries(main_window) -> Tuple[int, int]: #vers 1
    """Remove selected entries from current IMG
    
    Args:
        main_window: Main window instance
        
    Returns:
        Tuple[int, int]: (removed_count, failed_count)
    """
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("❌ No IMG file open")
            return 0, 0

        # Get selected entries
        selected_entries = _get_selected_entries(main_window)
        if not selected_entries:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("⚠️ No entries selected for removal")
            return 0, 0

        # Confirm removal
        if not confirm_removal(main_window, selected_entries, "selected"):
            return 0, 0

        return _process_entries_removal(main_window, selected_entries, "selected")

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Remove selected error: {str(e)}")
        return 0, 0

def remove_entries_by_type(main_window, file_types: List[str], confirm: bool = True) -> Tuple[int, int]: #vers 1
    """Remove entries filtered by file types
    
    Args:
        main_window: Main window instance
        file_types: List of file extensions to remove (e.g., ['dff', 'txd'])
        confirm: Whether to show confirmation dialog
        
    Returns:
        Tuple[int, int]: (removed_count, failed_count)
    """
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("❌ No IMG file open")
            return 0, 0

        all_entries = main_window.current_img.entries
        if not all_entries:
            return 0, 0

        # Filter by types
        file_types_lower = [ft.lower() for ft in file_types]
        entries_to_remove = []
        
        for entry in all_entries:
            entry_ext = os.path.splitext(entry.name)[1].lower().lstrip('.')
            if entry_ext in file_types_lower:
                entries_to_remove.append(entry)

        if not entries_to_remove:
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"⚠️ No entries found matching types: {', '.join(file_types)}")
            return 0, 0

        # Confirm removal if requested
        if confirm and not confirm_removal(main_window, entries_to_remove, f"type '{', '.join(file_types)}'"):
            return 0, 0

        return _process_entries_removal(main_window, entries_to_remove, f"types: {', '.join(file_types)}")

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Remove by type error: {str(e)}")
        return 0, 0

def remove_entries_by_name(main_window, name_patterns: List[str], case_sensitive: bool = False, 
                          confirm: bool = True) -> Tuple[int, int]: #vers 1
    """Remove entries matching name patterns
    
    Args:
        main_window: Main window instance
        name_patterns: List of name patterns to match
        case_sensitive: Whether pattern matching is case sensitive
        confirm: Whether to show confirmation dialog
        
    Returns:
        Tuple[int, int]: (removed_count, failed_count)
    """
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("❌ No IMG file open")
            return 0, 0

        all_entries = main_window.current_img.entries
        if not all_entries:
            return 0, 0

        # Filter by name patterns
        entries_to_remove = []
        search_patterns = name_patterns if case_sensitive else [p.lower() for p in name_patterns]
        
        for entry in all_entries:
            entry_name = entry.name if case_sensitive else entry.name.lower()
            
            for pattern in search_patterns:
                if pattern in entry_name:
                    entries_to_remove.append(entry)
                    break  # Only add once even if multiple patterns match

        if not entries_to_remove:
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"⚠️ No entries found matching patterns: {', '.join(name_patterns)}")
            return 0, 0

        # Confirm removal if requested
        if confirm and not confirm_removal(main_window, entries_to_remove, f"pattern '{', '.join(name_patterns)}'"):
            return 0, 0

        return _process_entries_removal(main_window, entries_to_remove, f"patterns: {', '.join(name_patterns)}")

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Remove by name error: {str(e)}")
        return 0, 0

def remove_all_entries(main_window, confirm: bool = True) -> Tuple[int, int]: #vers 1
    """Remove all entries from current IMG
    
    Args:
        main_window: Main window instance
        confirm: Whether to show confirmation dialog
        
    Returns:
        Tuple[int, int]: (removed_count, failed_count)
    """
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("❌ No IMG file open")
            return 0, 0

        all_entries = main_window.current_img.entries
        if not all_entries:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("⚠️ No entries found in IMG")
            return 0, 0

        # Special confirmation for removing ALL entries
        if confirm:
            reply = QMessageBox.question(
                main_window,
                "Remove All Entries",
                f"Remove ALL {len(all_entries)} entries from the IMG file?\n\n"
                f"This will leave the IMG file empty.\n"
                f"This action cannot be undone.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply != QMessageBox.StandardButton.Yes:
                return 0, 0

        return _process_entries_removal(main_window, all_entries, "all entries")

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Remove all error: {str(e)}")
        return 0, 0

def remove_entries_function(main_window) -> bool: #vers 1
    """Main remove function for selected entries with confirmation"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first")
            return False

        # Get selected entries
        selected_entries = _get_selected_entries(main_window)
        if not selected_entries:
            QMessageBox.warning(main_window, "No Selection", "Please select entries to remove")
            return False

        # Remove selected entries (with confirmation)
        removed, failed = remove_selected_entries(main_window)
        
        return removed > 0

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Remove function error: {str(e)}")
        return False

def get_removal_preview(main_window, entries_list: List = None) -> Dict[str, Any]: #vers 1
    """Get preview information for entries to be removed
    
    Args:
        main_window: Main window instance
        entries_list: Optional list of specific entries (uses selected if None)
        
    Returns:
        Dict with preview information
    """
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            return {'total_entries': 0, 'valid_entries': 0, 'entries': []}

        # Get entries to analyze
        if entries_list is None:
            entries_to_analyze = _get_selected_entries(main_window)
            if not entries_to_analyze:
                return {'total_entries': 0, 'valid_entries': 0, 'entries': []}
        else:
            entries_to_analyze = entries_list

        preview = {
            'total_entries': len(entries_to_analyze),
            'valid_entries': 0,
            'total_size': 0,
            'file_types': {},
            'rw_versions': {},
            'entries': []
        }

        for entry in entries_to_analyze:
            try:
                # Get entry data for analysis
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

                preview['entries'].append(entry_info)
                preview['valid_entries'] += 1
                preview['total_size'] += entry_size

                # Track file types
                if entry_ext not in preview['file_types']:
                    preview['file_types'][entry_ext] = 0
                preview['file_types'][entry_ext] += 1

                # Track RW versions
                if version_desc not in preview['rw_versions']:
                    preview['rw_versions'][version_desc] = 0
                preview['rw_versions'][version_desc] += 1

            except Exception:
                # Skip entries we can't read
                continue

        return preview

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Removal preview error: {str(e)}")
        return {'total_entries': 0, 'valid_entries': 0, 'entries': []}

def confirm_removal(main_window, entries_to_remove: List, filter_description: str) -> bool: #vers 1
    """Confirm removal with user
    
    Args:
        main_window: Main window instance
        entries_to_remove: List of entries to remove
        filter_description: Description of filter used
        
    Returns:
        bool: True if user confirmed removal
    """
    try:
        count = len(entries_to_remove)
        
        # Show confirmation dialog
        message = f"Remove {count} entries matching {filter_description}?\n\n"
        message += "This action cannot be undone.\n\n"
        
        if count <= 10:
            message += "Entries to remove:\n"
            for entry in entries_to_remove:
                message += f"• {entry.name}\n"
        else:
            message += f"First 5 entries:\n"
            for entry in entries_to_remove[:5]:
                message += f"• {entry.name}\n"
            message += f"... and {count - 5} more entries"
        
        reply = QMessageBox.question(
            main_window, 
            "Confirm Removal", 
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        return reply == QMessageBox.StandardButton.Yes
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Confirmation dialog error: {str(e)}")
        return False

def _get_selected_entries(main_window) -> List: #vers 1
    """Get selected entries from table or IMG Editor Tool"""
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

def _process_entries_removal(main_window, entries_to_remove: List, operation_name: str) -> Tuple[int, int]: #vers 1
    """Process removal of entries with progress tracking"""
    try:
        total_entries = len(entries_to_remove)
        removed_count = 0
        failed_count = 0
        rw_stats = {}

        # Start operation with progress
        start_operation(main_window, f"Removing {operation_name} ({total_entries} entries)", cancellable=True)

        for i, entry in enumerate(entries_to_remove):
            # Check for cancellation
            if hasattr(main_window, 'is_operation_cancelled') and main_window.is_operation_cancelled():
                if hasattr(main_window, 'log_message'):
                    main_window.log_message("⚠️ Removal cancelled by user")
                break

            # Update progress
            progress = int((i / total_entries) * 100)
            update_progress(main_window, progress, f"Removing {entry.name}...")

            # Remove entry
            if _process_single_removal(main_window, entry, rw_stats):
                removed_count += 1
            else:
                failed_count += 1

        # Complete operation
        complete_operation(main_window, True, f"Removal complete: {removed_count} removed, {failed_count} failed")

        # Create summary
        _create_removal_summary(main_window, removed_count, failed_count, rw_stats)

        # Refresh table if any removals succeeded
        if removed_count > 0:
            _refresh_img_table(main_window)

        return removed_count, failed_count

    except Exception as e:
        complete_operation(main_window, False, f"Removal failed: {str(e)}")
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Removal processing error: {str(e)}")
        return 0, len(entries_to_remove) if entries_to_remove else 0

def _process_single_removal(main_window, entry, rw_stats: Dict) -> bool: #vers 1
    """Remove single entry with RW detection"""
    try:
        # Get RW info before removal
        try:
            entry_data = entry.get_data()
            if entry_data and len(entry_data) >= 12:
                file_format, version_desc, version_value = detect_rw_file_format(entry_data, entry.name)
                
                # Track RW statistics
                if version_desc not in rw_stats:
                    rw_stats[version_desc] = 0
                rw_stats[version_desc] += 1
                
                rw_info = f" ({file_format} {version_desc})" if is_valid_rw_version(version_value) else ""
            else:
                rw_info = ""
        except Exception:
            rw_info = ""

        # Remove entry using available methods
        success = False
        
        # Method 1: Use remove_entry_safe if available
        if hasattr(main_window, 'remove_entry_safe'):
            success = main_window.remove_entry_safe(main_window.current_img, entry)
        
        # Method 2: Use IMG object remove_entry method
        elif hasattr(main_window.current_img, 'remove_entry'):
            success = main_window.current_img.remove_entry(entry)
        
        # Method 3: Direct entry removal (fallback)
        else:
            if entry in main_window.current_img.entries:
                main_window.current_img.entries.remove(entry)
                success = True
            else:
                success = False

        if success:
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"🗑️ Removed: {entry.name}{rw_info}")
        else:
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"❌ Failed to remove: {entry.name}")

        return success

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Error removing {entry.name}: {str(e)}")
        return False

def _create_removal_summary(main_window, removed: int, failed: int, rw_stats: Dict): #vers 1
    """Create detailed removal summary with RW statistics"""
    try:
        # Basic summary
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"📋 Removal complete: {removed} removed, {failed} failed")
            
            # RW version breakdown
            if rw_stats:
                main_window.log_message("📊 Removed RenderWare versions:")
                for version, count in sorted(rw_stats.items()):
                    main_window.log_message(f"   • {version}: {count} files")

        # Show summary dialog for large removals
        if removed > 10:
            summary_text = f"Removal Summary:\n\n"
            summary_text += f"Removed: {removed} files\n"
            summary_text += f"Failed: {failed} files\n\n"
            
            if rw_stats:
                summary_text += "Removed RenderWare Versions:\n"
                for version, count in sorted(rw_stats.items()):
                    summary_text += f"• {version}: {count} files\n"
            
            QMessageBox.information(main_window, "Removal Complete", summary_text)

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"⚠️ Error creating removal summary: {str(e)}")

def _refresh_img_table(main_window): #vers 1
    """Refresh IMG table after removal"""
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

def integrate_remove_functions(main_window) -> bool: #vers 1
    """Integrate core remove functions into main window"""
    try:
        # Add core remove methods
        main_window.remove_selected_entries = lambda: remove_selected_entries(main_window)
        main_window.remove_entries_by_type = lambda file_types, confirm=True: remove_entries_by_type(main_window, file_types, confirm)
        main_window.remove_entries_by_name = lambda patterns, case_sensitive=False, confirm=True: remove_entries_by_name(main_window, patterns, case_sensitive, confirm)
        main_window.remove_all_entries = lambda confirm=True: remove_all_entries(main_window, confirm)
        main_window.remove_entries_function = lambda: remove_entries_function(main_window)
        main_window.get_removal_preview = lambda entries=None: get_removal_preview(main_window, entries)
        main_window.confirm_removal = lambda entries, description: confirm_removal(main_window, entries, description)

        # Aliases for backward compatibility
        main_window.remove_selected = main_window.remove_entries_function
        main_window.remove_entries = main_window.remove_selected_entries

        if hasattr(main_window, 'log_message'):
            main_window.log_message("✅ Core Remove functions integrated")
            main_window.log_message("   • Selected entries removal")
            main_window.log_message("   • Type-filtered removal")
            main_window.log_message("   • Name-pattern removal")
            main_window.log_message("   • All entries removal")
            main_window.log_message("   • RW version tracking")
            main_window.log_message("   • Removal preview and confirmation")

        return True

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Core Remove integration failed: {str(e)}")
        return False

# Export functions
__all__ = [
    'remove_selected_entries',
    'remove_entries_by_type',
    'remove_entries_by_name',
    'remove_all_entries',
    'remove_entries_function',
    'get_removal_preview',
    'confirm_removal',
    'integrate_remove_functions'
]