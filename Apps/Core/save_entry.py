#this belongs in Core/save_entry.py - Version: 1
# X-Seti - September11 2025 - IMG Factory 1.5 - Save Entry Operations

"""
Save Entry Operations - Handles saving individual IMG entries to disk
Core operations for extracting and saving specific entries from IMG files
"""

import os
import shutil
from typing import Optional, List, Dict, Any
from pathlib import Path
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PyQt6.QtCore import Qt

##Methods list -
# save_img_entry
# save_selected_entries
# save_entry_to_file
# get_save_location_for_entry
# validate_save_entry_operation
# _extract_entry_data
# _save_single_entry
# get_entry_save_filter

def save_img_entry(main_window) -> bool: #vers 1
    """Save the currently selected IMG entry to disk"""
    try:
        if not hasattr(main_window, 'tab_widget') or main_window.tab_widget.count() == 0:
            main_window.log_message("❌ No IMG file loaded")
            return False

        # Get current tab and its IMG file
        current_tab = main_window.tab_widget.currentWidget()
        if not current_tab or not hasattr(current_tab, 'img_file'):
            main_window.log_message("❌ No active IMG file")
            return False

        img_file = current_tab.img_file
        
        # Get selected entries from table
        selected_entries = []
        if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'table'):
            table = main_window.gui_layout.table
            selected_rows = set()
            
            for item in table.selectedItems():
                selected_rows.add(item.row())
            
            if not selected_rows:
                main_window.log_message("❌ No entries selected")
                return False

            # Get entry names from selected rows
            for row in selected_rows:
                if row < table.rowCount():
                    name_item = table.item(row, 0)  # Assuming name is in first column
                    if name_item:
                        entry_name = name_item.text()
                        # Find matching entry in IMG file
                        for entry in img_file.entries:
                            if entry.name.lower() == entry_name.lower():
                                selected_entries.append(entry)
                                break

        if not selected_entries:
            main_window.log_message("❌ No valid entries found for saving")
            return False

        # Save entries
        if len(selected_entries) == 1:
            return _save_single_entry(main_window, selected_entries[0], img_file)
        else:
            return save_selected_entries(main_window, selected_entries, img_file)

    except Exception as e:
        main_window.log_message(f"❌ Save entry operation failed: {str(e)}")
        return False


def save_selected_entries(main_window, entries: List[Any], img_file) -> bool: #vers 1
    """Save multiple selected entries to disk"""
    try:
        if not entries:
            return False

        # Get save directory
        save_dir = QFileDialog.getExistingDirectory(
            main_window,
            f"Select folder to save {len(entries)} entries",
            os.path.expanduser("~/Desktop"),
            QFileDialog.Option.ShowDirsOnly
        )

        if not save_dir:
            return False

        saved_count = 0
        failed_count = 0

        main_window.log_message(f"💾 Saving {len(entries)} entries to: {save_dir}")

        for entry in entries:
            try:
                output_path = os.path.join(save_dir, entry.name)
                success = save_entry_to_file(main_window, entry, img_file, output_path)
                
                if success:
                    saved_count += 1
                else:
                    failed_count += 1
                    
            except Exception as e:
                main_window.log_message(f"⚠️ Failed to save {entry.name}: {str(e)}")
                failed_count += 1

        # Report results
        if saved_count > 0:
            main_window.log_message(f"✅ Saved {saved_count} entries successfully")
            
        if failed_count > 0:
            main_window.log_message(f"⚠️ Failed to save {failed_count} entries")

        return saved_count > 0

    except Exception as e:
        main_window.log_message(f"❌ Multiple entry save failed: {str(e)}")
        return False


def _save_single_entry(main_window, entry, img_file) -> bool: #vers 1
    """Save a single entry with file dialog"""
    try:
        # Get file extension for filter
        file_filter = get_entry_save_filter(entry.name)
        
        # Default filename
        default_name = entry.name
        
        # Get save location
        output_path, selected_filter = QFileDialog.getSaveFileName(
            main_window,
            f"Save entry: {entry.name}",
            os.path.join(os.path.expanduser("~/Desktop"), default_name),
            file_filter
        )

        if not output_path:
            return False

        # Save the entry
        success = save_entry_to_file(main_window, entry, img_file, output_path)
        
        if success:
            main_window.log_message(f"✅ Saved entry: {entry.name} → {os.path.basename(output_path)}")
            return True
        else:
            main_window.log_message(f"❌ Failed to save entry: {entry.name}")
            return False

    except Exception as e:
        main_window.log_message(f"❌ Single entry save failed: {str(e)}")
        return False


