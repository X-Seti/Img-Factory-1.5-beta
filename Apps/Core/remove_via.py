#this belongs in Core/remove_via.py - Version: 1
# X-Seti - September11 2025 - IMG Factory 1.5 - Remove Via Functions

"""
Remove Via Functions - Enhanced remove operations using IDE parser, RW detection and GUI dialogs
Uses existing components: methods/ide_parser_functions.py, core/rw_versions.py, gui/ide_dialog.py
"""

import os
from typing import Optional, List, Dict, Any, Tuple
from PyQt6.QtWidgets import QMessageBox, QFileDialog, QProgressDialog
from PyQt6.QtCore import Qt

# Import existing components - updated paths
from Shared.ide_parser_functions import IDEParser, parse_ide_file
from Core.rw_versions import detect_rw_file_format, get_rw_version_name, is_valid_rw_version
from Gui.ide_dialog import IDEDialog, create_ide_dialog
from Shared.progress_functions import show_progress, hide_progress
from Shared.populate_img_table import refresh_table, populate_img_table_enhanced
from Shared.populate_col_table import populate_col_table_enhanced

##Methods list -
# remove_via_entries_function
# remove_via_ide_filter
# remove_via_type_filter
# remove_via_rw_filter
# remove_via_name_pattern
# _get_entries_to_remove
# _confirm_removal
# _process_removal_with_tracking
# _create_removal_summary
# integrate_remove_via_functions

def remove_via_entries_function(main_window): #vers 1
    """Main remove via function - shows dialog for removal method selection"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first")
            return False

        if not hasattr(main_window.current_img, 'entries') or not main_window.current_img.entries:
            QMessageBox.information(main_window, "No Entries", "No entries found in IMG file")
            return False

        # Create IDE dialog for remove operation
        dialog = create_ide_dialog(main_window, "remove")
        if not dialog:
            main_window.log_message("❌ Failed to create remove dialog")
            return False

        # Show dialog and get result
        if dialog.exec() == dialog.DialogCode.Accepted:
            parser = dialog.get_ide_parser()
            if parser and parser.models:
                return remove_via_ide_filter(main_window, parser)
            else:
                # Show type selection dialog
                return _show_remove_type_dialog(main_window)
        
        return False

    except Exception as e:
        main_window.log_message(f"❌ Remove via failed: {str(e)}")
        return False

def remove_via_ide_filter(main_window, ide_parser: IDEParser) -> bool: #vers 1
    """Remove entries filtered by IDE parser results"""
    try:
        if not ide_parser.models:
            main_window.log_message("⚠️ No models found in IDE file")
            return False

        # Create model name lookup from IDE
        ide_models = set()
        for model in ide_parser.models:
            model_name = model['name'].lower()
            ide_models.add(f"{model_name}.dff")
            ide_models.add(f"{model_name}.txd")
            # Also check for COL files
            ide_models.add(f"{model_name}.col")

        # Find matching entries
        entries_to_remove = []
        all_entries = main_window.current_img.entries
        
        for entry in all_entries:
            entry_name = entry.name.lower()
            if entry_name in ide_models:
                entries_to_remove.append(entry)

        if not entries_to_remove:
            QMessageBox.information(main_window, "No Matches", 
                                  f"None of the entries match the IDE file.\n"
                                  f"Total entries: {len(all_entries)}\n"
                                  f"IDE models: {len(ide_parser.models)} models")
            return False

        main_window.log_message(f"📋 Found {len(entries_to_remove)} entries matching IDE file")
        
        # Confirm removal
        if not _confirm_removal(main_window, entries_to_remove, "IDE-matched"):
            return False
        
        return _process_removal_with_tracking(main_window, entries_to_remove)

    except Exception as e:
        main_window.log_message(f"❌ IDE filter removal failed: {str(e)}")
        return False

def remove_via_type_filter(main_window, file_types: List[str]) -> bool: #vers 1
    """Remove entries filtered by file type"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            return False

        all_entries = main_window.current_img.entries
        if not all_entries:
            return False

        # Filter by type
        file_types_lower = [ft.lower() for ft in file_types]
        entries_to_remove = []
        
        for entry in all_entries:
            entry_ext = os.path.splitext(entry.name)[1].lower().lstrip('.')
            if entry_ext in file_types_lower:
                entries_to_remove.append(entry)

        if not entries_to_remove:
            main_window.log_message(f"⚠️ No entries found matching types: {', '.join(file_types)}")
            return False

        main_window.log_message(f"📋 Found {len(entries_to_remove)} entries matching types: {', '.join(file_types)}")
        
        # Confirm removal
        if not _confirm_removal(main_window, entries_to_remove, f"type '{', '.join(file_types)}'"):
            return False
        
        return _process_removal_with_tracking(main_window, entries_to_remove)

    except Exception as e:
        main_window.log_message(f"❌ Type filter removal failed: {str(e)}")
        return False

