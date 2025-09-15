#this belongs in Core/rename.py - Version: 1
# X-Seti - September11 2025 - IMG Factory 1.5 - Rename Functions

"""
Rename Functions - Entry renaming operations with validation and batch processing
Handles single entry rename, batch rename with patterns, and name validation
"""

import os
import re
from typing import Optional, List, Dict, Any, Tuple
from PyQt6.QtWidgets import QMessageBox, QInputDialog, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget, QListWidgetItem

# Import from new structure
from shared.progress_functions import show_progress, update_progress, hide_progress, start_operation, complete_operation
from shared.populate_img_table import populate_img_table_enhanced, refresh_table

##Methods list -
# rename_selected_entry
# rename_multiple_entries
# batch_rename_with_pattern
# rename_entries_function
# validate_entry_name
# show_rename_dialog
# show_batch_rename_dialog
# _get_selected_entries
# _refresh_img_table
# integrate_rename_functions

def rename_selected_entry(main_window, new_name: str = None) -> bool: #vers 1
    """Rename single selected entry
    
    Args:
        main_window: Main window instance
        new_name: New name for entry (shows dialog if None)
        
    Returns:
        bool: True if rename successful
    """
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("❌ No IMG file open")
            return False

        # Get selected entries
        selected_entries = _get_selected_entries(main_window)
        if not selected_entries:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("⚠️ No entry selected for rename")
            return False

        if len(selected_entries) > 1:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("⚠️ Please select only one entry for rename")
            return False

        entry = selected_entries[0]
        old_name = entry.name

        # Get new name if not provided
        if new_name is None:
            new_name = show_rename_dialog(main_window, old_name)
            if not new_name:
                return False

        # Validate new name
        if not validate_entry_name(main_window, new_name, entry):
            return False

        # Perform rename using available methods
        success = False
        
        # Method 1: Use rename_entry_safe if available
        if hasattr(main_window, 'rename_entry_safe'):
            success = main_window.rename_entry_safe(main_window.current_img, entry, new_name)
        
        # Method 2: Direct rename
        elif hasattr(entry, 'name'):
            entry.name = new_name
            success = True
        
        if success:
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"✏️ Renamed: {old_name} → {new_name}")
            
            # Refresh table
            _refresh_img_table(main_window)
            return True
        else:
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"❌ Failed to rename: {old_name}")
            return False

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Rename error: {str(e)}")
        return False

def rename_multiple_entries(main_window, name_mapping: Dict[str, str]) -> Tuple[int, int]: #vers 1
    """Rename multiple entries using name mapping
    
    Args:
        main_window: Main window instance
        name_mapping: Dict mapping old names to new names
        
    Returns:
        Tuple[int, int]: (renamed_count, failed_count)
    """
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("❌ No IMG file open")
            return 0, 0

        if not name_mapping:
            return 0, 0

        entries = main_window.current_img.entries
        renamed_count = 0
        failed_count = 0

        # Start operation with progress
        start_operation(main_window, f"Renaming {len(name_mapping)} entries", cancellable=True)

        for i, (old_name, new_name) in enumerate(name_mapping.items()):
            # Check for cancellation
            if hasattr(main_window, 'is_operation_cancelled') and main_window.is_operation_cancelled():
                if hasattr(main_window, 'log_message'):
                    main_window.log_message("⚠️ Rename cancelled by user")
                break

            # Update progress
            progress = int((i / len(name_mapping)) * 100)
            update_progress(main_window, progress, f"Renaming {old_name}...")

            # Find entry with old name
            entry_to_rename = None
            for entry in entries:
                if entry.name == old_name:
                    entry_to_rename = entry
                    break

            if not entry_to_rename:
                failed_count += 1
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"⚠️ Entry not found: {old_name}")
                continue

            # Validate new name
            if not validate_entry_name(main_window, new_name, entry_to_rename, quiet=True):
                failed_count += 1
                continue

            # Perform rename
            success = False
            
            if hasattr(main_window, 'rename_entry_safe'):
                success = main_window.rename_entry_safe(main_window.current_img, entry_to_rename, new_name)
            elif hasattr(entry_to_rename, 'name'):
                entry_to_rename.name = new_name
                success = True

            if success:
                renamed_count += 1
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"✏️ Renamed: {old_name} → {new_name}")
            else:
                failed_count += 1
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"❌ Failed to rename: {old_name}")

        # Complete operation
        complete_operation(main_window, True, f"Rename complete: {renamed_count} renamed, {failed_count} failed")

        # Refresh table if any renames succeeded
        if renamed_count > 0:
            _refresh_img_table(main_window)

        return renamed_count, failed_count

    except Exception as e:
        complete_operation(main_window, False, f"Rename failed: {str(e)}")
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Multiple rename error: {str(e)}")
        return 0, len(name_mapping) if name_mapping else 0

