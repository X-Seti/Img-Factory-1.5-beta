#this belongs in application.shared/ui_interaction_handlers.py - Version: 1
# X-Seti - September12 2025 - IMG Factory 1.5 - UI Interaction Handlers

"""
UI Interaction Handlers - Event handlers and UI interactions for IMG Factory
Ported from IMG Editor's ui_interaction_handlers.py and adapted for IMG Factory
Provides unified event handling for file operations, import/export, and user interactions
"""

import os
from typing import Optional, List, Dict, Any, Callable
from PyQt6.QtWidgets import QFileDialog, QDialog, QMessageBox, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QGroupBox
from PyQt6.QtCore import pyqtSlot

##Methods list -
# setup_ui_interaction_handlers
# handle_open_img_file
# handle_open_multiple_imgs
# handle_create_new_img
# handle_close_current_img
# handle_import_files
# handle_export_selected
# handle_export_all
# handle_delete_selected
# handle_img_loaded_event
# handle_entries_updated_event
# show_import_preview_dialog
# show_export_preview_dialog
# integrate_with_existing_handlers

def setup_ui_interaction_handlers(main_window) -> bool: #vers 1
    """Setup UI interaction handlers for IMG Factory"""
    try:
        # File operation handlers
        main_window.handle_open_img_file = lambda: handle_open_img_file(main_window)
        main_window.handle_open_multiple_imgs = lambda: handle_open_multiple_imgs(main_window)
        main_window.handle_create_new_img = lambda: handle_create_new_img(main_window)
        main_window.handle_close_current_img = lambda: handle_close_current_img(main_window)
        
        # Import/Export handlers
        main_window.handle_import_files = lambda: handle_import_files(main_window)
        main_window.handle_export_selected = lambda: handle_export_selected(main_window)
        main_window.handle_export_all = lambda: handle_export_all(main_window)
        
        # Entry operation handlers
        main_window.handle_delete_selected = lambda: handle_delete_selected(main_window)
        main_window.handle_extract_selected = lambda: handle_extract_selected(main_window)
        
        # Event handlers for IMG operations
        main_window.on_img_loaded = lambda img_file: handle_img_loaded_event(main_window, img_file)
        main_window.on_img_closed = lambda: handle_img_closed_event(main_window)
        main_window.on_entries_updated = lambda entries: handle_entries_updated_event(main_window, entries)
        
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ UI handlers setup failed: {str(e)}")
        return False


def handle_open_img_file(main_window) -> bool: #vers 1
    """Handle opening a single IMG file"""
    try:
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            main_window,
            "Open IMG Archive",
            os.path.expanduser("~/Desktop"),
            "IMG Archives (*.img);;All Files (*.*)"
        )
        
        if file_path:
            main_window.log_message(f"📂 Opening IMG file: {os.path.basename(file_path)}")
            
            # Use tabs system if available
            if hasattr(main_window, 'open_img_in_new_tab'):
                return main_window.open_img_in_new_tab(file_path)
            elif hasattr(main_window, 'open_img_file'):
                return main_window.open_img_file(file_path)
            else:
                main_window.log_message("❌ No IMG opening function available")
                return False
        
        return False
        
    except Exception as e:
        main_window.log_message(f"❌ Open IMG file failed: {str(e)}")
        return False


def handle_open_multiple_imgs(main_window) -> bool: #vers 1
    """Handle opening multiple IMG files"""
    try:
        file_dialog = QFileDialog()
        file_paths, _ = file_dialog.getOpenFileNames(
            main_window,
            "Open Multiple IMG Archives",
            os.path.expanduser("~/Desktop"),
            "IMG Archives (*.img);;All Files (*.*)"
        )
        
        if file_paths:
            main_window.log_message(f"📂 Opening {len(file_paths)} IMG files")
            
            success_count = 0
            for file_path in file_paths:
                if hasattr(main_window, 'open_img_in_new_tab'):
                    if main_window.open_img_in_new_tab(file_path):
                        success_count += 1
                elif hasattr(main_window, 'open_img_file'):
                    if main_window.open_img_file(file_path):
                        success_count += 1
            
            main_window.log_message(f"✅ Successfully opened {success_count}/{len(file_paths)} IMG files")
            return success_count > 0
        
        return False
        
    except Exception as e:
        main_window.log_message(f"❌ Open multiple IMG files failed: {str(e)}")
        return False


