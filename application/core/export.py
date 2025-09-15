#this belongs in Core/export.py - Version: 1
# X-Seti - September11 2025 - IMG Factory 1.5 - Core Export Functions

"""
Core Export Functions - Essential file export operations extracted from img_editor_tool
Handles single entry, multiple entry, and filtered export with RW detection and validation
"""

import os
from typing import Optional, List, Dict, Any, Tuple
from PyQt6.QtWidgets import QMessageBox, QFileDialog

# Import from new structure
from application.core.rw_versions import detect_rw_file_format, get_rw_version_name, is_valid_rw_version
from shared.progress_functions import show_progress, update_progress, hide_progress, start_operation, complete_operation
from shared.populate_img_table import populate_img_table_enhanced, refresh_table

##Methods list -
# export_selected_entries
# export_all_entries
# export_entries_by_type
# export_entries_by_name
# export_entries_function
# get_export_preview
# validate_export_destination
# _process_entry_export
# _get_selected_entries
# _create_export_summary
# integrate_export_functions

def export_selected_entries(main_window, output_dir: str) -> Tuple[int, int]: #vers 1
    """Export selected entries from current IMG
    
    Args:
        main_window: Main window instance
        output_dir: Directory to export files to
        
    Returns:
        Tuple[int, int]: (exported_count, failed_count)
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
                main_window.log_message("⚠️ No entries selected for export")
            return 0, 0

        # Validate output directory
        if not validate_export_destination(main_window, output_dir):
            return 0, len(selected_entries)

        return _process_entries_export(main_window, selected_entries, output_dir, "selected")

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Export selected error: {str(e)}")
        return 0, 0

def export_all_entries(main_window, output_dir: str, filter_type: str = None) -> Tuple[int, int]: #vers 1
    """Export all entries from current IMG
    
    Args:
        main_window: Main window instance
        output_dir: Directory to export files to
        filter_type: Optional file type filter (e.g., 'DFF', 'TXD')
        
    Returns:
        Tuple[int, int]: (exported_count, failed_count)
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

        # Apply type filter if specified
        entries_to_export = all_entries
        if filter_type:
            filter_type = filter_type.lower()
            entries_to_export = []
            for entry in all_entries:
                entry_ext = os.path.splitext(entry.name)[1].lower().lstrip('.')
                if entry_ext == filter_type:
                    entries_to_export.append(entry)

        if not entries_to_export:
            if hasattr(main_window, 'log_message'):
                filter_msg = f" matching type '{filter_type}'" if filter_type else ""
                main_window.log_message(f"⚠️ No entries found{filter_msg}")
            return 0, 0

        # Validate output directory
        if not validate_export_destination(main_window, output_dir):
            return 0, len(entries_to_export)

        operation_name = f"all {filter_type}" if filter_type else "all"
        return _process_entries_export(main_window, entries_to_export, output_dir, operation_name)

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Export all error: {str(e)}")
        return 0, 0

def export_entries_by_type(main_window, output_dir: str, file_types: List[str]) -> Tuple[int, int]: #vers 1
    """Export entries filtered by file types
    
    Args:
        main_window: Main window instance
        output_dir: Directory to export files to
        file_types: List of file extensions to export (e.g., ['dff', 'txd'])
        
    Returns:
        Tuple[int, int]: (exported_count, failed_count)
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
        entries_to_export = []
        
        for entry in all_entries:
            entry_ext = os.path.splitext(entry.name)[1].lower().lstrip('.')
            if entry_ext in file_types_lower:
                entries_to_export.append(entry)

        if not entries_to_export:
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"⚠️ No entries found matching types: {', '.join(file_types)}")
            return 0, 0

        # Validate output directory
        if not validate_export_destination(main_window, output_dir):
            return 0, len(entries_to_export)

        return _process_entries_export(main_window, entries_to_export, output_dir, f"types: {', '.join(file_types)}")

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Export by type error: {str(e)}")
        return 0, 0

def export_entries_by_name(main_window, output_dir: str, name_patterns: List[str], 
                          case_sensitive: bool = False) -> Tuple[int, int]: #vers 1
    """Export entries matching name patterns
    
    Args:
        main_window: Main window instance
        output_dir: Directory to export files to
        name_patterns: List of name patterns to match
        case_sensitive: Whether pattern matching is case sensitive
        
    Returns:
        Tuple[int, int]: (exported_count, failed_count)
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
        entries_to_export = []
        search_patterns = name_patterns if case_sensitive else [p.lower() for p in name_patterns]
        
        for entry in all_entries:
            entry_name = entry.name if case_sensitive else entry.name.lower()
            
            for pattern in search_patterns:
                if pattern in entry_name:
                    entries_to_export.append(entry)
                    break  # Only add once even if multiple patterns match

        if not entries_to_export:
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"⚠️ No entries found matching patterns: {', '.join(name_patterns)}")
            return 0, 0

        # Validate output directory
        if not validate_export_destination(main_window, output_dir):
            return 0, len(entries_to_export)

        return _process_entries_export(main_window, entries_to_export, output_dir, f"patterns: {', '.join(name_patterns)}")

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Export by name error: {str(e)}")
        return 0, 0

