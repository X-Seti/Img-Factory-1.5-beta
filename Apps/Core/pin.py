#this belongs in Core/pin.py - Version: 1
# X-Seti - September11 2025 - IMG Factory 1.5 - Pin Entry Operations

"""
Pin Entry Operations - Handles pinning/unpinning entries for quick access
Core operations for managing pinned entries and priority ordering
"""

import os
from typing import Optional, List, Dict, Any, Set
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem, QCheckBox, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QFont

##Methods list -
# pin_selected_entries
# unpin_selected_entries
# show_pinned_entries_dialog
# toggle_entry_pin_status
# get_pinned_entries
# clear_all_pins
# validate_pin_operation
# _update_table_pin_display
# _save_pin_state
# _load_pin_state

class PinnedEntriesDialog(QDialog): #vers 1
    """Dialog for managing pinned entries"""
    
    def __init__(self, parent=None, img_file=None, pinned_entries=None):
        super().__init__(parent)
        self.img_file = img_file
        self.pinned_entries = pinned_entries or set()
        self.setup_ui()
        self.populate_lists()
        
    def setup_ui(self):
        self.setWindowTitle("Manage Pinned Entries")
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # Info header
        if self.img_file:
            total_entries = len(getattr(self.img_file, 'entries', []))
            pinned_count = len(self.pinned_entries)
            info_label = QLabel(f"Total entries: {total_entries} | Pinned: {pinned_count}")
            layout.addWidget(info_label)
        
        # Lists layout
        lists_layout = QHBoxLayout()
        
        # Pinned entries list
        pinned_layout = QVBoxLayout()
        pinned_layout.addWidget(QLabel("📌 Pinned Entries:"))
        
        self.pinned_list = QListWidget()
        self.pinned_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        pinned_layout.addWidget(self.pinned_list)
        
        # Pinned list buttons
        pinned_buttons = QHBoxLayout()
        self.unpin_btn = QPushButton("Unpin Selected")
        self.unpin_btn.clicked.connect(self.unpin_selected)
        pinned_buttons.addWidget(self.unpin_btn)
        
        self.clear_all_btn = QPushButton("Clear All")
        self.clear_all_btn.clicked.connect(self.clear_all_pins)
        pinned_buttons.addWidget(self.clear_all_btn)
        
        pinned_layout.addLayout(pinned_buttons)
        lists_layout.addLayout(pinned_layout)
        
        # Available entries list
        available_layout = QVBoxLayout()
        available_layout.addWidget(QLabel("📋 Available Entries:"))
        
        self.available_list = QListWidget()
        self.available_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        available_layout.addWidget(self.available_list)
        
        # Available list buttons
        available_buttons = QHBoxLayout()
        self.pin_btn = QPushButton("Pin Selected")
        self.pin_btn.clicked.connect(self.pin_selected)
        available_buttons.addWidget(self.pin_btn)
        
        self.pin_all_btn = QPushButton("Pin All Visible")
        self.pin_all_btn.clicked.connect(self.pin_all_visible)
        available_buttons.addWidget(self.pin_all_btn)
        
        available_layout.addLayout(available_buttons)
        lists_layout.addLayout(available_layout)
        
        layout.addLayout(lists_layout)
        
        # Options
        options_layout = QVBoxLayout()
        options_layout.addWidget(QLabel("Pin Options:"))
        
        self.show_pinned_first_check = QCheckBox("Show pinned entries at top of table")
        self.show_pinned_first_check.setChecked(True)
        options_layout.addWidget(self.show_pinned_first_check)
        
        self.highlight_pinned_check = QCheckBox("Highlight pinned entries in table")
        self.highlight_pinned_check.setChecked(True)
        options_layout.addWidget(self.highlight_pinned_check)
        
        layout.addLayout(options_layout)
        
        # Dialog buttons
        button_layout = QHBoxLayout()
        
        self.apply_btn = QPushButton("Apply Changes")
        self.apply_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.apply_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def populate_lists(self):
        """Populate the pinned and available lists"""
        self.pinned_list.clear()
        self.available_list.clear()
        
        if not self.img_file or not hasattr(self.img_file, 'entries'):
            return
        
        # Add pinned entries
        for entry in self.img_file.entries:
            entry_name = getattr(entry, 'name', '')
            if entry_name in self.pinned_entries:
                item = QListWidgetItem(f"📌 {entry_name}")
                item.setData(Qt.ItemDataRole.UserRole, entry_name)
                self.pinned_list.addItem(item)
        
        # Add available (non-pinned) entries
        for entry in self.img_file.entries:
            entry_name = getattr(entry, 'name', '')
            if entry_name not in self.pinned_entries:
                item = QListWidgetItem(entry_name)
                item.setData(Qt.ItemDataRole.UserRole, entry_name)
                self.available_list.addItem(item)
    
    def pin_selected(self):
        """Pin selected available entries"""
        selected_items = self.available_list.selectedItems()
        for item in selected_items:
            entry_name = item.data(Qt.ItemDataRole.UserRole)
            self.pinned_entries.add(entry_name)
        
        self.populate_lists()
    
    def unpin_selected(self):
        """Unpin selected pinned entries"""
        selected_items = self.pinned_list.selectedItems()
        for item in selected_items:
            entry_name = item.data(Qt.ItemDataRole.UserRole)
            self.pinned_entries.discard(entry_name)
        
        self.populate_lists()
    
    def pin_all_visible(self):
        """Pin all visible available entries"""
        for i in range(self.available_list.count()):
            item = self.available_list.item(i)
            entry_name = item.data(Qt.ItemDataRole.UserRole)
            self.pinned_entries.add(entry_name)
        
        self.populate_lists()
    
    def clear_all_pins(self):
        """Clear all pinned entries"""
        reply = QMessageBox.question(
            self,
            "Clear All Pins",
            f"Remove all {len(self.pinned_entries)} pinned entries?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.pinned_entries.clear()
            self.populate_lists()
    
    def get_pinned_entries(self):
        """Get the current set of pinned entries"""
        return self.pinned_entries
    
    def get_pin_options(self):
        """Get the pin display options"""
        return {
            'show_pinned_first': self.show_pinned_first_check.isChecked(),
            'highlight_pinned': self.highlight_pinned_check.isChecked()
        }


def pin_selected_entries(main_window) -> bool: #vers 1
    """Pin currently selected entries"""
    try:
        if not validate_pin_operation(main_window):
            return False

        # Get current IMG file
        current_tab = main_window.tab_widget.currentWidget()
        if not current_tab or not hasattr(current_tab, 'img_file'):
            main_window.log_message("❌ No active IMG file")
            return False

        img_file = current_tab.img_file
        
        # Get selected entries from table
        selected_entries = _get_selected_entry_names(main_window)
        if not selected_entries:
            main_window.log_message("❌ No entries selected for pinning")
            return False

        # Get or create pinned entries set for this IMG
        if not hasattr(img_file, '_pinned_entries'):
            img_file._pinned_entries = set()

        # Add selected entries to pinned set
        initial_count = len(img_file._pinned_entries)
        img_file._pinned_entries.update(selected_entries)
        new_pins = len(img_file._pinned_entries) - initial_count

        if new_pins > 0:
            main_window.log_message(f"📌 Pinned {new_pins} entries")
            
            # Update table display
            _update_table_pin_display(main_window, img_file)
            
            # Save pin state
            _save_pin_state(main_window, img_file)
            
            return True
        else:
            main_window.log_message("ℹ️ Selected entries are already pinned")
            return True

    except Exception as e:
        main_window.log_message(f"❌ Pin operation failed: {str(e)}")
        return False


def unpin_selected_entries(main_window) -> bool: #vers 1
    """Unpin currently selected entries"""
    try:
        if not validate_pin_operation(main_window):
            return False

        # Get current IMG file
        current_tab = main_window.tab_widget.currentWidget()
        if not current_tab or not hasattr(current_tab, 'img_file'):
            main_window.log_message("❌ No active IMG file")
            return False

        img_file = current_tab.img_file
        
        # Get selected entries from table
        selected_entries = _get_selected_entry_names(main_window)
        if not selected_entries:
            main_window.log_message("❌ No entries selected for unpinning")
            return False

        # Get pinned entries set
        if not hasattr(img_file, '_pinned_entries'):
            img_file._pinned_entries = set()

        # Remove selected entries from pinned set
        initial_count = len(img_file._pinned_entries)
        img_file._pinned_entries.difference_update(selected_entries)
        removed_pins = initial_count - len(img_file._pinned_entries)

        if removed_pins > 0:
            main_window.log_message(f"📌 Unpinned {removed_pins} entries")
            
            # Update table display
            _update_table_pin_display(main_window, img_file)
            
            # Save pin state
            _save_pin_state(main_window, img_file)
            
            return True
        else:
            main_window.log_message("ℹ️ Selected entries were not pinned")
            return True

    except Exception as e:
        main_window.log_message(f"❌ Unpin operation failed: {str(e)}")
        return False


def show_pinned_entries_dialog(main_window) -> bool: #vers 1
    """Show dialog to manage pinned entries"""
    try:
        if not validate_pin_operation(main_window):
            return False

        # Get current IMG file
        current_tab = main_window.tab_widget.currentWidget()
        if not current_tab or not hasattr(current_tab, 'img_file'):
            main_window.log_message("❌ No active IMG file")
            return False

        img_file = current_tab.img_file
        
        # Get or create pinned entries set
        if not hasattr(img_file, '_pinned_entries'):
            img_file._pinned_entries = set()

        # Show dialog
        dialog = PinnedEntriesDialog(main_window, img_file, img_file._pinned_entries.copy())
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Apply changes
            img_file._pinned_entries = dialog.get_pinned_entries()
            pin_options = dialog.get_pin_options()
            
            # Store pin options
            if not hasattr(img_file, '_pin_options'):
                img_file._pin_options = {}
            img_file._pin_options.update(pin_options)
            
            # Update table display
            _update_table_pin_display(main_window, img_file)
            
            # Save pin state
            _save_pin_state(main_window, img_file)
            
            pinned_count = len(img_file._pinned_entries)
            main_window.log_message(f"📌 Pin configuration updated: {pinned_count} entries pinned")
            return True
        else:
            return False

    except Exception as e:
        main_window.log_message(f"❌ Pinned entries dialog failed: {str(e)}")
        return False


def toggle_entry_pin_status(main_window, entry_name: str) -> bool: #vers 1
    """Toggle pin status of a specific entry"""
    try:
        # Get current IMG file
        current_tab = main_window.tab_widget.currentWidget()
        if not current_tab or not hasattr(current_tab, 'img_file'):
            return False

        img_file = current_tab.img_file
        
        # Get or create pinned entries set
        if not hasattr(img_file, '_pinned_entries'):
            img_file._pinned_entries = set()

        # Toggle pin status
        if entry_name in img_file._pinned_entries:
            img_file._pinned_entries.remove(entry_name)
            main_window.log_message(f"📌 Unpinned: {entry_name}")
        else:
            img_file._pinned_entries.add(entry_name)
            main_window.log_message(f"📌 Pinned: {entry_name}")

        # Update table display
        _update_table_pin_display(main_window, img_file)
        
        # Save pin state
        _save_pin_state(main_window, img_file)
        
        return True

    except Exception as e:
        main_window.log_message(f"❌ Toggle pin failed: {str(e)}")
        return False


def get_pinned_entries(main_window) -> Set[str]: #vers 1
    """Get set of pinned entry names for current IMG"""
    try:
        # Get current IMG file
        current_tab = main_window.tab_widget.currentWidget()
        if not current_tab or not hasattr(current_tab, 'img_file'):
            return set()

        img_file = current_tab.img_file
        
        # Get pinned entries set
        if hasattr(img_file, '_pinned_entries'):
            return img_file._pinned_entries.copy()
        else:
            return set()

    except Exception as e:
        main_window.log_message(f"❌ Failed to get pinned entries: {str(e)}")
        return set()


def clear_all_pins(main_window) -> bool: #vers 1
    """Clear all pinned entries for current IMG"""
    try:
        if not validate_pin_operation(main_window):
            return False

        # Get current IMG file
        current_tab = main_window.tab_widget.currentWidget()
        if not current_tab or not hasattr(current_tab, 'img_file'):
            main_window.log_message("❌ No active IMG file")
            return False

        img_file = current_tab.img_file
        
        # Get pinned entries count
        pinned_count = 0
        if hasattr(img_file, '_pinned_entries'):
            pinned_count = len(img_file._pinned_entries)

        if pinned_count == 0:
            main_window.log_message("ℹ️ No entries are currently pinned")
            return True

        # Confirm clear operation
        reply = QMessageBox.question(
            main_window,
            "Clear All Pins",
            f"Remove all {pinned_count} pinned entries?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Clear pinned entries
            img_file._pinned_entries = set()
            
            # Update table display
            _update_table_pin_display(main_window, img_file)
            
            # Save pin state
            _save_pin_state(main_window, img_file)
            
            main_window.log_message(f"📌 Cleared all {pinned_count} pinned entries")
            return True
        else:
            return False

    except Exception as e:
        main_window.log_message(f"❌ Clear pins operation failed: {str(e)}")
        return False


def _get_selected_entry_names(main_window) -> List[str]: #vers 1
    """Get names of currently selected entries"""
    try:
        selected_entries = []
        
        if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'table'):
            table = main_window.gui_layout.table
            selected_rows = set()
            
            for item in table.selectedItems():
                selected_rows.add(item.row())
            
            # Get entry names from selected rows
            for row in selected_rows:
                if row < table.rowCount():
                    name_item = table.item(row, 0)  # Assuming name is in first column
                    if name_item:
                        selected_entries.append(name_item.text())

        return selected_entries

    except Exception as e:
        main_window.log_message(f"⚠️ Failed to get selected entries: {str(e)}")
        return []


def _update_table_pin_display(main_window, img_file) -> bool: #vers 1
    """Update table display to show pinned entries"""
    try:
        if not hasattr(main_window, 'gui_layout') or not hasattr(main_window.gui_layout, 'table'):
            return False

        table = main_window.gui_layout.table
        pinned_entries = getattr(img_file, '_pinned_entries', set())
        pin_options = getattr(img_file, '_pin_options', {})
        
        show_pinned_first = pin_options.get('show_pinned_first', True)
        highlight_pinned = pin_options.get('highlight_pinned', True)

        # If show pinned first is enabled, reorganize entries
        if show_pinned_first and hasattr(img_file, 'entries'):
            # Separate pinned and unpinned entries
            pinned_list = []
            unpinned_list = []
            
            for entry in img_file.entries:
                entry_name = getattr(entry, 'name', '')
                if entry_name in pinned_entries:
                    pinned_list.append(entry)
                else:
                    unpinned_list.append(entry)
            
            # Reorder: pinned entries first, then unpinned
            img_file.entries = pinned_list + unpinned_list

        # Update table display using existing population system
        if hasattr(main_window, 'populate_img_table'):
            main_window.populate_img_table(img_file)
        elif hasattr(main_window, 'refresh_table_display'):
            main_window.refresh_table_display()

        # Apply highlighting if enabled
        if highlight_pinned:
            _apply_pin_highlighting(main_window, table, pinned_entries)

        return True

    except Exception as e:
        main_window.log_message(f"❌ Failed to update pin display: {str(e)}")
        return False


def _apply_pin_highlighting(main_window, table, pinned_entries: Set[str]) -> bool: #vers 1
    """Apply visual highlighting to pinned entries in table"""
    try:
        from PyQt6.QtGui import QBrush, QColor
        from PyQt6.QtCore import Qt

        # Define pin highlight color
        pin_color = QColor(255, 255, 200)  # Light yellow
        pin_brush = QBrush(pin_color)
        
        # Highlight pinned entries
        for row in range(table.rowCount()):
            name_item = table.item(row, 0)
            if name_item:
                entry_name = name_item.text()
                
                if entry_name in pinned_entries:
                    # Highlight this row
                    for col in range(table.columnCount()):
                        item = table.item(row, col)
                        if item:
                            item.setBackground(pin_brush)
                            # Add pin icon to name
                            if col == 0 and not entry_name.startswith("📌"):
                                item.setText(f"📌 {entry_name}")
                else:
                    # Remove highlighting
                    for col in range(table.columnCount()):
                        item = table.item(row, col)
                        if item:
                            item.setBackground(QBrush())
                            # Remove pin icon from name
                            if col == 0 and entry_name.startswith("📌"):
                                clean_name = entry_name.replace("📌 ", "")
                                item.setText(clean_name)

        return True

    except Exception as e:
        main_window.log_message(f"⚠️ Failed to apply pin highlighting: {str(e)}")
        return False


def _save_pin_state(main_window, img_file) -> bool: #vers 1
    """Save pin state to file or memory"""
    try:
        # Simple implementation: store pin state as IMG file attribute
        # In a full implementation, this could save to a separate config file
        
        if hasattr(img_file, '_pinned_entries'):
            # Create a simple serializable representation
            pin_data = {
                'pinned_entries': list(img_file._pinned_entries),
                'pin_options': getattr(img_file, '_pin_options', {})
            }
            
            # Store in IMG file object
            img_file._pin_state = pin_data
            
            return True

    except Exception as e:
        main_window.log_message(f"⚠️ Failed to save pin state: {str(e)}")
        return False


def _load_pin_state(main_window, img_file) -> bool: #vers 1
    """Load pin state from file or memory"""
    try:
        # Load pin state from IMG file object
        if hasattr(img_file, '_pin_state'):
            pin_data = img_file._pin_state
            
            # Restore pinned entries
            if 'pinned_entries' in pin_data:
                img_file._pinned_entries = set(pin_data['pinned_entries'])
            
            # Restore pin options
            if 'pin_options' in pin_data:
                img_file._pin_options = pin_data['pin_options']
            
            return True
        else:
            # Initialize empty pin state
            img_file._pinned_entries = set()
            img_file._pin_options = {
                'show_pinned_first': True,
                'highlight_pinned': True
            }
            return True

    except Exception as e:
        main_window.log_message(f"⚠️ Failed to load pin state: {str(e)}")
        return False


def get_pin_statistics(main_window) -> Dict[str, Any]: #vers 1
    """Get statistics about pinned entries"""
    try:
        # Get current IMG file
        current_tab = main_window.tab_widget.currentWidget()
        if not current_tab or not hasattr(current_tab, 'img_file'):
            return {'total_entries': 0, 'pinned_entries': 0}

        img_file = current_tab.img_file
        total_entries = len(getattr(img_file, 'entries', []))
        pinned_entries = len(getattr(img_file, '_pinned_entries', set()))
        
        stats = {
            'total_entries': total_entries,
            'pinned_entries': pinned_entries,
            'pin_percentage': (pinned_entries / total_entries * 100) if total_entries > 0 else 0,
            'pin_options': getattr(img_file, '_pin_options', {})
        }

        return stats

    except Exception as e:
        main_window.log_message(f"❌ Failed to get pin statistics: {str(e)}")
        return {'total_entries': 0, 'pinned_entries': 0}


def validate_pin_operation(main_window) -> bool: #vers 1
    """Validate if pin operation can proceed"""
    try:
        if not hasattr(main_window, 'tab_widget') or main_window.tab_widget.count() == 0:
            main_window.log_message("❌ No IMG file loaded")
            return False

        return True

    except Exception as e:
        main_window.log_message(f"❌ Pin validation failed: {str(e)}")
        return False


def is_entry_pinned(main_window, entry_name: str) -> bool: #vers 1
    """Check if a specific entry is pinned"""
    try:
        # Get current IMG file
        current_tab = main_window.tab_widget.currentWidget()
        if not current_tab or not hasattr(current_tab, 'img_file'):
            return False

        img_file = current_tab.img_file
        pinned_entries = getattr(img_file, '_pinned_entries', set())
        
        return entry_name in pinned_entries

    except Exception as e:
        return False


def setup_pin_system_for_img(main_window, img_file) -> bool: #vers 1
    """Initialize pin system for an IMG file"""
    try:
        # Load existing pin state or create new
        _load_pin_state(main_window, img_file)
        
        # Update display if this is the current IMG
        current_tab = main_window.tab_widget.currentWidget()
        if current_tab and hasattr(current_tab, 'img_file') and current_tab.img_file == img_file:
            _update_table_pin_display(main_window, img_file)

        return True

    except Exception as e:
        main_window.log_message(f"⚠️ Failed to setup pin system: {str(e)}")
        return False


def cleanup_pin_system_for_img(main_window, img_file) -> bool: #vers 1
    """Cleanup pin system for an IMG file"""
    try:
        # Save current pin state before cleanup
        _save_pin_state(main_window, img_file)
        
        return True

    except Exception as e:
        main_window.log_message(f"⚠️ Failed to cleanup pin system: {str(e)}")
        return False


def integrate_pin_functions(main_window) -> bool: #vers 1
    """Integrate pin functions into main window"""
    try:
        # Add pin functions to main window
        main_window.pin_selected_entries = lambda: pin_selected_entries(main_window)
        main_window.unpin_selected_entries = lambda: unpin_selected_entries(main_window)
        main_window.show_pinned_entries_dialog = lambda: show_pinned_entries_dialog(main_window)
        main_window.toggle_entry_pin_status = lambda entry_name: toggle_entry_pin_status(main_window, entry_name)
        main_window.get_pinned_entries = lambda: get_pinned_entries(main_window)
        main_window.clear_all_pins = lambda: clear_all_pins(main_window)
        main_window.is_entry_pinned = lambda entry_name: is_entry_pinned(main_window, entry_name)
        main_window.get_pin_statistics = lambda: get_pin_statistics(main_window)
        main_window.setup_pin_system_for_img = lambda img_file: setup_pin_system_for_img(main_window, img_file)
        main_window.cleanup_pin_system_for_img = lambda img_file: cleanup_pin_system_for_img(main_window, img_file)
        
        main_window.log_message("✅ Pin functions integrated")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Failed to integrate pin functions: {str(e)}")
        return False