def handle_create_new_img(main_window) -> bool: #vers 1
    """Handle creating a new IMG file"""
    try:
        file_path, _ = QFileDialog.getSaveFileName(
            main_window,
            "Create New IMG File",
            os.path.expanduser("~/Desktop/new_archive.img"),
            "IMG Files (*.img);;All Files (*.*)"
        )
        
        if file_path:
            main_window.log_message(f"📁 Creating new IMG file: {os.path.basename(file_path)}")
            
            if hasattr(main_window, 'create_new_img'):
                return main_window.create_new_img(file_path)
            else:
                main_window.log_message("❌ No create IMG function available")
                return False
        
        return False
        
    except Exception as e:
        main_window.log_message(f"❌ Create new IMG failed: {str(e)}")
        return False


def handle_close_current_img(main_window) -> bool: #vers 1
    """Handle closing current IMG file"""
    try:
        if hasattr(main_window, 'close_img_tab'):
            return main_window.close_img_tab()
        elif hasattr(main_window, 'close_img_file'):
            return main_window.close_img_file()
        else:
            main_window.log_message("❌ No close IMG function available")
            return False
        
    except Exception as e:
        main_window.log_message(f"❌ Close IMG failed: {str(e)}")
        return False


def handle_import_files(main_window) -> bool: #vers 1
    """Handle importing files to current IMG"""
    try:
        # Check if IMG is loaded
        current_archive = None
        if hasattr(main_window, 'get_current_img_archive'):
            current_archive = main_window.get_current_img_archive()
        
        if not current_archive:
            QMessageBox.warning(
                main_window,
                "No IMG Open",
                "Please open an IMG file before importing."
            )
            return False
        
        # Get files to import
        file_dialog = QFileDialog()
        file_paths, _ = file_dialog.getOpenFileNames(
            main_window,
            "Select Files to Import",
            os.path.expanduser("~/Desktop"),
            "Game Assets (*.dff *.txd *.col *.ide *.ipl *.dat *.wav);;All Files (*.*)"
        )
        
        if not file_paths:
            return False
        
        # Show import preview if available
        if hasattr(main_window, 'show_import_preview'):
            if not show_import_preview_dialog(main_window, file_paths):
                return False
        
        # Perform import
        main_window.log_message(f"📥 Importing {len(file_paths)} files")
        
        if hasattr(main_window, 'import_files'):
            return main_window.import_files(file_paths)
        else:
            main_window.log_message("❌ No import function available")
            return False
        
    except Exception as e:
        main_window.log_message(f"❌ Import files failed: {str(e)}")
        return False


def handle_export_selected(main_window) -> bool: #vers 1
    """Handle exporting selected entries"""
    try:
        # Check if IMG is loaded
        current_archive = None
        if hasattr(main_window, 'get_current_img_archive'):
            current_archive = main_window.get_current_img_archive()
        
        if not current_archive:
            QMessageBox.warning(
                main_window,
                "No IMG Open",
                "Please open an IMG file before exporting."
            )
            return False
        
        # Get selected entries
        selected_entries = []
        if hasattr(main_window, 'get_selected_entries'):
            selected_entries = main_window.get_selected_entries()
        
        if not selected_entries:
            QMessageBox.warning(
                main_window,
                "No Selection",
                "Please select entries to export."
            )
            return False
        
        # Get export directory
        export_dir = QFileDialog.getExistingDirectory(
            main_window,
            "Select Export Directory",
            os.path.expanduser("~/Desktop"),
            QFileDialog.Option.ShowDirsOnly
        )
        
        if not export_dir:
            return False
        
        # Perform export
        main_window.log_message(f"📤 Exporting {len(selected_entries)} entries")
        
        if hasattr(main_window, 'export_selected'):
            return main_window.export_selected(export_dir)
        else:
            main_window.log_message("❌ No export selected function available")
            return False
        
    except Exception as e:
        main_window.log_message(f"❌ Export selected failed: {str(e)}")
        return False