def export_entries_function(main_window) -> bool: #vers 1
    """Main export function with folder dialog"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first")
            return False

        # Get selected entries
        selected_entries = _get_selected_entries(main_window)
        if not selected_entries:
            QMessageBox.warning(main_window, "No Selection", "Please select entries to export")
            return False

        # Show folder dialog
        output_dir = QFileDialog.getExistingDirectory(
            main_window,
            "Select Export Folder"
        )

        if not output_dir:
            return False

        # Export selected entries
        exported, failed = export_selected_entries(main_window, output_dir)
        
        return exported > 0

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Export dialog error: {str(e)}")
        return False

def get_export_preview(main_window, entries_list: List = None, filter_type: str = None) -> Dict[str, Any]: #vers 1
    """Get preview information for entries to be exported
    
    Args:
        main_window: Main window instance
        entries_list: Optional list of specific entries (uses selected if None)
        filter_type: Optional file type filter
        
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
                entries_to_analyze = main_window.current_img.entries
        else:
            entries_to_analyze = entries_list

        if not entries_to_analyze:
            return {'total_entries': 0, 'valid_entries': 0, 'entries': []}

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
                # Apply filter if specified
                if filter_type:
                    entry_ext = os.path.splitext(entry.name)[1].lower().lstrip('.')
                    if entry_ext != filter_type.lower():
                        continue

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
            main_window.log_message(f"❌ Export preview error: {str(e)}")
        return {'total_entries': 0, 'valid_entries': 0, 'entries': []}

def validate_export_destination(main_window, output_dir: str) -> bool: #vers 1
    """Validate export destination directory
    
    Args:
        main_window: Main window instance
        output_dir: Directory to validate
        
    Returns:
        bool: True if directory is valid for export
    """
    try:
        # Check if directory exists
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"📁 Created export directory: {output_dir}")
            except Exception as e:
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"❌ Cannot create export directory: {str(e)}")
                return False

        # Check write permissions
        test_file = os.path.join(output_dir, 'test_write.tmp')
        try:
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            return True
        except Exception as e:
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"❌ No write permission to export directory: {str(e)}")
            return False

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Export validation error: {str(e)}")
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

def _process_entries_export(main_window, entries_to_export: List, output_dir: str, operation_name: str) -> Tuple[int, int]: #vers 1
    """Process export of entries with progress tracking"""
    try:
        total_entries = len(entries_to_export)
        exported_count = 0
        failed_count = 0
        rw_stats = {}

        # Start operation with progress
        start_operation(main_window, f"Exporting {operation_name} ({total_entries} entries)", cancellable=True)

        for i, entry in enumerate(entries_to_export):
            # Check for cancellation
            if hasattr(main_window, 'is_operation_cancelled') and main_window.is_operation_cancelled():
                if hasattr(main_window, 'log_message'):
                    main_window.log_message("⚠️ Export cancelled by user")
                break

            # Update progress
            progress = int((i / total_entries) * 100)
            update_progress(main_window, progress, f"Exporting {entry.name}...")

            # Export entry
            if _process_single_export(main_window, entry, output_dir, rw_stats):
                exported_count += 1
            else:
                failed_count += 1

        # Complete operation
        complete_operation(main_window, True, f"Export complete: {exported_count} exported, {failed_count} failed")

        # Create summary
        _create_export_summary(main_window, exported_count, failed_count, rw_stats, output_dir)

        return exported_count, failed_count

    except Exception as e:
        complete_operation(main_window, False, f"Export failed: {str(e)}")
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Export processing error: {str(e)}")
        return 0, len(entries_to_export) if entries_to_export else 0