def save_entry_to_file(main_window, entry, img_file, output_path: str) -> bool: #vers 1
    """Extract and save entry data to specified file path"""
    try:
        if not validate_save_entry_operation(main_window, entry, output_path):
            return False

        # Extract entry data
        entry_data = _extract_entry_data(main_window, entry, img_file)
        if not entry_data:
            main_window.log_message(f"❌ Failed to extract data for: {entry.name}")
            return False

        # Create output directory if needed
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Check for existing file
        if os.path.exists(output_path):
            reply = QMessageBox.question(
                main_window,
                "File Exists",
                f"File '{os.path.basename(output_path)}' already exists.\n\nOverwrite?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply != QMessageBox.StandardButton.Yes:
                return False

        # Write data to file
        with open(output_path, 'wb') as f:
            f.write(entry_data)

        # Verify file was written correctly
        if os.path.exists(output_path) and os.path.getsize(output_path) == len(entry_data):
            return True
        else:
            main_window.log_message(f"❌ File verification failed for: {os.path.basename(output_path)}")
            return False

    except Exception as e:
        main_window.log_message(f"❌ Save to file failed: {str(e)}")
        return False


def _extract_entry_data(main_window, entry, img_file) -> Optional[bytes]: #vers 1
    """Extract raw data from IMG entry"""
    try:
        if not hasattr(entry, 'offset') or not hasattr(entry, 'size'):
            main_window.log_message(f"❌ Entry missing offset/size information: {entry.name}")
            return None

        if not hasattr(img_file, 'file_path') or not os.path.exists(img_file.file_path):
            main_window.log_message(f"❌ IMG file not accessible: {getattr(img_file, 'file_path', 'unknown')}")
            return None

        # Read data from IMG file
        with open(img_file.file_path, 'rb') as f:
            f.seek(entry.offset)
            data = f.read(entry.size)
            
            if len(data) != entry.size:
                main_window.log_message(f"❌ Data size mismatch for {entry.name}: expected {entry.size}, got {len(data)}")
                return None
                
            return data

    except Exception as e:
        main_window.log_message(f"❌ Data extraction failed for {entry.name}: {str(e)}")
        return None


def get_entry_save_filter(filename: str) -> str: #vers 1
    """Get appropriate file filter based on entry filename"""
    try:
        ext = os.path.splitext(filename)[1].lower()
        
        filter_map = {
            '.dff': "DFF Models (*.dff);;All Files (*.*)",
            '.txd': "TXD Textures (*.txd);;All Files (*.*)",
            '.col': "COL Collision (*.col);;All Files (*.*)",
            '.ide': "IDE Definition (*.ide);;All Files (*.*)",
            '.ipl': "IPL Placement (*.ipl);;All Files (*.*)",
            '.dat': "DAT Data (*.dat);;All Files (*.*)",
            '.img': "IMG Archive (*.img);;All Files (*.*)",
            '.wav': "WAV Audio (*.wav);;All Files (*.*)",
            '.mp3': "MP3 Audio (*.mp3);;All Files (*.*)",
        }
        
        return filter_map.get(ext, "All Files (*.*)")

    except:
        return "All Files (*.*)"


def validate_save_entry_operation(main_window, entry, output_path: str) -> bool: #vers 1
    """Validate if save entry operation can proceed"""
    try:
        if not entry:
            main_window.log_message("❌ Invalid entry for save operation")
            return False

        if not hasattr(entry, 'name') or not entry.name:
            main_window.log_message("❌ Entry missing name")
            return False

        if not hasattr(entry, 'size') or entry.size <= 0:
            main_window.log_message(f"❌ Entry has invalid size: {getattr(entry, 'size', 'unknown')}")
            return False

        if not output_path or not output_path.strip():
            main_window.log_message("❌ Invalid output path")
            return False

        # Check if output directory is writable
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.access(output_dir, os.W_OK):
            main_window.log_message(f"❌ Output directory not writable: {output_dir}")
            return False

        return True

    except Exception as e:
        main_window.log_message(f"❌ Save validation failed: {str(e)}")
        return False


def get_save_location_for_entry(main_window, entry_name: str) -> Optional[str]: #vers 1
    """Get save location for a specific entry"""
    try:
        # Get default save directory (Desktop or last used)
        default_dir = os.path.expanduser("~/Desktop")
        
        if hasattr(main_window, 'last_save_directory') and main_window.last_save_directory:
            if os.path.exists(main_window.last_save_directory):
                default_dir = main_window.last_save_directory

        default_path = os.path.join(default_dir, entry_name)
        file_filter = get_entry_save_filter(entry_name)

        save_path, _ = QFileDialog.getSaveFileName(
            main_window,
            f"Save Entry: {entry_name}",
            default_path,
            file_filter
        )

        if save_path:
            # Remember the directory for next time
            main_window.last_save_directory = os.path.dirname(save_path)
            return save_path

        return None

    except Exception as e:
        main_window.log_message(f"❌ Save location dialog failed: {str(e)}")
        return None


def integrate_save_entry_function(main_window) -> bool: #vers 1
    """Integrate save entry functions into main window"""
    try:
        # Add save entry functions to main window
        main_window.save_img_entry = lambda: save_img_entry(main_window)
        main_window.save_selected_entries = lambda entries, img_file: save_selected_entries(main_window, entries, img_file)
        main_window.save_entry_to_file = lambda entry, img_file, output_path: save_entry_to_file(main_window, entry, img_file, output_path)
        main_window.get_save_location_for_entry = lambda entry_name: get_save_location_for_entry(main_window, entry_name)
        
        # Initialize save directory tracking
        if not hasattr(main_window, 'last_save_directory'):
            main_window.last_save_directory = os.path.expanduser("~/Desktop")
        
        main_window.log_message("✅ Save entry functions integrated")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Failed to integrate save entry functions: {str(e)}")
        return False