def remove_via_rw_filter(main_window, rw_versions: List[str]) -> bool: #vers 1
    """Remove entries filtered by RenderWare version"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            return False

        all_entries = main_window.current_img.entries
        if not all_entries:
            return False

        # Filter by RW version
        entries_to_remove = []
        
        for entry in all_entries:
            try:
                entry_data = entry.get_data()
                if entry_data and len(entry_data) >= 12:
                    file_format, version_desc, version_value = detect_rw_file_format(entry_data, entry.name)
                    
                    # Check if this version matches our filter
                    if version_desc in rw_versions or str(version_value) in rw_versions:
                        entries_to_remove.append(entry)
                        
            except Exception:
                continue  # Skip entries we can't read

        if not entries_to_remove:
            main_window.log_message(f"⚠️ No entries found matching RW versions: {', '.join(rw_versions)}")
            return False

        main_window.log_message(f"📋 Found {len(entries_to_remove)} entries matching RW versions: {', '.join(rw_versions)}")
        
        # Confirm removal
        if not _confirm_removal(main_window, entries_to_remove, f"RW version '{', '.join(rw_versions)}'"):
            return False
        
        return _process_removal_with_tracking(main_window, entries_to_remove)

    except Exception as e:
        main_window.log_message(f"❌ RW filter removal failed: {str(e)}")
        return False

def remove_via_name_pattern(main_window, pattern: str, case_sensitive: bool = False) -> bool: #vers 1
    """Remove entries matching name pattern"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            return False

        all_entries = main_window.current_img.entries
        if not all_entries:
            return False

        # Filter by name pattern
        entries_to_remove = []
        search_pattern = pattern if case_sensitive else pattern.lower()
        
        for entry in all_entries:
            entry_name = entry.name if case_sensitive else entry.name.lower()
            if search_pattern in entry_name:
                entries_to_remove.append(entry)

        if not entries_to_remove:
            main_window.log_message(f"⚠️ No entries found matching pattern: '{pattern}'")
            return False

        main_window.log_message(f"📋 Found {len(entries_to_remove)} entries matching pattern: '{pattern}'")
        
        # Confirm removal
        if not _confirm_removal(main_window, entries_to_remove, f"pattern '{pattern}'"):
            return False
        
        return _process_removal_with_tracking(main_window, entries_to_remove)

    except Exception as e:
        main_window.log_message(f"❌ Pattern removal failed: {str(e)}")
        return False

