#this belongs in Core/convert.py - Version: 1
# X-Seti - September11 2025 - IMG Factory 1.5 - IMG Format Conversion

"""
IMG Format Conversion - Handles converting IMG files between different versions
Core operations for converting IMG v1/v2 formats and updating headers
"""

import os
import struct
import tempfile
import shutil
from typing import Optional, Dict, Any
from pathlib import Path
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QCheckBox, QFileDialog, QMessageBox
from PyQt6.QtCore import Qt

##Methods list -
# convert_img_format
# show_conversion_dialog
# convert_img_v1_to_v2
# convert_img_v2_to_v1
# detect_img_version
# validate_conversion_operation
# _update_img_header
# _convert_directory_structure
# _create_converted_img

class IMGConversionDialog(QDialog): #vers 1
    """Dialog for configuring IMG format conversion"""
    
    def __init__(self, parent=None, img_file=None):
        super().__init__(parent)
        self.img_file = img_file
        self.conversion_config = None
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Convert IMG Format")
        self.setModal(True)
        self.resize(400, 250)
        
        layout = QVBoxLayout(self)
        
        # Current file info
        if self.img_file:
            file_name = getattr(self.img_file, 'file_path', 'Unknown')
            current_version = detect_img_version(self.img_file)
            entry_count = len(getattr(self.img_file, 'entries', []))
            
            info_label = QLabel(f"File: {os.path.basename(file_name)}\n"
                               f"Current Version: {current_version}\n"
                               f"Entries: {entry_count}")
            layout.addWidget(info_label)
        
        # Target version selection
        version_layout = QHBoxLayout()
        version_layout.addWidget(QLabel("Convert to:"))
        
        self.version_combo = QComboBox()
        self.version_combo.addItems([
            "IMG Version 1 (GTA III/VC)",
            "IMG Version 2 (GTA SA)",
            "Auto-detect Best Format"
        ])
        
        # Set default based on current version
        if self.img_file:
            current_ver = detect_img_version(self.img_file)
            if "Version 1" in current_ver:
                self.version_combo.setCurrentText("IMG Version 2 (GTA SA)")
            else:
                self.version_combo.setCurrentText("IMG Version 1 (GTA III/VC)")
        
        version_layout.addWidget(self.version_combo)
        layout.addLayout(version_layout)
        
        # Conversion options
        options_layout = QVBoxLayout()
        options_layout.addWidget(QLabel("Conversion Options:"))
        
        self.backup_check = QCheckBox("Create backup of original file")
        self.backup_check.setChecked(True)
        options_layout.addWidget(self.backup_check)
        
        self.optimize_check = QCheckBox("Optimize entry order for faster access")
        self.optimize_check.setChecked(False)
        options_layout.addWidget(self.optimize_check)
        
        self.verify_check = QCheckBox("Verify converted file integrity")
        self.verify_check.setChecked(True)
        options_layout.addWidget(self.verify_check)
        
        layout.addLayout(options_layout)
        
        # Output location
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output:"))
        
        self.output_combo = QComboBox()
        self.output_combo.addItems([
            "Replace original file",
            "Save as new file"
        ])
        output_layout.addWidget(self.output_combo)
        layout.addLayout(output_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.convert_btn = QPushButton("Convert IMG")
        self.convert_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.convert_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def get_conversion_config(self):
        """Get the conversion configuration from dialog"""
        target_version = self.version_combo.currentText()
        
        if "Version 1" in target_version:
            target_format = "v1"
        elif "Version 2" in target_version:
            target_format = "v2"
        else:
            target_format = "auto"
        
        return {
            'target_format': target_format,
            'create_backup': self.backup_check.isChecked(),
            'optimize_order': self.optimize_check.isChecked(),
            'verify_integrity': self.verify_check.isChecked(),
            'replace_original': self.output_combo.currentText() == "Replace original file"
        }


def convert_img_format(main_window) -> bool: #vers 1
    """Main function to convert IMG format"""
    try:
        if not validate_conversion_operation(main_window):
            return False

        # Get current IMG file
        current_tab = main_window.tab_widget.currentWidget()
        if not current_tab or not hasattr(current_tab, 'img_file'):
            main_window.log_message("❌ No active IMG file to convert")
            return False

        img_file = current_tab.img_file
        
        # Show conversion dialog
        conversion_config = show_conversion_dialog(main_window, img_file)
        if not conversion_config:
            main_window.log_message("❌ Conversion cancelled")
            return False

        current_version = detect_img_version(img_file)
        target_format = conversion_config['target_format']
        
        main_window.log_message(f"🔄 Converting from {current_version} to {target_format.upper()}")

        # Determine actual conversion needed
        if target_format == "auto":
            # Auto-detect best format based on content
            target_format = _determine_optimal_format(main_window, img_file)
            main_window.log_message(f"📊 Auto-selected format: {target_format.upper()}")

        # Check if conversion is actually needed
        if _is_conversion_needed(current_version, target_format):
            # Perform conversion
            success = _perform_format_conversion(main_window, img_file, target_format, conversion_config)
            
            if success:
                main_window.log_message(f"✅ IMG format converted successfully to {target_format.upper()}")
                
                # Refresh table if needed
                if hasattr(main_window, 'refresh_table_display'):
                    main_window.refresh_table_display()
                
                return True
            else:
                main_window.log_message("❌ IMG format conversion failed")
                return False
        else:
            main_window.log_message(f"ℹ️ IMG is already in {target_format.upper()} format")
            return True

    except Exception as e:
        main_window.log_message(f"❌ Conversion operation failed: {str(e)}")
        return False


def show_conversion_dialog(main_window, img_file) -> Optional[Dict[str, Any]]: #vers 1
    """Show conversion configuration dialog"""
    try:
        dialog = IMGConversionDialog(main_window, img_file)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.get_conversion_config()
        else:
            return None

    except Exception as e:
        main_window.log_message(f"❌ Conversion dialog failed: {str(e)}")
        return None


def detect_img_version(img_file) -> str: #vers 1
    """Detect the version of an IMG file"""
    try:
        if not hasattr(img_file, 'file_path') or not os.path.exists(img_file.file_path):
            return "Unknown"

        with open(img_file.file_path, 'rb') as f:
            # Read first 4 bytes for version signature
            signature = f.read(4)
            
            if signature == b'VER2':
                return "IMG Version 2"
            elif len(signature) == 4 and signature[0:1] != b'VER':
                # Likely Version 1 (starts with entry count)
                return "IMG Version 1"
            else:
                return "Unknown Format"

    except Exception as e:
        return "Detection Failed"


def _perform_format_conversion(main_window, img_file, target_format: str, config: Dict[str, Any]) -> bool: #vers 1
    """Perform the actual format conversion"""
    try:
        file_path = getattr(img_file, 'file_path', '')
        
        # Create backup if requested
        if config.get('create_backup', True):
            backup_path = f"{file_path}.backup"
            shutil.copy2(file_path, backup_path)
            main_window.log_message(f"💾 Created backup: {os.path.basename(backup_path)}")

        # Determine output path
        if config.get('replace_original', True):
            output_path = file_path
            # Use temporary file for conversion
            temp_path = f"{file_path}.tmp"
        else:
            # Get new file path
            base_name, ext = os.path.splitext(file_path)
            output_path = f"{base_name}_{target_format}{ext}"
            temp_path = output_path

        # Perform conversion based on target format
        success = False
        if target_format == "v1":
            success = convert_img_v2_to_v1(main_window, img_file, temp_path)
        elif target_format == "v2":
            success = convert_img_v1_to_v2(main_window, img_file, temp_path)

        if success:
            # Replace original file if needed
            if config.get('replace_original', True) and temp_path != output_path:
                shutil.move(temp_path, output_path)
            
            # Verify integrity if requested
            if config.get('verify_integrity', True):
                if _verify_converted_img(main_window, output_path):
                    main_window.log_message("✅ Conversion integrity verified")
                else:
                    main_window.log_message("⚠️ Conversion integrity check failed")
            
            return True
        else:
            # Clean up temp file on failure
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass
            return False

    except Exception as e:
        main_window.log_message(f"❌ Format conversion failed: {str(e)}")
        return False


def convert_img_v1_to_v2(main_window, img_file, output_path: str) -> bool: #vers 1
    """Convert IMG Version 1 to Version 2"""
    try:
        if not hasattr(img_file, 'entries') or not img_file.entries:
            return False

        entries = img_file.entries
        
        with open(output_path, 'wb') as f:
            # Write Version 2 header
            f.write(b'VER2')  # Version signature
            f.write(len(entries).to_bytes(4, 'little'))  # Entry count

            # Calculate data start offset (header + directory)
            header_size = 8
            directory_size = len(entries) * 32  # 32 bytes per entry in v2
            data_start = header_size + directory_size

            # Write directory entries (Version 2 format)
            current_offset = data_start
            for entry in entries:
                entry_size = getattr(entry, 'size', 0)
                
                # Version 2 directory entry format
                f.write(current_offset.to_bytes(4, 'little'))  # Offset
                f.write(entry_size.to_bytes(4, 'little'))      # Size
                
                # Entry name (24 bytes, null-padded)
                name = getattr(entry, 'name', '').encode('ascii', errors='ignore')[:23]
                name_padded = name.ljust(24, b'\x00')
                f.write(name_padded)
                
                current_offset += entry_size

            # Copy file data
            _copy_entry_data(main_window, img_file, f, entries)

        main_window.log_message("🔄 Converted to IMG Version 2 format")
        return True

    except Exception as e:
        main_window.log_message(f"❌ V1 to V2 conversion failed: {str(e)}")
        return False


def convert_img_v2_to_v1(main_window, img_file, output_path: str) -> bool: #vers 1
    """Convert IMG Version 2 to Version 1"""
    try:
        if not hasattr(img_file, 'entries') or not img_file.entries:
            return False

        entries = img_file.entries
        
        with open(output_path, 'wb') as f:
            # Write Version 1 header (no signature, just entry count)
            f.write(len(entries).to_bytes(4, 'little'))  # Entry count

            # Calculate data start offset (header + directory)
            header_size = 4
            directory_size = len(entries) * 32  # Same as v2
            data_start = header_size + directory_size

            # Write directory entries (Version 1 format)
            current_offset = data_start
            for entry in entries:
                entry_size = getattr(entry, 'size', 0)
                
                # Version 1 directory entry format (similar to v2 but no signature)
                f.write(current_offset.to_bytes(4, 'little'))  # Offset
                f.write(entry_size.to_bytes(4, 'little'))      # Size
                
                # Entry name (24 bytes, null-padded)
                name = getattr(entry, 'name', '').encode('ascii', errors='ignore')[:23]
                name_padded = name.ljust(24, b'\x00')
                f.write(name_padded)
                
                current_offset += entry_size

            # Copy file data
            _copy_entry_data(main_window, img_file, f, entries)

        main_window.log_message("🔄 Converted to IMG Version 1 format")
        return True

    except Exception as e:
        main_window.log_message(f"❌ V2 to V1 conversion failed: {str(e)}")
        return False


def _copy_entry_data(main_window, img_file, output_file, entries) -> bool: #vers 1
    """Copy entry data from source IMG to output file"""
    try:
        source_path = getattr(img_file, 'file_path', '')
        if not os.path.exists(source_path):
            return False

        with open(source_path, 'rb') as source_file:
            for entry in entries:
                if hasattr(entry, 'offset') and hasattr(entry, 'size'):
                    # Read data from source
                    source_file.seek(entry.offset)
                    data = source_file.read(entry.size)
                    
                    # Write to output
                    output_file.write(data)

        return True

    except Exception as e:
        main_window.log_message(f"❌ Data copy failed: {str(e)}")
        return False


def _determine_optimal_format(main_window, img_file) -> str: #vers 1
    """Determine optimal IMG format based on content"""
    try:
        # Simple heuristic: prefer v2 for larger files, v1 for smaller
        if hasattr(img_file, 'entries'):
            entry_count = len(img_file.entries)
            
            # Calculate total size estimate
            total_size = sum(getattr(entry, 'size', 0) for entry in img_file.entries)
            
            # Use v2 for files > 100MB or > 1000 entries (SA style)
            if total_size > 100 * 1024 * 1024 or entry_count > 1000:
                return "v2"
            else:
                return "v1"
        
        return "v2"  # Default to v2

    except:
        return "v2"


def _is_conversion_needed(current_version: str, target_format: str) -> bool: #vers 1
    """Check if conversion is actually needed"""
    try:
        if target_format == "v1" and "Version 1" in current_version:
            return False
        elif target_format == "v2" and "Version 2" in current_version:
            return False
        else:
            return True

    except:
        return True


def _verify_converted_img(main_window, file_path: str) -> bool: #vers 1
    """Verify the integrity of converted IMG file"""
    try:
        if not os.path.exists(file_path):
            return False

        # Basic verification: try to read header and directory
        with open(file_path, 'rb') as f:
            # Check header
            header = f.read(8)
            if len(header) < 4:
                return False

            # Determine version and read entry count
            if header[:4] == b'VER2':
                entry_count = int.from_bytes(header[4:8], 'little')
            else:
                entry_count = int.from_bytes(header[:4], 'little')
                f.seek(4)  # Reset for v1

            # Verify entry count is reasonable
            if entry_count < 0 or entry_count > 100000:
                return False

            # Try to read directory entries
            directory_size = entry_count * 32
            directory_data = f.read(directory_size)
            
            if len(directory_data) != directory_size:
                return False

        return True

    except Exception as e:
        main_window.log_message(f"⚠️ Verification failed: {str(e)}")
        return False


def validate_conversion_operation(main_window) -> bool: #vers 1
    """Validate if conversion operation can proceed"""
    try:
        if not hasattr(main_window, 'tab_widget') or main_window.tab_widget.count() == 0:
            main_window.log_message("❌ No IMG file loaded")
            return False

        # Check if any operations are running
        if hasattr(main_window, 'progress_dialog') and main_window.progress_dialog.isVisible():
            QMessageBox.warning(
                main_window,
                "Operation in Progress",
                "Cannot convert IMG format while another operation is in progress.\n"
                "Please wait for the current operation to complete."
            )
            return False

        return True

    except Exception as e:
        main_window.log_message(f"❌ Conversion validation failed: {str(e)}")
        return False


def integrate_convert_functions(main_window) -> bool: #vers 1
    """Integrate convert functions into main window"""
    try:
        # Add convert functions to main window
        main_window.convert_img_format = lambda: convert_img_format(main_window)
        main_window.convert_img_v1_to_v2 = lambda img_file, output_path: convert_img_v1_to_v2(main_window, img_file, output_path)
        main_window.convert_img_v2_to_v1 = lambda img_file, output_path: convert_img_v2_to_v1(main_window, img_file, output_path)
        main_window.detect_img_version = lambda img_file: detect_img_version(img_file)
        main_window.validate_conversion_operation = lambda: validate_conversion_operation(main_window)
        
        main_window.log_message("✅ Convert functions integrated")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Failed to integrate convert functions: {str(e)}")
        return False