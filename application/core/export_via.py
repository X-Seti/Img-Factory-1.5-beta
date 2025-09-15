#this belongs in Core/export_via.py - Version: 1
# X-Seti - September11 2025 - IMG Factory 1.5 - Export Via Functions

"""
Export Via Functions - Enhanced export operations using IDE parser, RW detection and GUI dialogs
Uses existing components: methods/ide_parser_functions.py, core/rw_versions.py, gui/ide_dialog.py
"""

import os
from typing import Optional, List, Dict, Any, Tuple
from PyQt6.QtWidgets import QMessageBox, QFileDialog, QProgressDialog
from PyQt6.QtCore import Qt

# Import existing components - updated paths
from shared.ide_parser_functions import IDEParser, parse_ide_file
from application.core.rw_versions import detect_rw_file_format, get_rw_version_name, is_valid_rw_version
from gui.ide_dialog import IDEDialog, create_ide_dialog
from shared.progress_functions import show_progress, hide_progress

##Methods list -
# export_selected_via
# export_via_ide_filter
# export_via_type_filter
# export_via_rw_filter
# _get_selected_entries
# _validate_export_destination
# _process_export_with_rw_info
# _create_export_summary
# integrate_export_via_functions

def export_selected_via(main_window): #vers 1
    """Main export via function - shows dialog for export method selection"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first")
            return False

        # Get selected entries
        selected_entries = _get_selected_entries(main_window)
        if not selected_entries:
            QMessageBox.warning(main_window, "No Selection", "Please select entries to export")
            return False

        # Create IDE dialog for export operation
        dialog = create_ide_dialog(main_window, "export")
        if not dialog:
            main_window.log_message("❌ Failed to create export dialog")
            return False

        # Show dialog and get result
        if dialog.exec() == dialog.DialogCode.Accepted:
            export_folder = dialog.get_export_folder()
            if not export_folder:
                QMessageBox.warning(main_window, "No Folder", "Please select an export folder")
                return False

            parser = dialog.get_ide_parser()
            if parser and parser.models:
                return export_via_ide_filter(main_window, selected_entries, parser, export_folder)
            else:
                # Direct export without IDE filtering
                return _process_export_with_rw_info(main_window, selected_entries, export_folder)
        
        return False

    except Exception as e:
        main_window.log_message(f"❌ Export via failed: {str(e)}")
        return False

def export_via_ide_filter(main_window, selected_entries: List, ide_parser: IDEParser, export_folder: str) -> bool: #vers 1
    """Export entries filtered by IDE parser results"""
    try:
        if not ide_parser.models:
            main_window.log_message("⚠️ No models found in IDE file")
            return _process_export_with_rw_info(main_window, selected_entries, export_folder)

        # Create model name lookup from IDE
        ide_models = set()
        for model in ide_parser.models:
            model_name = model['name'].lower()
            ide_models.add(f"{model_name}.dff")
            ide_models.add(f"{model_name}.txd")

        # Filter selected entries based on IDE
        filtered_entries = []
        for entry in selected_entries:
            entry_name = entry.name.lower()
            if entry_name in ide_models:
                filtered_entries.append(entry)

        if not filtered_entries:
            QMessageBox.information(main_window, "No Matches", 
                                  f"None of the selected entries match the IDE file.\n"
                                  f"Selected: {len(selected_entries)} entries\n"
                                  f"IDE models: {len(ide_parser.models)} models")
            return False

        main_window.log_message(f"📋 Filtered {len(selected_entries)} entries to {len(filtered_entries)} IDE matches")
        
        return _process_export_with_rw_info(main_window, filtered_entries, export_folder)

    except Exception as e:
        main_window.log_message(f"❌ IDE filter export failed: {str(e)}")
        return False

def export_via_type_filter(main_window, file_types: List[str], export_folder: str) -> bool: #vers 1
    """Export entries filtered by file type"""
    try:
        # Get all entries
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            return False

        all_entries = main_window.current_img.entries
        if not all_entries:
            return False

        # Filter by type
        file_types_lower = [ft.lower() for ft in file_types]
        filtered_entries = []
        
        for entry in all_entries:
            entry_ext = os.path.splitext(entry.name)[1].lower().lstrip('.')
            if entry_ext in file_types_lower:
                filtered_entries.append(entry)

        if not filtered_entries:
            main_window.log_message(f"⚠️ No entries found matching types: {', '.join(file_types)}")
            return False

        main_window.log_message(f"📋 Found {len(filtered_entries)} entries matching types: {', '.join(file_types)}")
        
        return _process_export_with_rw_info(main_window, filtered_entries, export_folder)

    except Exception as e:
        main_window.log_message(f"❌ Type filter export failed: {str(e)}")
        return False

def export_via_rw_filter(main_window, rw_versions: List[str], export_folder: str) -> bool: #vers 1
    """Export entries filtered by RenderWare version"""
    try:
        # Get all entries
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            return False

        all_entries = main_window.current_img.entries
        if not all_entries:
            return False

        # Filter by RW version
        filtered_entries = []
        
        for entry in all_entries:
            # Get entry data for RW detection
            try:
                entry_data = entry.get_data()
                if entry_data and len(entry_data) >= 12:
                    file_format, version_desc, version_value = detect_rw_file_format(entry_data, entry.name)
                    
                    # Check if this version matches our filter
                    if version_desc in rw_versions or str(version_value) in rw_versions:
                        filtered_entries.append(entry)
                        
            except Exception:
                continue  # Skip entries we can't read

        if not filtered_entries:
            main_window.log_message(f"⚠️ No entries found matching RW versions: {', '.join(rw_versions)}")
            return False

        main_window.log_message(f"📋 Found {len(filtered_entries)} entries matching RW versions: {', '.join(rw_versions)}")
        
        return _process_export_with_rw_info(main_window, filtered_entries, export_folder)

    except Exception as e:
        main_window.log_message(f"❌ RW filter export failed: {str(e)}")
        return False

def _get_selected_entries(main_window) -> Optional[List]: #vers 1
    """Get selected entries from table"""
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
        
        return selected_entries if selected_entries else None
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Error getting selected entries: {str(e)}")
        return None

def _validate_export_destination(main_window, export_folder: str) -> bool: #vers 1
    """Validate export destination folder"""
    try:
        # Check folder exists
        if not os.path.exists(export_folder):
            try:
                os.makedirs(export_folder, exist_ok=True)
                main_window.log_message(f"📁 Created export folder: {export_folder}")
            except Exception as e:
                main_window.log_message(f"❌ Cannot create export folder: {str(e)}")
                return False
        
        # Check write permissions
        test_file = os.path.join(export_folder, 'test_write.tmp')
        try:
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            return True
        except Exception as e:
            main_window.log_message(f"❌ No write permission to export folder: {str(e)}")
            return False
            
    except Exception as e:
        main_window.log_message(f"❌ Export validation failed: {str(e)}")
        return False

def _process_export_with_rw_info(main_window, entries_to_export: List, export_folder: str) -> bool: #vers 1
    """Process export with RW version detection and logging"""
    try:
        if not _validate_export_destination(main_window, export_folder):
            return False

        total_entries = len(entries_to_export)
        exported_count = 0
        failed_count = 0
        rw_stats = {}

        # Show progress
        show_progress(main_window, 0, f"Exporting {total_entries} entries...")

        for i, entry in enumerate(entries_to_export):
            try:
                # Update progress
                progress = int((i / total_entries) * 100)
                show_progress(main_window, progress, f"Exporting {entry.name}...")

                # Get entry data
                entry_data = entry.get_data()
                if not entry_data:
                    failed_count += 1
                    main_window.log_message(f"❌ No data for: {entry.name}")
                    continue

                # Detect RW version
                file_format, version_desc, version_value = detect_rw_file_format(entry_data, entry.name)
                
                # Track RW statistics
                if version_desc not in rw_stats:
                    rw_stats[version_desc] = 0
                rw_stats[version_desc] += 1

                # Export file
                export_path = os.path.join(export_folder, entry.name)
                
                # Check for overwrite
                if os.path.exists(export_path):
                    # Could add overwrite dialog here
                    pass

                with open(export_path, 'wb') as f:
                    f.write(entry_data)

                exported_count += 1
                
                # Log with RW info
                rw_info = f" ({file_format} {version_desc})" if is_valid_rw_version(version_value) else ""
                main_window.log_message(f"✅ Exported: {entry.name}{rw_info}")

            except Exception as e:
                failed_count += 1
                main_window.log_message(f"❌ Failed to export {entry.name}: {str(e)}")

        # Hide progress
        hide_progress(main_window)

        # Create summary
        _create_export_summary(main_window, exported_count, failed_count, rw_stats, export_folder)
        
        return exported_count > 0

    except Exception as e:
        hide_progress(main_window)
        main_window.log_message(f"❌ Export processing failed: {str(e)}")
        return False

def _create_export_summary(main_window, exported: int, failed: int, rw_stats: Dict, folder: str): #vers 1
    """Create detailed export summary with RW statistics"""
    try:
        # Basic summary
        main_window.log_message(f"📋 Export complete: {exported} exported, {failed} failed")
        main_window.log_message(f"📁 Export location: {folder}")
        
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
            summary_text += f"Location: {folder}\n\n"
            
            if rw_stats:
                summary_text += "RenderWare Versions:\n"
                for version, count in sorted(rw_stats.items()):
                    summary_text += f"• {version}: {count} files\n"
            
            QMessageBox.information(main_window, "Export Complete", summary_text)
        
    except Exception as e:
        main_window.log_message(f"⚠️ Error creating export summary: {str(e)}")

def integrate_export_via_functions(main_window) -> bool: #vers 1
    """Integrate export via functions into main window"""
    try:
        # Add export via methods
        main_window.export_selected_via = lambda: export_selected_via(main_window)
        main_window.export_via_ide = lambda entries, parser, folder: export_via_ide_filter(main_window, entries, parser, folder)
        main_window.export_via_type = lambda types, folder: export_via_type_filter(main_window, types, folder)
        main_window.export_via_rw = lambda versions, folder: export_via_rw_filter(main_window, versions, folder)

        # Aliases for backward compatibility
        main_window.export_via_function = main_window.export_selected_via
        main_window.export_via = main_window.export_selected_via

        if hasattr(main_window, 'log_message'):
            main_window.log_message("✅ Export Via functions integrated")
            main_window.log_message("   • IDE parser filtering")
            main_window.log_message("   • RW version detection")
            main_window.log_message("   • Type-based filtering")
            main_window.log_message("   • GUI dialog support")

        return True

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Export Via integration failed: {str(e)}")
        return False

# Export functions
__all__ = [
    'export_selected_via',
    'export_via_ide_filter',
    'export_via_type_filter',
    'export_via_rw_filter',
    'integrate_export_via_functions'
]