def batch_rename_with_pattern(main_window, find_pattern: str, replace_pattern: str, 
                             use_regex: bool = False, selected_only: bool = True) -> Tuple[int, int]: #vers 1
    """Batch rename entries using find/replace pattern
    
    Args:
        main_window: Main window instance
        find_pattern: Pattern to find in names
        replace_pattern: Pattern to replace with
        use_regex: Whether to use regular expressions
        selected_only: Whether to rename only selected entries
        
    Returns:
        Tuple[int, int]: (renamed_count, failed_count)
    """
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("❌ No IMG file open")
            return 0, 0

        # Get entries to rename
        if selected_only:
            entries_to_rename = _get_selected_entries(main_window)
            if not entries_to_rename:
                if hasattr(main_window, 'log_message'):
                    main_window.log_message("⚠️ No entries selected for batch rename")
                return 0, 0
        else:
            entries_to_rename = main_window.current_img.entries

        # Create name mapping
        name_mapping = {}
        
        for entry in entries_to_rename:
            old_name = entry.name
            
            if use_regex:
                try:
                    new_name = re.sub(find_pattern, replace_pattern, old_name)
                except re.error as e:
                    if hasattr(main_window, 'log_message'):
                        main_window.log_message(f"❌ Regex error: {str(e)}")
                    return 0, 0
            else:
                new_name = old_name.replace(find_pattern, replace_pattern)
            
            # Only add to mapping if name actually changed
            if new_name != old_name:
                name_mapping[old_name] = new_name

        if not name_mapping:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("⚠️ No entries match the find pattern")
            return 0, 0

        # Perform batch rename
        return rename_multiple_entries(main_window, name_mapping)

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Batch rename error: {str(e)}")
        return 0, 0