def handle_export_all(main_window) -> bool: #vers 1
    """Handle exporting all entries"""
    try:
        # Check if IMG is loaded
        current_archive = None
        if hasattr(main_window, 'get_current_img_archive'):
            current_archive = main_window.get_current_img_archive()
        
        if not current_archive:
            QMessageBox.warning(
                main_window,
                "No IMG Open",
                "Please open an IMG file before exporting."
            )
            return False
        
        # Get export directory
        export_dir = QFileDialog.getExistingDirectory(
            main_window,
            "Select Export Directory for All Entries",
            os.path.expanduser("~/Desktop"),
            QFileDialog.Option.ShowDirsOnly
        )
        
        if not export_dir:
            return False
        
        # Confirm export all
        entry_count = len(getattr(current_archive, 'entries', []))
        reply = QMessageBox.question(
            main_window,
            "Export All Entries",
            f"Export all {entry_count} entries to:\n{export_dir}\n\nThis may take some time. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return False
        
        # Perform export
        main_window.log_message(f"📤 Exporting all {entry_count} entries")
        
        if hasattr(main_window, 'export_all'):
            return main_window.export_all(export_dir)
        else:
            main_window.log_message("❌ No export all function available")
            return False
        
    except Exception as e:
        main_window.log_message(f"❌ Export all failed: {str(e)}")
        return False


def handle_delete_selected(main_window) -> bool: #vers 1
    """Handle deleting selected entries"""
    try:
        # Get selected entries
        selected_entries = []
        if hasattr(main_window, 'get_selected_entries'):
            selected_entries = main_window.get_selected_entries()
        
        if not selected_entries:
            QMessageBox.warning(
                main_window,
                "No Selection",
                "Please select entries to delete."
            )
            return False
        
        # Check if entries are locked
        if hasattr(main_window, 'check_operation_allowed'):
            if not main_window.check_operation_allowed("Delete"):
                return False
        
        # Confirm deletion
        selected_names = [getattr(entry, 'name', str(entry)) for entry in selected_entries]
        name_list = '\n'.join([f"• {name}" for name in selected_names[:10]])
        if len(selected_names) > 10:
            name_list += f"\n... and {len(selected_names) - 10} more"
        
        reply = QMessageBox.question(
            main_window,
            "Delete Entries",
            f"Delete {len(selected_entries)} selected entries?\n\n{name_list}\n\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return False
        
        # Perform deletion
        main_window.log_message(f"🗑️ Deleting {len(selected_entries)} entries")
        
        if hasattr(main_window, 'remove_selected'):
            return main_window.remove_selected()
        else:
            main_window.log_message("❌ No remove selected function available")
            return False
        
    except Exception as e:
        main_window.log_message(f"❌ Delete selected failed: {str(e)}")
        return False


def handle_extract_selected(main_window) -> bool: #vers 1
    """Handle extracting selected entries (same as export selected)"""
    return handle_export_selected(main_window)


def handle_img_loaded_event(main_window, img_archive) -> bool: #vers 1
    """Handle IMG loaded event"""
    try:
        # Update file info panel
        if hasattr(main_window, 'file_info_panel'):
            # Get IMG info
            img_info = {
                'path': getattr(img_archive, 'file_path', 'Unknown'),
                'version': getattr(img_archive, 'version', 'Unknown'),
                'entry_count': len(getattr(img_archive, 'entries', [])),
                'total_size': sum(getattr(entry, 'size', 0) for entry in getattr(img_archive, 'entries', [])),
                'modified': getattr(img_archive, 'modified', False)
            }
            
            # Get RW summary if available
            rw_summary = None
            if hasattr(main_window, 'get_rw_version_summary'):
                rw_summary = main_window.get_rw_version_summary(img_archive)
            
            main_window.file_info_panel.update_info(img_info, rw_summary)
        
        # Populate table with entries
        if hasattr(main_window, 'populate_img_table'):
            main_window.populate_img_table(img_archive)
        
        # Update window title
        if hasattr(img_archive, 'file_path'):
            file_name = os.path.basename(img_archive.file_path)
            main_window.setWindowTitle(f"IMG Factory 1.5 - {file_name}")
        
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ IMG loaded event failed: {str(e)}")
        return False


def handle_img_closed_event(main_window) -> bool: #vers 1
    """Handle IMG closed event"""
    try:
        # Reset file info panel
        if hasattr(main_window, 'file_info_panel'):
            main_window.file_info_panel.update_info(None)
        
        # Clear entries table
        if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'table'):
            main_window.gui_layout.table.setRowCount(0)
        
        # Reset window title
        main_window.setWindowTitle("IMG Factory 1.5")
        
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ IMG closed event failed: {str(e)}")
        return False


def handle_entries_updated_event(main_window, entries) -> bool: #vers 1
    """Handle entries updated event"""
    try:
        # Get current IMG archive
        current_archive = None
        if hasattr(main_window, 'get_current_img_archive'):
            current_archive = main_window.get_current_img_archive()
        
        if current_archive:
            # Update file info panel
            if hasattr(main_window, 'file_info_panel'):
                img_info = {
                    'path': getattr(current_archive, 'file_path', 'Unknown'),
                    'version': getattr(current_archive, 'version', 'Unknown'),
                    'entry_count': len(entries),
                    'total_size': sum(getattr(entry, 'size', 0) for entry in entries),
                    'modified': getattr(current_archive, 'modified', True)  # Assume modified if entries updated
                }
                
                # Get RW summary if available
                rw_summary = None
                if hasattr(main_window, 'get_rw_version_summary'):
                    rw_summary = main_window.get_rw_version_summary(current_archive)
                
                main_window.file_info_panel.update_info(img_info, rw_summary)
            
            # Refresh entries table
            if hasattr(main_window, 'populate_img_table'):
                main_window.populate_img_table(current_archive)
        
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Entries updated event failed: {str(e)}")
        return False


def show_import_preview_dialog(main_window, file_paths: List[str]) -> bool: #vers 1
    """Show import preview dialog"""
    try:
        dialog = QDialog(main_window)
        dialog.setWindowTitle("Import Preview")
        dialog.setMinimumSize(500, 400)
        
        layout = QVBoxLayout(dialog)
        
        # Info header
        info_label = QLabel(f"Ready to import {len(file_paths)} files:")
        layout.addWidget(info_label)
        
        # File list
        file_list = QTextEdit()
        file_list.setReadOnly(True)
        file_list.setMaximumHeight(200)
        
        file_text = ""
        for file_path in file_paths[:20]:  # Show first 20 files
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            size_text = _format_size(file_size)
            file_text += f"• {file_name} ({size_text})\n"
        
        if len(file_paths) > 20:
            file_text += f"... and {len(file_paths) - 20} more files"
        
        file_list.setPlainText(file_text)
        layout.addWidget(file_list)
        
        # Existing files warning
        existing_files = _check_existing_files(main_window, file_paths)
        if existing_files:
            warning_label = QLabel(f"⚠️ {len(existing_files)} files already exist and will be replaced:")
            warning_label.setStyleSheet("color: orange; font-weight: bold;")
            layout.addWidget(warning_label)
            
            existing_list = QTextEdit()
            existing_list.setReadOnly(True)
            existing_list.setMaximumHeight(100)
            existing_text = "\n".join([f"• {name}" for name in existing_files[:10]])
            if len(existing_files) > 10:
                existing_text += f"\n... and {len(existing_files) - 10} more"
            existing_list.setPlainText(existing_text)
            layout.addWidget(existing_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        proceed_btn = QPushButton("Proceed with Import")
        proceed_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(proceed_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        return dialog.exec() == QDialog.DialogCode.Accepted
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Import preview failed: {str(e)}")
        return True  # Proceed anyway


def show_export_preview_dialog(main_window, entries: List, export_dir: str) -> bool: #vers 1
    """Show export preview dialog"""
    try:
        dialog = QDialog(main_window)
        dialog.setWindowTitle("Export Preview")
        dialog.setMinimumSize(500, 300)
        
        layout = QVBoxLayout(dialog)
        
        # Info header
        info_label = QLabel(f"Ready to export {len(entries)} entries to:\n{export_dir}")
        layout.addWidget(info_label)
        
        # Entry list
        entry_list = QTextEdit()
        entry_list.setReadOnly(True)
        entry_list.setMaximumHeight(200)
        
        entry_text = ""
        total_size = 0
        
        for entry in entries[:20]:  # Show first 20 entries
            entry_name = getattr(entry, 'name', 'Unknown')
            entry_size = getattr(entry, 'size', 0)
            total_size += entry_size
            size_text = _format_size(entry_size)
            entry_text += f"• {entry_name} ({size_text})\n"
        
        if len(entries) > 20:
            # Calculate remaining size
            remaining_size = sum(getattr(e, 'size', 0) for e in entries[20:])
            total_size += remaining_size
            entry_text += f"... and {len(entries) - 20} more entries"
        
        entry_list.setPlainText(entry_text)
        layout.addWidget(entry_list)
        
        # Total size info
        total_label = QLabel(f"Total size: {_format_size(total_size)}")
        total_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(total_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        proceed_btn = QPushButton("Proceed with Export")
        proceed_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(proceed_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        return dialog.exec() == QDialog.DialogCode.Accepted
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Export preview failed: {str(e)}")
        return True  # Proceed anyway


def _check_existing_files(main_window, file_paths: List[str]) -> List[str]: #vers 1
    """Check which files already exist in current IMG"""
    try:
        existing_files = []
        
        # Get current archive
        current_archive = None
        if hasattr(main_window, 'get_current_img_archive'):
            current_archive = main_window.get_current_img_archive()
        
        if not current_archive or not hasattr(current_archive, 'entries'):
            return existing_files
        
        # Get existing entry names
        existing_names = {getattr(entry, 'name', '').lower() for entry in current_archive.entries}
        
        # Check each file
        for file_path in file_paths:
            file_name = os.path.basename(file_path).lower()
            if file_name in existing_names:
                existing_files.append(os.path.basename(file_path))
        
        return existing_files
        
    except:
        return []


def _format_size(size_bytes: int) -> str: #vers 1
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 bytes"
    
    for unit in ['bytes', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            if unit == 'bytes':
                return f"{int(size_bytes)} {unit}"
            else:
                return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    
    return f"{size_bytes:.1f} TB"


def integrate_with_existing_handlers(main_window) -> bool: #vers 1
    """Integrate UI handlers with existing IMG Factory functions"""
    try:
        # Connect to existing button actions if gui_layout exists
        if hasattr(main_window, 'gui_layout'):
            # Connect file operation buttons
            button_mapping = {
                'open': 'handle_open_img_file',
                'create': 'handle_create_new_img', 
                'close': 'handle_close_current_img',
                'import': 'handle_import_files',
                'export': 'handle_export_selected',
                'remove': 'handle_delete_selected'
            }
            
            # Connect buttons to handlers
            for button_name, handler_name in button_mapping.items():
                if hasattr(main_window.gui_layout, f'{button_name}_button'):
                    button = getattr(main_window.gui_layout, f'{button_name}_button')
                    if hasattr(main_window, handler_name):
                        handler = getattr(main_window, handler_name)
                        button.clicked.connect(handler)
        
        # Connect table selection events
        if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'table'):
            table = main_window.gui_layout.table
            
            # Connect selection change to update UI
            def on_selection_changed():
                selected_count = len(table.selectedItems()) // table.columnCount()
                if hasattr(main_window, 'update_selection_status'):
                    main_window.update_selection_status(selected_count)
            
            table.selectionModel().selectionChanged.connect(on_selection_changed)
        
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Handler integration failed: {str(e)}")
        return False


def create_context_menu_handlers(main_window) -> Dict[str, Callable]: #vers 1
    """Create context menu handlers for table right-clicks"""
    try:
        handlers = {
            'export_entry': lambda: handle_export_selected(main_window),
            'delete_entry': lambda: handle_delete_selected(main_window),
            'rename_entry': lambda: handle_rename_selected(main_window),
            'properties': lambda: show_entry_properties(main_window)
        }
        
        return handlers
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Context menu handlers failed: {str(e)}")
        return {}


def handle_rename_selected(main_window) -> bool: #vers 1
    """Handle renaming selected entry"""
    try:
        # Get selected entries
        selected_entries = []
        if hasattr(main_window, 'get_selected_entries'):
            selected_entries = main_window.get_selected_entries()
        
        if len(selected_entries) != 1:
            QMessageBox.warning(
                main_window,
                "Invalid Selection", 
                "Please select exactly one entry to rename."
            )
            return False
        
        entry = selected_entries[0]
        current_name = getattr(entry, 'name', '')
        
        # Simple rename dialog
        from PyQt6.QtWidgets import QInputDialog
        new_name, ok = QInputDialog.getText(
            main_window,
            "Rename Entry",
            f"Enter new name for '{current_name}':",
            text=current_name
        )
        
        if ok and new_name and new_name != current_name:
            if hasattr(main_window, 'rename_entry'):
                return main_window.rename_entry(entry, new_name)
            else:
                main_window.log_message("❌ No rename function available")
                return False
        
        return False
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Rename failed: {str(e)}")
        return False


def show_entry_properties(main_window) -> bool: #vers 1
    """Show properties dialog for selected entry"""
    try:
        # Get selected entries
        selected_entries = []
        if hasattr(main_window, 'get_selected_entries'):
            selected_entries = main_window.get_selected_entries()
        
        if len(selected_entries) != 1:
            QMessageBox.warning(
                main_window,
                "Invalid Selection",
                "Please select exactly one entry to view properties."
            )
            return False
        
        entry = selected_entries[0]
        
        # Create properties dialog
        dialog = QDialog(main_window)
        dialog.setWindowTitle(f"Properties - {getattr(entry, 'name', 'Unknown')}")
        dialog.setMinimumSize(350, 250)
        
        layout = QVBoxLayout(dialog)
        
        # Entry properties
        props_text = f"""Entry Name: {getattr(entry, 'name', 'Unknown')}
File Size: {_format_size(getattr(entry, 'size', 0))}
File Offset: {getattr(entry, 'offset', 0):,} bytes
File Type: {os.path.splitext(getattr(entry, 'name', ''))[1].upper() or 'Unknown'}
"""
        
        # Add RW version if available
        if hasattr(entry, 'rw_version'):
            props_text += f"RW Version: {getattr(entry, 'rw_version', 'Unknown')}\n"
        
        # Add modification status
        if hasattr(entry, 'is_new'):
            props_text += f"Status: {'New Entry' if getattr(entry, 'is_new', False) else 'Original'}\n"
        
        props_label = QLabel(props_text)
        props_label.setStyleSheet("font-family: monospace; padding: 10px;")
        layout.addWidget(props_label)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.exec()
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Properties dialog failed: {str(e)}")
        return False