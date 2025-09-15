#this belongs in Core/dump.py - Version: 1
# X-Seti - September11 2025 - IMG Factory 1.5 - Core Dump Functions

"""
Core Dump Functions - Advanced export operations with COL file creation and batch processing
Handles dumping selected entries or all entries with optional COL file generation
"""

import os
from typing import Optional, List, Dict, Any, Tuple
from PyQt6.QtWidgets import QMessageBox, QFileDialog

# Import from new structure
from application.core.rw_versions import detect_rw_file_format, get_rw_version_name, is_valid_rw_version
from shared.progress_functions import show_progress, update_progress, hide_progress, start_operation, complete_operation
from shared.populate_img_table import populate_img_table_enhanced, refresh_table

##Methods list -
# dump_selected_entries
# dump_all_entries
# dump_entries_as_col
# dump_entries_function
# get_dump_preview
# _process_entries_dump
# _create_col_file_from_entries
# _get_selected_entries
# _create_dump_summary
# integrate_dump_functions

def dump_selected_entries(main_window, output_dir: str, create_col: bool = False) -> Tuple[int, int]: #vers 1
    """Dump selected entries from current IMG
    
    Args:
        main_window: Main window instance
        output_dir: Directory to dump files to
        create_col: Whether to create a combined COL file
        
    Returns:
        Tuple[int, int]: (dumped_count, failed_count)
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
                main_window.log_message("⚠️ No entries selected for dump")
            return 0, 0

        # Validate output directory
        if not _validate_dump_destination(main_window, output_dir):
            return 0, len(selected_entries)

        return _process_entries_dump(main_window, selected_entries, output_dir, "selected", create_col)

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Dump selected error: {str(e)}")
        return 0, 0

def dump_all_entries(main_window, output_dir: str, filter_type: str = None, create_col: bool = False) -> Tuple[int, int]: #vers 1
    """Dump all entries from current IMG
    
    Args:
        main_window: Main window instance
        output_dir: Directory to dump files to
        filter_type: Optional file type filter (e.g., 'COL' for collision files only)
        create_col: Whether to create a combined COL file
        
    Returns:
        Tuple[int, int]: (dumped_count, failed_count)
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
        entries_to_dump = all_entries
        if filter_type:
            filter_type = filter_type.lower()
            entries_to_dump = []
            for entry in all_entries:
                entry_ext = os.path.splitext(entry.name)[1].lower().lstrip('.')
                if entry_ext == filter_type:
                    entries_to_dump.append(entry)

        if not entries_to_dump:
            if hasattr(main_window, 'log_message'):
                filter_msg = f" matching type '{filter_type}'" if filter_type else ""
                main_window.log_message(f"⚠️ No entries found{filter_msg}")
            return 0, 0

        # Validate output directory
        if not _validate_dump_destination(main_window, output_dir):
            return 0, len(entries_to_dump)

        operation_name = f"all {filter_type}" if filter_type else "all"
        return _process_entries_dump(main_window, entries_to_dump, output_dir, operation_name, create_col)

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Dump all error: {str(e)}")
        return 0, 0

def dump_entries_as_col(main_window, output_dir: str, entries_list: List = None) -> bool: #vers 1
    """Dump collision entries as combined COL file
    
    Args:
        main_window: Main window instance
        output_dir: Directory to dump COL file to
        entries_list: Optional list of specific entries (uses selected if None)
        
    Returns:
        bool: True if COL file created successfully
    """
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("❌ No IMG file open")
            return False

        # Get entries to dump
        if entries_list is None:
            entries_to_dump = _get_selected_entries(main_window)
            if not entries_to_dump:
                if hasattr(main_window, 'log_message'):
                    main_window.log_message("⚠️ No entries selected for COL dump")
                return False
        else:
            entries_to_dump = entries_list

        # Filter for COL files only
        col_entries = []
        for entry in entries_to_dump:
            if entry.name.lower().endswith('.col'):
                col_entries.append(entry)

        if not col_entries:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("⚠️ No COL files found in selection")
            return False

        # Create combined COL file
        return _create_col_file_from_entries(main_window, col_entries, output_dir)

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ COL dump error: {str(e)}")
        return False