def _show_remove_type_dialog(main_window) -> bool: #vers 1
    """Show dialog for selecting removal type when no IDE is used"""
    try:
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem
        
        dialog = QDialog(main_window)
        dialog.setWindowTitle("Remove Entries by Type")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        # Instructions
        label = QLabel("Select file types to remove:")
        layout.addWidget(label)
        
        # Type list
        type_list = QListWidget()
        type_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        
        # Add common types
        types = ['DFF', 'TXD', 'COL', 'IFP', 'WAV', 'MP3', 'DAT', 'IPL']
        for file_type in types:
            item = QListWidgetItem(f"{file_type} files")
            item.setData(Qt.ItemDataRole.UserRole, file_type.lower())
            type_list.addItem(item)
        
        layout.addWidget(type_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        ok_btn = QPushButton("Remove Selected Types")
        ok_btn.clicked.connect(dialog.accept)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        # Show dialog
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected_types = []
            for i in range(type_list.count()):
                item = type_list.item(i)
                if item.isSelected():
                    selected_types.append(item.data(Qt.ItemDataRole.UserRole))
            
            if selected_types:
                return remove_via_type_filter(main_window, selected_types)
        
        return False
        
    except Exception as e:
        main_window.log_message(f"❌ Remove type dialog failed: {str(e)}")
        return False

def _confirm_removal(main_window, entries_to_remove: List, filter_description: str) -> bool: #vers 1
    """Confirm removal with user"""
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
        main_window.log_message(f"❌ Confirmation dialog failed: {str(e)}")
        return False

def _process_removal_with_tracking(main_window, entries_to_remove: List) -> bool: #vers 1
    """Process removal with RW version tracking and progress"""
    try:
        total_entries = len(entries_to_remove)
        removed_count = 0
        failed_count = 0
        rw_stats = {}

        # Show progress
        show_progress(main_window, 0, f"Removing {total_entries} entries...")

        for i, entry in enumerate(entries_to_remove):
            try:
                # Update progress
                progress = int((i / total_entries) * 100)
                show_progress(main_window, progress, f"Removing {entry.name}...")

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

                # Remove entry using existing functions
                if hasattr(main_window, 'remove_entry_safe'):
                    success = main_window.remove_entry_safe(main_window.current_img, entry)
                elif hasattr(main_window.current_img, 'remove_entry'):
                    success = main_window.current_img.remove_entry(entry)
                else:
                    # Fallback to direct removal
                    if entry in main_window.current_img.entries:
                        main_window.current_img.entries.remove(entry)
                        success = True
                    else:
                        success = False

                if success:
                    removed_count += 1
                    main_window.log_message(f"🗑️ Removed: {entry.name}{rw_info}")
                else:
                    failed_count += 1
                    main_window.log_message(f"❌ Failed to remove: {entry.name}")

            except Exception as e:
                failed_count += 1
                main_window.log_message(f"❌ Error removing {entry.name}: {str(e)}")

        # Hide progress
        hide_progress(main_window)

        # Create summary
        _create_removal_summary(main_window, removed_count, failed_count, rw_stats)
        
        # Refresh table if successful removals
        if removed_count > 0:
            # Use existing table population functions
            if hasattr(main_window, 'refresh_table'):
                main_window.refresh_table()
            elif hasattr(main_window, 'populate_img_table_enhanced'):
                main_window.populate_img_table_enhanced(main_window.current_img)
            elif hasattr(main_window, 'populate_col_table_enhanced') and hasattr(main_window, 'current_col'):
                main_window.populate_col_table_enhanced(main_window.current_col)

        return removed_count > 0

    except Exception as e:
        hide_progress(main_window)
        main_window.log_message(f"❌ Removal processing failed: {str(e)}")
        return False

def _create_removal_summary(main_window, removed: int, failed: int, rw_stats: Dict): #vers 1
    """Create detailed removal summary with RW statistics"""
    try:
        # Basic summary
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
        main_window.log_message(f"⚠️ Error creating removal summary: {str(e)}")

def integrate_remove_via_functions(main_window) -> bool: #vers 1
    """Integrate remove via functions into main window"""
    try:
        # Add remove via methods
        main_window.remove_via_entries_function = lambda: remove_via_entries_function(main_window)
        main_window.remove_via_ide = lambda parser: remove_via_ide_filter(main_window, parser)
        main_window.remove_via_type = lambda types: remove_via_type_filter(main_window, types)
        main_window.remove_via_rw = lambda versions: remove_via_rw_filter(main_window, versions)
        main_window.remove_via_pattern = lambda pattern, case_sensitive=False: remove_via_name_pattern(main_window, pattern, case_sensitive)

        # Aliases for backward compatibility
        main_window.remove_via_function = main_window.remove_via_entries_function
        main_window.remove_via = main_window.remove_via_entries_function

        if hasattr(main_window, 'log_message'):
            main_window.log_message("✅ Remove Via functions integrated")
            main_window.log_message("   • IDE parser filtering")
            main_window.log_message("   • RW version detection")
            main_window.log_message("   • Type-based filtering") 
            main_window.log_message("   • Pattern matching")
            main_window.log_message("   • GUI dialog support")

        return True

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Remove Via integration failed: {str(e)}")
        return False

# Export functions
__all__ = [
    'remove_via_entries_function',
    'remove_via_ide_filter',
    'remove_via_type_filter',
    'remove_via_rw_filter',
    'remove_via_name_pattern',
    'integrate_remove_via_functions'
]