def _process_single_export(main_window, entry, output_dir: str, rw_stats: Dict) -> bool: #vers 1
    """Export single entry with RW detection"""
    try:
        # Get entry data
        entry_data = entry.get_data()
        if not entry_data:
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"❌ No data for: {entry.name}")
            return False

        # Detect RW version
        file_format, version_desc, version_value = detect_rw_file_format(entry_data, entry.name)
        
        # Track RW statistics
        if version_desc not in rw_stats:
            rw_stats[version_desc] = 0
        rw_stats[version_desc] += 1

        # Export file
        export_path = os.path.join(output_dir, entry.name)
        
        # Handle overwrite
        if os.path.exists(export_path):
            # For now, overwrite. Could add dialog here later
            pass

        with open(export_path, 'wb') as f:
            f.write(entry_data)

        # Log with RW info
        rw_info = f" ({file_format} {version_desc})" if is_valid_rw_version(version_value) else ""
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"✅ Exported: {entry.name}{rw_info}")

        return True

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Failed to export {entry.name}: {str(e)}")
        return False

def _create_export_summary(main_window, exported: int, failed: int, rw_stats: Dict, output_dir: str): #vers 1
    """Create detailed export summary with RW statistics"""
    try:
        # Basic summary
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"📋 Export complete: {exported} exported, {failed} failed")
            main_window.log_message(f"📁 Export location: {output_dir}")
            
            # RW version breakdown
            if rw_stats:
                main_window.log_message("📊 RenderWare version breakdown:")
                for version, count in sorted(rw_stats.items()):
                    main_window.log_message(f"   • {version}: {count} files")

        # Show summary dialog for large exports
        if exported > 10:
            summary_text = f"Export Summary:\n\n"
            summary_text += f"Exported: {exported} files\n"
            summary_text += f"Failed: {failed} files\n"
            summary_text += f"Location: {output_dir}\n\n"
            
            if rw_stats:
                summary_text += "RenderWare Versions:\n"
                for version, count in sorted(rw_stats.items()):
                    summary_text += f"• {version}: {count} files\n"
            
            QMessageBox.information(main_window, "Export Complete", summary_text)

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"⚠️ Error creating export summary: {str(e)}")

def integrate_export_functions(main_window) -> bool: #vers 1
    """Integrate core export functions into main window"""
    try:
        # Add core export methods
        main_window.export_selected_entries = lambda output_dir: export_selected_entries(main_window, output_dir)
        main_window.export_all_entries = lambda output_dir, filter_type=None: export_all_entries(main_window, output_dir, filter_type)
        main_window.export_entries_by_type = lambda output_dir, file_types: export_entries_by_type(main_window, output_dir, file_types)
        main_window.export_entries_by_name = lambda output_dir, patterns, case_sensitive=False: export_entries_by_name(main_window, output_dir, patterns, case_sensitive)
        main_window.export_entries_function = lambda: export_entries_function(main_window)
        main_window.get_export_preview = lambda entries=None, filter_type=None: get_export_preview(main_window, entries, filter_type)
        main_window.validate_export_destination = lambda output_dir: validate_export_destination(main_window, output_dir)

        # Aliases for backward compatibility
        main_window.export_selected = main_window.export_entries_function
        main_window.export_all = lambda output_dir: export_all_entries(main_window, output_dir)

        if hasattr(main_window, 'log_message'):
            main_window.log_message("✅ Core Export functions integrated")
            main_window.log_message("   • Selected entries export")
            main_window.log_message("   • All entries export")
            main_window.log_message("   • Type-filtered export")
            main_window.log_message("   • Name-pattern export")
            main_window.log_message("   • RW version detection")
            main_window.log_message("   • Export preview and validation")

        return True

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Core Export integration failed: {str(e)}")
        return False

# Export functions
__all__ = [
    'export_selected_entries',
    'export_all_entries',
    'export_entries_by_type',
    'export_entries_by_name',
    'export_entries_function',
    'get_export_preview',
    'validate_export_destination',
    'integrate_export_functions'
]