def rename_entries_function(main_window) -> bool: #vers 1
    """Main rename function with dialog selection"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first")
            return False

        # Get selected entries
        selected_entries = _get_selected_entries(main_window)
        if not selected_entries:
            QMessageBox.warning(main_window, "No Selection", "Please select entries to rename")
            return False

        # Show appropriate dialog based on selection
        if len(selected_entries) == 1:
            # Single entry rename
            return rename_selected_entry(main_window)
        else:
            # Multiple entries - show batch rename dialog
            return show_batch_rename_dialog(main_window, selected_entries)

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Rename function error: {str(e)}")
        return False

def validate_entry_name(main_window, new_name: str, entry=None, quiet: bool = False) -> bool: #vers 1
    """Validate entry name for IMG files
    
    Args:
        main_window: Main window instance
        new_name: Name to validate
        entry: Entry being renamed (for duplicate checking)
        quiet: Whether to suppress error messages
        
    Returns:
        bool: True if name is valid
    """
    try:
        # Check for empty name
        if not new_name or not new_name.strip():
            if not quiet and hasattr(main_window, 'log_message'):
                main_window.log_message("❌ Entry name cannot be empty")
            return False

        new_name = new_name.strip()

        # Check length (IMG has filename length limits)
        if len(new_name) > 23:  # Standard IMG filename limit
            if not quiet and hasattr(main_window, 'log_message'):
                main_window.log_message("❌ Entry name too long (max 23 characters)")
            return False

        # Check for invalid characters
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        for char in invalid_chars:
            if char in new_name:
                if not quiet and hasattr(main_window, 'log_message'):
                    main_window.log_message(f"❌ Entry name contains invalid character: '{char}'")
                return False

        # Check for duplicate names
        if hasattr(main_window, 'current_img') and main_window.current_img:
            for existing_entry in main_window.current_img.entries:
                if existing_entry != entry and existing_entry.name.lower() == new_name.lower():
                    if not quiet and hasattr(main_window, 'log_message'):
                        main_window.log_message(f"❌ Entry name already exists: {new_name}")
                    return False

        return True

    except Exception as e:
        if not quiet and hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Name validation error: {str(e)}")
        return False

def show_rename_dialog(main_window, current_name: str) -> Optional[str]: #vers 1
    """Show single entry rename dialog"""
    try:
        new_name, ok = QInputDialog.getText(
            main_window,
            "Rename Entry",
            f"Enter new name for '{current_name}':",
            text=current_name
        )
        
        if ok and new_name:
            return new_name.strip()
        
        return None

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Rename dialog error: {str(e)}")
        return None

def show_batch_rename_dialog(main_window, selected_entries: List) -> bool: #vers 1
    """Show batch rename dialog for multiple entries"""
    try:
        from PyQt6.QtWidgets import QCheckBox, QGroupBox, QGridLayout
        
        dialog = QDialog(main_window)
        dialog.setWindowTitle(f"Batch Rename ({len(selected_entries)} entries)")
        dialog.setMinimumWidth(500)
        
        layout = QVBoxLayout(dialog)
        
        # Find/Replace section
        find_replace_group = QGroupBox("Find and Replace")
        find_replace_layout = QGridLayout(find_replace_group)
        
        find_replace_layout.addWidget(QLabel("Find:"), 0, 0)
        find_input = QLineEdit()
        find_replace_layout.addWidget(find_input, 0, 1)
        
        find_replace_layout.addWidget(QLabel("Replace:"), 1, 0)
        replace_input = QLineEdit()
        find_replace_layout.addWidget(replace_input, 1, 1)
        
        regex_check = QCheckBox("Use Regular Expressions")
        find_replace_layout.addWidget(regex_check, 2, 0, 1, 2)
        
        layout.addWidget(find_replace_group)
        
        # Preview section
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        preview_list = QListWidget()
        preview_list.setMaximumHeight(200)
        
        # Show current names
        for entry in selected_entries:
            preview_list.addItem(f"{entry.name} → (unchanged)")
        
        preview_layout.addWidget(preview_list)
        layout.addWidget(preview_group)
        
        # Update preview function
        def update_preview():
            find_text = find_input.text()
            replace_text = replace_input.text()
            use_regex = regex_check.isChecked()
            
            preview_list.clear()
            
            for entry in selected_entries:
                old_name = entry.name
                
                if find_text:
                    if use_regex:
                        try:
                            new_name = re.sub(find_text, replace_text, old_name)
                        except re.error:
                            new_name = old_name + " (regex error)"
                    else:
                        new_name = old_name.replace(find_text, replace_text)
                else:
                    new_name = old_name
                
                if new_name != old_name:
                    preview_list.addItem(f"{old_name} → {new_name}")
                else:
                    preview_list.addItem(f"{old_name} → (unchanged)")
        
        # Connect preview updates
        find_input.textChanged.connect(update_preview)
        replace_input.textChanged.connect(update_preview)
        regex_check.toggled.connect(update_preview)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        ok_btn = QPushButton("Rename")
        ok_btn.clicked.connect(dialog.accept)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        # Show dialog
        if dialog.exec() == QDialog.DialogCode.Accepted:
            find_text = find_input.text()
            replace_text = replace_input.text()
            use_regex = regex_check.isChecked()
            
            if find_text:
                renamed, failed = batch_rename_with_pattern(
                    main_window, find_text, replace_text, use_regex, selected_only=True
                )
                return renamed > 0
        
        return False

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Batch rename dialog error: {str(e)}")
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

def _refresh_img_table(main_window): #vers 1
    """Refresh IMG table after rename"""
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

def integrate_rename_functions(main_window) -> bool: #vers 1
    """Integrate rename functions into main window"""
    try:
        # Add rename methods
        main_window.rename_selected_entry = lambda new_name=None: rename_selected_entry(main_window, new_name)
        main_window.rename_multiple_entries = lambda name_mapping: rename_multiple_entries(main_window, name_mapping)
        main_window.batch_rename_with_pattern = lambda find_pattern, replace_pattern, use_regex=False, selected_only=True: batch_rename_with_pattern(main_window, find_pattern, replace_pattern, use_regex, selected_only)
        main_window.rename_entries_function = lambda: rename_entries_function(main_window)
        main_window.validate_entry_name = lambda new_name, entry=None, quiet=False: validate_entry_name(main_window, new_name, entry, quiet)
        main_window.show_rename_dialog = lambda current_name: show_rename_dialog(main_window, current_name)
        main_window.show_batch_rename_dialog = lambda selected_entries: show_batch_rename_dialog(main_window, selected_entries)

        # Aliases for backward compatibility
        main_window.rename_selected = main_window.rename_entries_function
        main_window.rename_entry = main_window.rename_selected_entry

        if hasattr(main_window, 'log_message'):
            main_window.log_message("✅ Rename functions integrated")
            main_window.log_message("   • Single entry rename")
            main_window.log_message("   • Batch rename with patterns")
            main_window.log_message("   • Regular expression support")
            main_window.log_message("   • Name validation")
            main_window.log_message("   • Interactive dialogs")

        return True

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Rename integration failed: {str(e)}")
        return False

# Export functions
__all__ = [
    'rename_selected_entry',
    'rename_multiple_entries',
    'batch_rename_with_pattern',
    'rename_entries_function',
    'validate_entry_name',
    'show_rename_dialog',
    'show_batch_rename_dialog',
    'integrate_rename_functions'
]
