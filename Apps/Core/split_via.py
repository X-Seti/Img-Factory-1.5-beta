#this belongs in Core/split_via.py - Version: 1
# X-Seti - September11 2025 - IMG Factory 1.5 - Split IMG Operations

"""
Split IMG Operations - Handles splitting IMG files into smaller archives
Core operations for splitting IMG files by size, count, or file type
"""

import os
import math
from typing import Optional, List, Dict, Any
from pathlib import Path
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QComboBox, QSpinBox, QCheckBox, QFileDialog, QMessageBox
from PyQt6.QtCore import Qt

##Methods list -
# split_img
# show_split_dialog
# split_by_file_count
# split_by_file_size
# split_by_file_type
# validate_split_operation
# _create_split_img
# _distribute_entries
# _get_split_output_paths

class SplitIMGDialog(QDialog): #vers 1
    """Dialog for configuring IMG split options"""
    
    def __init__(self, parent=None, img_file=None):
        super().__init__(parent)
        self.img_file = img_file
        self.split_config = None
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Split IMG File")
        self.setModal(True)
        self.resize(400, 300)
        
        layout = QVBoxLayout(self)
        
        # File info
        if self.img_file:
            file_name = getattr(self.img_file, 'file_path', 'Unknown')
            entry_count = len(getattr(self.img_file, 'entries', []))
            
            info_label = QLabel(f"File: {os.path.basename(file_name)}\nEntries: {entry_count}")
            layout.addWidget(info_label)
        
        # Split method selection
        method_layout = QHBoxLayout()
        method_layout.addWidget(QLabel("Split Method:"))
        
        self.method_combo = QComboBox()
        self.method_combo.addItems([
            "By Number of Parts",
            "By Entries per Part", 
            "By File Size",
            "By File Type"
        ])
        self.method_combo.currentTextChanged.connect(self.on_method_changed)
        method_layout.addWidget(self.method_combo)
        layout.addLayout(method_layout)
        
        # Configuration area
        self.config_widget = QVBoxLayout()
        layout.addLayout(self.config_widget)
        
        # Output directory
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output Directory:"))
        
        self.output_edit = QLineEdit()
        self.output_edit.setText(os.path.expanduser("~/Desktop"))
        output_layout.addWidget(self.output_edit)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_output_dir)
        output_layout.addWidget(browse_btn)
        layout.addLayout(output_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.split_btn = QPushButton("Split IMG")
        self.split_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.split_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        # Initialize with first method
        self.on_method_changed()
    
    def on_method_changed(self):
        # Clear previous config widgets
        self.clear_config_layout()
        
        method = self.method_combo.currentText()
        
        if method == "By Number of Parts":
            self.setup_parts_config()
        elif method == "By Entries per Part":
            self.setup_entries_config()
        elif method == "By File Size":
            self.setup_size_config()
        elif method == "By File Type":
            self.setup_type_config()
    
    def clear_config_layout(self):
        while self.config_widget.count():
            child = self.config_widget.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def setup_parts_config(self):
        layout = QHBoxLayout()
        layout.addWidget(QLabel("Number of Parts:"))
        
        self.parts_spin = QSpinBox()
        self.parts_spin.setRange(2, 100)
        self.parts_spin.setValue(2)
        layout.addWidget(self.parts_spin)
        
        self.config_widget.addLayout(layout)
    
    def setup_entries_config(self):
        layout = QHBoxLayout()
        layout.addWidget(QLabel("Entries per Part:"))
        
        self.entries_spin = QSpinBox()
        self.entries_spin.setRange(1, 10000)
        self.entries_spin.setValue(100)
        layout.addWidget(self.entries_spin)
        
        self.config_widget.addLayout(layout)
    
    def setup_size_config(self):
        layout = QHBoxLayout()
        layout.addWidget(QLabel("Max Size per Part:"))
        
        self.size_spin = QSpinBox()
        self.size_spin.setRange(1, 2048)
        self.size_spin.setValue(100)
        self.size_spin.setSuffix(" MB")
        layout.addWidget(self.size_spin)
        
        self.config_widget.addLayout(layout)
    
    def setup_type_config(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Split by file extensions:"))
        
        # Common GTA file types
        self.type_checks = {}
        types = [".dff", ".txd", ".col", ".ide", ".ipl", ".dat"]
        
        for file_type in types:
            check = QCheckBox(f"{file_type.upper()} files")
            check.setChecked(True)
            self.type_checks[file_type] = check
            layout.addWidget(check)
        
        self.config_widget.addLayout(layout)
    
    def browse_output_dir(self):
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Output Directory",
            self.output_edit.text()
        )
        if directory:
            self.output_edit.setText(directory)
    
    def get_split_config(self):
        """Get the split configuration from dialog"""
        method = self.method_combo.currentText()
        output_dir = self.output_edit.text()
        
        config = {
            'method': method,
            'output_dir': output_dir
        }
        
        if method == "By Number of Parts":
            config['parts'] = self.parts_spin.value()
        elif method == "By Entries per Part":
            config['entries_per_part'] = self.entries_spin.value()
        elif method == "By File Size":
            config['max_size_mb'] = self.size_spin.value()
        elif method == "By File Type":
            selected_types = []
            for file_type, check in self.type_checks.items():
                if check.isChecked():
                    selected_types.append(file_type)
            config['file_types'] = selected_types
        
        return config


def split_img(main_window) -> bool: #vers 1
    """Main function to split IMG file"""
    try:
        if not validate_split_operation(main_window):
            return False

        # Get current IMG file
        current_tab = main_window.tab_widget.currentWidget()
        if not current_tab or not hasattr(current_tab, 'img_file'):
            main_window.log_message("❌ No active IMG file to split")
            return False

        img_file = current_tab.img_file
        
        # Show split configuration dialog
        split_config = show_split_dialog(main_window, img_file)
        if not split_config:
            main_window.log_message("❌ Split operation cancelled")
            return False

        main_window.log_message(f"✂️ Starting IMG split: {split_config['method']}")

        # Perform split based on method
        method = split_config['method']
        success = False

        if method == "By Number of Parts":
            success = split_by_parts_count(main_window, img_file, split_config)
        elif method == "By Entries per Part":
            success = split_by_entries_per_part(main_window, img_file, split_config)
        elif method == "By File Size":
            success = split_by_file_size(main_window, img_file, split_config)
        elif method == "By File Type":
            success = split_by_file_type(main_window, img_file, split_config)

        if success:
            main_window.log_message("✅ IMG split completed successfully")
            return True
        else:
            main_window.log_message("❌ IMG split operation failed")
            return False

    except Exception as e:
        main_window.log_message(f"❌ Split operation failed: {str(e)}")
        return False


def show_split_dialog(main_window, img_file) -> Optional[Dict[str, Any]]: #vers 1
    """Show split configuration dialog"""
    try:
        dialog = SplitIMGDialog(main_window, img_file)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.get_split_config()
        else:
            return None

    except Exception as e:
        main_window.log_message(f"❌ Split dialog failed: {str(e)}")
        return None


def split_by_parts_count(main_window, img_file, config: Dict[str, Any]) -> bool: #vers 1
    """Split IMG into specified number of parts"""
    try:
        if not hasattr(img_file, 'entries') or not img_file.entries:
            main_window.log_message("❌ No entries to split")
            return False

        entries = img_file.entries
        parts_count = config['parts']
        entries_per_part = math.ceil(len(entries) / parts_count)

        main_window.log_message(f"📊 Splitting {len(entries)} entries into {parts_count} parts ({entries_per_part} entries each)")

        # Create entry groups
        entry_groups = []
        for i in range(0, len(entries), entries_per_part):
            group = entries[i:i + entries_per_part]
            entry_groups.append(group)

        # Create split IMG files
        success_count = 0
        for i, group in enumerate(entry_groups):
            output_path = _get_split_output_path(config, img_file, f"part{i+1}")
            
            if _create_split_img(main_window, group, output_path):
                success_count += 1
                main_window.log_message(f"✅ Created part {i+1}: {len(group)} entries")
            else:
                main_window.log_message(f"❌ Failed to create part {i+1}")

        return success_count == len(entry_groups)

    except Exception as e:
        main_window.log_message(f"❌ Parts count split failed: {str(e)}")
        return False


def split_by_entries_per_part(main_window, img_file, config: Dict[str, Any]) -> bool: #vers 1
    """Split IMG by specified entries per part"""
    try:
        if not hasattr(img_file, 'entries') or not img_file.entries:
            main_window.log_message("❌ No entries to split")
            return False

        entries = img_file.entries
        entries_per_part = config['entries_per_part']
        parts_count = math.ceil(len(entries) / entries_per_part)

        main_window.log_message(f"📊 Splitting {len(entries)} entries into {parts_count} parts ({entries_per_part} entries each)")

        # Create entry groups
        entry_groups = []
        for i in range(0, len(entries), entries_per_part):
            group = entries[i:i + entries_per_part]
            entry_groups.append(group)

        # Create split IMG files
        success_count = 0
        for i, group in enumerate(entry_groups):
            output_path = _get_split_output_path(config, img_file, f"part{i+1}")
            
            if _create_split_img(main_window, group, output_path):
                success_count += 1
                main_window.log_message(f"✅ Created part {i+1}: {len(group)} entries")
            else:
                main_window.log_message(f"❌ Failed to create part {i+1}")

        return success_count == len(entry_groups)

    except Exception as e:
        main_window.log_message(f"❌ Entries per part split failed: {str(e)}")
        return False


def split_by_file_size(main_window, img_file, config: Dict[str, Any]) -> bool: #vers 1
    """Split IMG by maximum file size"""
    try:
        if not hasattr(img_file, 'entries') or not img_file.entries:
            main_window.log_message("❌ No entries to split")
            return False

        entries = img_file.entries
        max_size_bytes = config['max_size_mb'] * 1024 * 1024  # Convert MB to bytes
        
        main_window.log_message(f"📊 Splitting by size: max {config['max_size_mb']} MB per part")

        # Group entries by size constraint
        entry_groups = []
        current_group = []
        current_size = 0
        header_overhead = 8 + (32 * len(entries))  # Estimate header size

        for entry in entries:
            entry_size = getattr(entry, 'size', 0)
            
            # Check if adding this entry would exceed size limit
            if current_size + entry_size + header_overhead > max_size_bytes and current_group:
                # Start new group
                entry_groups.append(current_group)
                current_group = [entry]
                current_size = entry_size
            else:
                # Add to current group
                current_group.append(entry)
                current_size += entry_size

        # Add final group if not empty
        if current_group:
            entry_groups.append(current_group)

        main_window.log_message(f"📊 Created {len(entry_groups)} size-based parts")

        # Create split IMG files
        success_count = 0
        for i, group in enumerate(entry_groups):
            output_path = _get_split_output_path(config, img_file, f"part{i+1}")
            
            if _create_split_img(main_window, group, output_path):
                success_count += 1
                
                # Calculate actual size
                group_size = sum(getattr(e, 'size', 0) for e in group)
                size_mb = group_size / (1024 * 1024)
                main_window.log_message(f"✅ Created part {i+1}: {len(group)} entries, {size_mb:.1f} MB")
            else:
                main_window.log_message(f"❌ Failed to create part {i+1}")

        return success_count == len(entry_groups)

    except Exception as e:
        main_window.log_message(f"❌ File size split failed: {str(e)}")
        return False


def split_by_file_type(main_window, img_file, config: Dict[str, Any]) -> bool: #vers 1
    """Split IMG by file type extensions"""
    try:
        if not hasattr(img_file, 'entries') or not img_file.entries:
            main_window.log_message("❌ No entries to split")
            return False

        entries = img_file.entries
        file_types = config.get('file_types', [])
        
        if not file_types:
            main_window.log_message("❌ No file types selected for split")
            return False

        main_window.log_message(f"📊 Splitting by file types: {', '.join(file_types)}")

        # Group entries by file type
        type_groups = {}
        other_entries = []

        for entry in entries:
            entry_name = getattr(entry, 'name', '')
            entry_ext = os.path.splitext(entry_name)[1].lower()
            
            if entry_ext in file_types:
                if entry_ext not in type_groups:
                    type_groups[entry_ext] = []
                type_groups[entry_ext].append(entry)
            else:
                other_entries.append(entry)

        # Add "other" group if there are unmatched entries
        if other_entries:
            type_groups['other'] = other_entries

        main_window.log_message(f"📊 Created {len(type_groups)} type-based groups")

        # Create split IMG files
        success_count = 0
        for file_type, group in type_groups.items():
            if not group:
                continue
                
            suffix = file_type.replace('.', '') if file_type != 'other' else 'other'
            output_path = _get_split_output_path(config, img_file, suffix)
            
            if _create_split_img(main_window, group, output_path):
                success_count += 1
                main_window.log_message(f"✅ Created {suffix} part: {len(group)} entries")
            else:
                main_window.log_message(f"❌ Failed to create {suffix} part")

        return success_count == len(type_groups)

    except Exception as e:
        main_window.log_message(f"❌ File type split failed: {str(e)}")
        return False


def _create_split_img(main_window, entries: List[Any], output_path: str) -> bool: #vers 1
    """Create a split IMG file with given entries"""
    try:
        # Import IMG core classes
        from methods.img_core_classes import IMGFile
        
        # Create new IMG file
        split_img = IMGFile()
        split_img.entries = entries
        split_img.file_path = output_path
        
        # Save the split IMG
        if hasattr(split_img, 'save_to_file'):
            success = split_img.save_to_file(output_path)
        else:
            # Fallback to basic writing
            success = _write_split_img_file(main_window, entries, output_path)
        
        return success and os.path.exists(output_path)

    except Exception as e:
        main_window.log_message(f"❌ Failed to create split IMG: {str(e)}")
        return False


def _write_split_img_file(main_window, entries: List[Any], output_path: str) -> bool: #vers 1
    """Write split IMG file using basic format"""
    try:
        with open(output_path, 'wb') as f:
            # Write IMG header
            f.write(b'VER2')  # Version signature
            f.write(len(entries).to_bytes(4, 'little'))  # Entry count

            # Calculate data start offset
            header_size = 8
            directory_size = len(entries) * 32
            data_start = header_size + directory_size

            # Write directory entries
            current_offset = data_start
            for entry in entries:
                entry_size = getattr(entry, 'size', 0)
                
                # Write directory entry
                f.write(current_offset.to_bytes(4, 'little'))  # Offset
                f.write(entry_size.to_bytes(4, 'little'))      # Size
                
                # Write entry name (24 bytes, null-padded)
                name = getattr(entry, 'name', '').encode('ascii', errors='ignore')[:23]
                name_padded = name.ljust(24, b'\x00')
                f.write(name_padded)
                
                current_offset += entry_size

            # Write file data
            for entry in entries:
                if hasattr(entry, 'get_data'):
                    data = entry.get_data()
                elif hasattr(entry, 'data'):
                    data = entry.data
                else:
                    data = b''  # Placeholder
                
                if data:
                    f.write(data)

        return True

    except Exception as e:
        main_window.log_message(f"❌ Failed to write split IMG file: {str(e)}")
        return False


def _get_split_output_path(config: Dict[str, Any], img_file, suffix: str) -> str: #vers 1
    """Get output path for split IMG file"""
    try:
        output_dir = config['output_dir']
        original_name = os.path.basename(getattr(img_file, 'file_path', 'unknown.img'))
        base_name, ext = os.path.splitext(original_name)
        
        split_name = f"{base_name}_{suffix}{ext}"
        return os.path.join(output_dir, split_name)

    except:
        return os.path.join(os.path.expanduser("~/Desktop"), f"split_{suffix}.img")


def validate_split_operation(main_window) -> bool: #vers 1
    """Validate if split operation can proceed"""
    try:
        if not hasattr(main_window, 'tab_widget') or main_window.tab_widget.count() == 0:
            main_window.log_message("❌ No IMG file loaded")
            return False

        # Check if any operations are running
        if hasattr(main_window, 'progress_dialog') and main_window.progress_dialog.isVisible():
            QMessageBox.warning(
                main_window,
                "Operation in Progress",
                "Cannot split IMG file while another operation is in progress.\n"
                "Please wait for the current operation to complete."
            )
            return False

        return True

    except Exception as e:
        main_window.log_message(f"❌ Split validation failed: {str(e)}")
        return False


def integrate_split_functions(main_window) -> bool: #vers 1
    """Integrate split functions into main window"""
    try:
        # Add split functions to main window
        main_window.split_img = lambda: split_img(main_window)
        main_window.split_by_parts_count = lambda img_file, config: split_by_parts_count(main_window, img_file, config)
        main_window.split_by_file_size = lambda img_file, config: split_by_file_size(main_window, img_file, config)
        main_window.split_by_file_type = lambda img_file, config: split_by_file_type(main_window, img_file, config)
        main_window.split_by_ide_sections = lambda img_file, config: split_by_ide_sections(main_window, img_file, config)
        main_window.split_by_ide_list = lambda img_file, config: split_by_ide_list(main_window, img_file, config)
        main_window.validate_split_operation = lambda: validate_split_operation(main_window)
        
        main_window.log_message("✅ Split functions integrated")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Failed to integrate split functions: {str(e)}")
        return False