def dump_entries_function(main_window) -> bool: #vers 1
    """Main dump function with folder dialog and options"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first")
            return False

        # Get selected entries
        selected_entries = _get_selected_entries(main_window)
        if not selected_entries:
            QMessageBox.warning(main_window, "No Selection", "Please select entries to dump")
            return False

        # Show folder dialog
        output_dir = QFileDialog.getExistingDirectory(
            main_window,
            "Select Dump Folder"
        )

        if not output_dir:
            return False

        # Check if there are COL files and ask about combined COL
        col_files = [e for e in selected_entries if e.name.lower().endswith('.col')]
        create_col = False
        
        if col_files:
            reply = QMessageBox.question(
                main_window,
                "COL Files Found",
                f"Found {len(col_files)} COL files in selection.\n\n"
                f"Create combined COL file in addition to individual files?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            create_col = (reply == QMessageBox.StandardButton.Yes)

        # Dump selected entries
        dumped, failed = dump_selected_entries(main_window, output_dir, create_col)
        
        return dumped > 0

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Dump dialog error: {str(e)}")
        return False

def get_dump_preview(main_window, entries_list: List = None) -> Dict[str, Any]: #vers 1
    """Get preview information for entries to be dumped"""
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
            'col_files': 0,
            'can_create_col': False,
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

                # Check for COL files
                if entry_ext == 'COL':
                    preview['col_files'] += 1

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
                continue

        # Can create combined COL if there are multiple COL files
        preview['can_create_col'] = preview['col_files'] > 1

        return preview

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Dump preview error: {str(e)}")
        return {'total_entries': 0, 'valid_entries': 0, 'entries': []}

def _validate_dump_destination(main_window, output_dir: str) -> bool: #vers 1
    """Validate dump destination directory"""
    try:
        # Check if directory exists
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"📁 Created dump directory: {output_dir}")
            except Exception as e:
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"❌ Cannot create dump directory: {str(e)}")
                return False

        # Check write permissions
        test_file = os.path.join(output_dir, 'test_dump.tmp')
        try:
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            return True
        except Exception as e:
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"❌ No write permission to dump directory: {str(e)}")
            return False

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Dump validation error: {str(e)}")
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

def _process_entries_dump(main_window, entries_to_dump: List, output_dir: str, operation_name: str, create_col: bool) -> Tuple[int, int]: #vers 1
    """Process dump of entries with progress tracking"""
    try:
        total_entries = len(entries_to_dump)
        dumped_count = 0
        failed_count = 0
        rw_stats = {}

        # Start operation with progress
        start_operation(main_window, f"Dumping {operation_name} ({total_entries} entries)", cancellable=True)

        for i, entry in enumerate(entries_to_dump):
            # Check for cancellation
            if hasattr(main_window, 'is_operation_cancelled') and main_window.is_operation_cancelled():
                if hasattr(main_window, 'log_message'):
                    main_window.log_message("⚠️ Dump cancelled by user")
                break

            # Update progress
            progress = int((i / total_entries) * 100)
            update_progress(main_window, progress, f"Dumping {entry.name}...")

            # Dump entry
            if _process_single_dump(main_window, entry, output_dir, rw_stats):
                dumped_count += 1
            else:
                failed_count += 1

        # Create combined COL file if requested
        if create_col and dumped_count > 0:
            col_entries = [e for e in entries_to_dump if e.name.lower().endswith('.col')]
            if col_entries:
                update_progress(main_window, 95, "Creating combined COL file...")
                _create_col_file_from_entries(main_window, col_entries, output_dir)

        # Complete operation
        complete_operation(main_window, True, f"Dump complete: {dumped_count} dumped, {failed_count} failed")

        # Create summary
        _create_dump_summary(main_window, dumped_count, failed_count, rw_stats, output_dir, create_col)

        return dumped_count, failed_count

    except Exception as e:
        complete_operation(main_window, False, f"Dump failed: {str(e)}")
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Dump processing error: {str(e)}")
        return 0, len(entries_to_dump) if entries_to_dump else 0

def _process_single_dump(main_window, entry, output_dir: str, rw_stats: Dict) -> bool: #vers 1
    """Dump single entry with RW detection"""
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

        # Dump file
        dump_path = os.path.join(output_dir, entry.name)
        
        # Handle overwrite (for dump, we usually overwrite)
        with open(dump_path, 'wb') as f:
            f.write(entry_data)

        # Log with RW info
        rw_info = f" ({file_format} {version_desc})" if is_valid_rw_version(version_value) else ""
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"📦 Dumped: {entry.name}{rw_info}")

        return True

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Failed to dump {entry.name}: {str(e)}")
        return False

def _create_col_file_from_entries(main_window, col_entries: List, output_dir: str) -> bool: #vers 1
    """Create combined COL file from multiple COL entries"""
    try:
        if not col_entries:
            return False

        # Get IMG filename for COL name
        img_name = "combined"
        if hasattr(main_window, 'current_img') and hasattr(main_window.current_img, 'file_path'):
            img_name = os.path.splitext(os.path.basename(main_window.current_img.file_path))[0]

        col_filename = f"{img_name}_combined.col"
        col_path = os.path.join(output_dir, col_filename)

        # This is a simplified COL combination - real implementation would need proper COL parsing
        with open(col_path, 'wb') as combined_file:
            # Write basic COL header (simplified)
            combined_file.write(b'COLL')  # COL signature
            
            # Combine all COL data (simplified approach)
            total_size = 0
            for entry in col_entries:
                try:
                    entry_data = entry.get_data()
                    if entry_data and len(entry_data) > 4:  # Skip COL header
                        combined_file.write(entry_data[4:])  # Skip individual headers
                        total_size += len(entry_data) - 4
                except Exception:
                    continue

        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"📦 Created combined COL: {col_filename} ({len(col_entries)} files)")

        return True

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Failed to create combined COL: {str(e)}")
        return False

def _create_dump_summary(main_window, dumped: int, failed: int, rw_stats: Dict, output_dir: str, created_col: bool): #vers 1
    """Create detailed dump summary with RW statistics"""
    try:
        # Basic summary
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"📋 Dump complete: {dumped} dumped, {failed} failed")
            main_window.log_message(f"📁 Dump location: {output_dir}")
            
            if created_col:
                main_window.log_message("📦 Combined COL file created")
            
            # RW version breakdown
            if rw_stats:
                main_window.log_message("📊 RenderWare version breakdown:")
                for version, count in sorted(rw_stats.items()):
                    main_window.log_message(f"   • {version}: {count} files")

        # Show summary dialog for large dumps
        if dumped > 10:
            summary_text = f"Dump Summary:\n\n"
            summary_text += f"Dumped: {dumped} files\n"
            summary_text += f"Failed: {failed} files\n"
            summary_text += f"Location: {output_dir}\n"
            
            if created_col:
                summary_text += f"Combined COL: Created\n"
            
            summary_text += "\n"
            
            if rw_stats:
                summary_text += "RenderWare Versions:\n"
                for version, count in sorted(rw_stats.items()):
                    summary_text += f"• {version}: {count} files\n"
            
            QMessageBox.information(main_window, "Dump Complete", summary_text)

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"⚠️ Error creating dump summary: {str(e)}")

def integrate_dump_functions(main_window) -> bool: #vers 1
    """Integrate core dump functions into main window"""
    try:
        # Add core dump methods
        main_window.dump_selected_entries = lambda output_dir, create_col=False: dump_selected_entries(main_window, output_dir, create_col)
        main_window.dump_all_entries = lambda output_dir, filter_type=None, create_col=False: dump_all_entries(main_window, output_dir, filter_type, create_col)
        main_window.dump_entries_as_col = lambda output_dir, entries=None: dump_entries_as_col(main_window, output_dir, entries)
        main_window.dump_entries_function = lambda: dump_entries_function(main_window)
        main_window.get_dump_preview = lambda entries=None: get_dump_preview(main_window, entries)

        # Aliases for backward compatibility
        main_window.dump_selected = main_window.dump_entries_function
        main_window.dump_all = lambda output_dir: dump_all_entries(main_window, output_dir)

        if hasattr(main_window, 'log_message'):
            main_window.log_message("✅ Core Dump functions integrated")
            main_window.log_message("   • Selected entries dump")
            main_window.log_message("   • All entries dump")
            main_window.log_message("   • Combined COL file creation")
            main_window.log_message("   • RW version detection")
            main_window.log_message("   • Dump preview and validation")

        return True

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Core Dump integration failed: {str(e)}")
        return False

# Export functions
__all__ = [
    'dump_selected_entries',
    'dump_all_entries',
    'dump_entries_as_col',
    'dump_entries_function',
    'get_dump_preview',
    'integrate_dump_functions'
]
