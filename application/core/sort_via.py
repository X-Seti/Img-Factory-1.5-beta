#this belongs in Core/sort_entries.py - Version: 1
# X-Seti - September11 2025 - IMG Factory 1.5 - Sort Table Entries

"""
Sort Table Entries - Handles sorting IMG table entries by various criteria
Core operations for organizing table display and entry ordering
"""

import os
from typing import Optional, List, Dict, Any, Callable
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QCheckBox, QMessageBox
from PyQt6.QtCore import Qt

##Methods list -
# sort_entries
# show_sort_dialog
# sort_by_name
# sort_by_size
# sort_by_type
# sort_by_offset
# validate_sort_operation
# _apply_sort_to_table
# _get_sort_key_function
# _preserve_selection_during_sort

class SortEntriesDialog(QDialog): #vers 1
    """Dialog for configuring entry sorting options"""
    
    def __init__(self, parent=None, img_file=None):
        super().__init__(parent)
        self.img_file = img_file
        self.sort_config = None
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Sort Table Entries")
        self.setModal(True)
        self.resize(350, 200)
        
        layout = QVBoxLayout(self)
        
        # File info
        if self.img_file:
            entry_count = len(getattr(self.img_file, 'entries', []))
            info_label = QLabel(f"Entries to sort: {entry_count}")
            layout.addWidget(info_label)
        
        # Sort criteria selection
        criteria_layout = QHBoxLayout()
        criteria_layout.addWidget(QLabel("Sort by:"))
        
        self.criteria_combo = QComboBox()
        self.criteria_combo.addItems([
            "Name (A-Z)",
            "Name (Z-A)",
            "File Size (Smallest first)",
            "File Size (Largest first)",
            "File Type (Extension)",
            "Offset (File position)",
            "Custom Order"
        ])
        criteria_layout.addWidget(self.criteria_combo)
        layout.addLayout(criteria_layout)
        
        # Sort options
        options_layout = QVBoxLayout()
        options_layout.addWidget(QLabel("Sort Options:"))
        
        self.case_sensitive_check = QCheckBox("Case sensitive name sorting")
        self.case_sensitive_check.setChecked(False)
        options_layout.addWidget(self.case_sensitive_check)
        
        self.natural_sort_check = QCheckBox("Natural number sorting (file1, file2, file10)")
        self.natural_sort_check.setChecked(True)
        options_layout.addWidget(self.natural_sort_check)
        
        self.preserve_selection_check = QCheckBox("Preserve current selection")
        self.preserve_selection_check.setChecked(True)
        options_layout.addWidget(self.preserve_selection_check)
        
        layout.addLayout(options_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.sort_btn = QPushButton("Sort Entries")
        self.sort_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.sort_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def get_sort_config(self):
        """Get the sort configuration from dialog"""
        criteria = self.criteria_combo.currentText()
        
        return {
            'criteria': criteria,
            'case_sensitive': self.case_sensitive_check.isChecked(),
            'natural_sort': self.natural_sort_check.isChecked(),
            'preserve_selection': self.preserve_selection_check.isChecked()
        }


def sort_entries(main_window) -> bool: #vers 1
    """Main function to sort table entries"""
    try:
        if not validate_sort_operation(main_window):
            return False

        # Get current IMG file
        current_tab = main_window.tab_widget.currentWidget()
        if not current_tab or not hasattr(current_tab, 'img_file'):
            main_window.log_message("❌ No active IMG file to sort")
            return False

        img_file = current_tab.img_file
        
        if not hasattr(img_file, 'entries') or not img_file.entries:
            main_window.log_message("❌ No entries to sort")
            return False

        # Show sort configuration dialog
        sort_config = show_sort_dialog(main_window, img_file)
        if not sort_config:
            main_window.log_message("❌ Sort operation cancelled")
            return False

        criteria = sort_config['criteria']
        main_window.log_message(f"📊 Sorting {len(img_file.entries)} entries by: {criteria}")

        # Preserve selection if requested
        selected_entries = []
        if sort_config.get('preserve_selection', True):
            selected_entries = _get_currently_selected_entries(main_window)

        # Perform sort based on criteria
        success = False
        if "Name" in criteria:
            reverse_order = "Z-A" in criteria
            success = sort_by_name(main_window, img_file, reverse_order, sort_config)
        elif "File Size" in criteria:
            reverse_order = "Largest first" in criteria
            success = sort_by_size(main_window, img_file, reverse_order, sort_config)
        elif "File Type" in criteria:
            success = sort_by_type(main_window, img_file, sort_config)
        elif "Offset" in criteria:
            success = sort_by_offset(main_window, img_file, sort_config)
        elif "Custom Order" in criteria:
            success = _show_custom_sort_dialog(main_window, img_file)

        if success:
            # Apply sort to table display
            _apply_sort_to_table(main_window, img_file)
            
            # Restore selection if requested
            if sort_config.get('preserve_selection', True) and selected_entries:
                _restore_selection_after_sort(main_window, selected_entries)
            
            # Mark IMG as modified (entry order changed)
            if hasattr(img_file, 'modified'):
                img_file.modified = True
            
            main_window.log_message(f"✅ Entries sorted successfully by {criteria}")
            return True
        else:
            main_window.log_message("❌ Entry sorting failed")
            return False

    except Exception as e:
        main_window.log_message(f"❌ Sort operation failed: {str(e)}")
        return False


def show_sort_dialog(main_window, img_file) -> Optional[Dict[str, Any]]: #vers 1
    """Show sort configuration dialog"""
    try:
        dialog = SortEntriesDialog(main_window, img_file)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.get_sort_config()
        else:
            return None

    except Exception as e:
        main_window.log_message(f"❌ Sort dialog failed: {str(e)}")
        return None


def sort_by_name(main_window, img_file, reverse_order: bool = False, config: Dict[str, Any] = None) -> bool: #vers 1
    """Sort entries alphabetically by name"""
    try:
        if not hasattr(img_file, 'entries'):
            return False

        case_sensitive = config.get('case_sensitive', False) if config else False
        natural_sort = config.get('natural_sort', True) if config else True

        if natural_sort:
            # Natural sorting (handles numbers properly)
            sort_key = _get_natural_sort_key(case_sensitive)
        else:
            # Simple alphabetical sorting
            if case_sensitive:
                sort_key = lambda entry: getattr(entry, 'name', '')
            else:
                sort_key = lambda entry: getattr(entry, 'name', '').lower()

        img_file.entries.sort(key=sort_key, reverse=reverse_order)
        
        order_text = "descending" if reverse_order else "ascending"
        main_window.log_message(f"📝 Sorted by name ({order_text})")
        return True

    except Exception as e:
        main_window.log_message(f"❌ Name sorting failed: {str(e)}")
        return False


def sort_by_size(main_window, img_file, reverse_order: bool = False, config: Dict[str, Any] = None) -> bool: #vers 1
    """Sort entries by file size"""
    try:
        if not hasattr(img_file, 'entries'):
            return False

        img_file.entries.sort(
            key=lambda entry: getattr(entry, 'size', 0),
            reverse=reverse_order
        )
        
        order_text = "largest first" if reverse_order else "smallest first"
        main_window.log_message(f"📏 Sorted by size ({order_text})")
        return True

    except Exception as e:
        main_window.log_message(f"❌ Size sorting failed: {str(e)}")
        return False


def sort_by_type(main_window, img_file, config: Dict[str, Any] = None) -> bool: #vers 1
    """Sort entries by file type (extension)"""
    try:
        if not hasattr(img_file, 'entries'):
            return False

        case_sensitive = config.get('case_sensitive', False) if config else False

        def type_sort_key(entry):
            name = getattr(entry, 'name', '')
            ext = os.path.splitext(name)[1]
            if not case_sensitive:
                ext = ext.lower()
            # Sort by extension first, then by name
            return (ext, name.lower() if not case_sensitive else name)

        img_file.entries.sort(key=type_sort_key)
        
        main_window.log_message("🏷️ Sorted by file type")
        return True

    except Exception as e:
        main_window.log_message(f"❌ Type sorting failed: {str(e)}")
        return False


def sort_by_offset(main_window, img_file, config: Dict[str, Any] = None) -> bool: #vers 1
    """Sort entries by file offset (original order)"""
    try:
        if not hasattr(img_file, 'entries'):
            return False

        img_file.entries.sort(key=lambda entry: getattr(entry, 'offset', 0))
        
        main_window.log_message("📍 Sorted by file offset (original order)")
        return True

    except Exception as e:
        main_window.log_message(f"❌ Offset sorting failed: {str(e)}")
        return False


def _get_natural_sort_key(case_sensitive: bool = False) -> Callable: #vers 1
    """Get natural sorting key function"""
    import re
    
    def natural_key(entry):
        name = getattr(entry, 'name', '')
        if not case_sensitive:
            name = name.