#this belongs in Core/merge.py - Version: 1
# X-Seti - September11 2025 - IMG Factory 1.5 - Merge IMG Operations

"""
Merge IMG Operations - Handles merging multiple IMG files into one
Core operations for combining IMG archives and managing duplicate entries
"""

import os
import tempfile
from typing import Optional, List, Dict, Any, Set
from pathlib import Path
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QInputDialog
from PyQt6.QtCore import Qt

##Methods list -
# merge_img
# merge_multiple_imgs
# select_imgs_for_merge
# handle_duplicate_entries
# create_merged_img
# validate_merge_operation
# _combine_img_entries
# _resolve_entry_conflicts
# _write_merged_img_file

def merge_img(main_window) -> bool: #vers 1
    """Main function to merge IMG files"""
    try:
        if not validate_merge_operation(main_window):
            return False

        main_window.log_message("🔗 Starting IMG merge operation")

        # Get IMG files to merge
        img_files_to_merge = select_imgs_for_merge(main_window)
        if not img_files_to_merge:
            main_window.log_message("❌ No IMG files selected for merge")
            return False

        if len(img_files_to_merge) < 2:
            main_window.log_message("❌ Need at least 2 IMG files to merge")
            return False

        # Get output location
        output_path, _ = QFileDialog.getSaveFileName(
            main_window,
            "Save Merged IMG File",
            os.path.join(os.path.expanduser("~/Desktop"), "merged.img"),
            "IMG Archives (*.img);;All Files (*.*)"
        )

        if not output_path:
            main_window.log_message("❌ No output file selected")
            return False

        # Perform merge
        success = merge_multiple_imgs(main_window, img_files_to_merge, output_path)
        
        if success:
            main_window.log_message(f"✅ Successfully merged {len(img_files_to_merge)} IMG files")
            
            # Ask if user wants to open the merged file
            reply = QMessageBox.question(
                main_window,
                "Merge Complete",
                f"IMG files merged successfully!\n\nOpen the merged file?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            
            if reply == QMessageBox.StandardButton.Yes and hasattr(main_window, 'open_img_file'):
                main_window.open_img_file(output_path)
            
            return True
        else:
            main_window.log_message("❌ IMG merge operation failed")
            return False

    except Exception as e:
        main_window.log_message(f"❌ Failed to write merged IMG file: {str(e)}")
        return False


def validate_merge_operation(main_window) -> bool: #vers 1
    """Validate if merge operation can proceed"""
    try:
        # Check if any operations are running
        if hasattr(main_window, 'progress_dialog') and main_window.progress_dialog.isVisible():
            QMessageBox.warning(
                main_window,
                "Operation in Progress",
                "Cannot merge IMG files while another operation is in progress.\n"
                "Please wait for the current operation to complete."
            )
            return False

        return True

    except Exception as e:
        main_window.log_message(f"❌ Merge validation failed: {str(e)}")
        return False


def handle_duplicate_entries(main_window, duplicates: List[Dict[str, Any]]) -> str: #vers 1
    """Handle duplicate entries during merge"""
    try:
        if not duplicates:
            return "none"

        # Show resolution options
        msg = QMessageBox(main_window)
        msg.setWindowTitle("Duplicate Entries Found")
        msg.setText(f"Found {len(duplicates)} duplicate entries.\n\nHow should duplicates be handled?")
        
        skip_btn = msg.addButton("Skip Duplicates", QMessageBox.ButtonRole.AcceptRole)
        replace_btn = msg.addButton("Replace with Newer", QMessageBox.ButtonRole.AcceptRole)
        rename_btn = msg.addButton("Rename Duplicates", QMessageBox.ButtonRole.AcceptRole)
        cancel_btn = msg.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
        
        msg.setDefaultButton(replace_btn)
        msg.exec()
        
        clicked_button = msg.clickedButton()
        
        if clicked_button == skip_btn:
            return "skip"
        elif clicked_button == replace_btn:
            return "replace"
        elif clicked_button == rename_btn:
            return "rename"
        else:
            return "cancel"

    except Exception as e:
        main_window.log_message(f"❌ Duplicate handling failed: {str(e)}")
        return "cancel"


def get_merge_statistics(main_window, img_files: List[str]) -> Dict[str, Any]: #vers 1
    """Get statistics about IMG files to be merged"""
    try:
        stats = {
            'total_files': len(img_files),
            'total_entries': 0,
            'total_size': 0,
            'file_details': []
        }

        for file_path in img_files:
            try:
                file_size = os.path.getsize(file_path)
                stats['total_size'] += file_size
                
                # Try to load IMG to get entry count
                from methods.img_core_classes import IMGFile
                img_file = IMGFile()
                
                entry_count = 0
                if img_file.load_from_file(file_path):
                    if hasattr(img_file, 'entries'):
                        entry_count = len(img_file.entries)
                        stats['total_entries'] += entry_count

                stats['file_details'].append({
                    'path': file_path,
                    'name': os.path.basename(file_path),
                    'size': file_size,
                    'entries': entry_count
                })

            except Exception as e:
                main_window.log_message(f"⚠️ Failed to analyze {os.path.basename(file_path)}: {str(e)}")

        return stats

    except Exception as e:
        main_window.log_message(f"❌ Failed to get merge statistics: {str(e)}")
        return {'total_files': 0, 'total_entries': 0, 'total_size': 0, 'file_details': []}


def integrate_merge_functions(main_window) -> bool: #vers 1
    """Integrate merge functions into main window"""
    try:
        # Add merge functions to main window
        main_window.merge_img = lambda: merge_img(main_window)
        main_window.merge_multiple_imgs = lambda img_files, output_path: merge_multiple_imgs(main_window, img_files, output_path)
        main_window.select_imgs_for_merge = lambda: select_imgs_for_merge(main_window)
        main_window.validate_merge_operation = lambda: validate_merge_operation(main_window)
        main_window.get_merge_statistics = lambda img_files: get_merge_statistics(main_window, img_files)
        
        main_window.log_message("✅ Merge functions integrated")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Failed to integrate merge functions: {str(e)}")
        return Falsemessage(f"❌ Merge operation failed: {str(e)}")
        return False


def select_imgs_for_merge(main_window) -> List[str]: #vers 1
    """Select IMG files for merging"""
    try:
        # Show selection dialog
        msg = QMessageBox(main_window)
        msg.setWindowTitle("Select IMG Files to Merge")
        msg.setText("Choose source for IMG files to merge:")
        
        # Add custom buttons
        open_tabs_btn = msg.addButton("Use Open Tabs", QMessageBox.ButtonRole.AcceptRole)
        select_files_btn = msg.addButton("Select Files", QMessageBox.ButtonRole.AcceptRole)
        cancel_btn = msg.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
        
        msg.setDefaultButton(select_files_btn)
        msg.exec()
        
        clicked_button = msg.clickedButton()
        
        if clicked_button == open_tabs_btn:
            # Use open tabs
            return _get_img_files_from_tabs(main_window)
        elif clicked_button == select_files_btn:
            # Select files manually
            return _select_img_files_manually(main_window)
        else:
            return []

    except Exception as e:
        main_window.log_message(f"❌ IMG file selection failed: {str(e)}")
        return []


def _get_img_files_from_tabs(main_window) -> List[str]: #vers 1
    """Get IMG files from currently open tabs"""
    try:
        img_files = []
        
        if hasattr(main_window, 'tab_widget'):
            for i in range(main_window.tab_widget.count()):
                tab_data = main_window.tab_widget.widget(i)
                if hasattr(tab_data, 'img_file'):
                    img_file = tab_data.img_file
                    file_path = getattr(img_file, 'file_path', None)
                    if file_path and os.path.exists(file_path):
                        img_files.append(file_path)

        if len(img_files) < 2:
            QMessageBox.warning(
                main_window,
                "Insufficient Files",
                f"Only {len(img_files)} IMG file(s) open.\nNeed at least 2 files to merge."
            )
            return []

        return img_files

    except Exception as e:
        main_window.log_message(f"❌ Failed to get IMG files from tabs: {str(e)}")
        return []


def _select_img_files_manually(main_window) -> List[str]: #vers 1
    """Manually select IMG files for merging"""
    try:
        file_paths, _ = QFileDialog.getOpenFileNames(
            main_window,
            "Select IMG Files to Merge",
            os.path.expanduser("~/Desktop"),
            "IMG Archives (*.img);;All Files (*.*)"
        )

        if len(file_paths) < 2:
            if file_paths:
                QMessageBox.warning(
                    main_window,
                    "Insufficient Files",
                    f"Selected {len(file_paths)} file(s).\nNeed at least 2 files to merge."
                )
            return []

        return file_paths

    except Exception as e:
        main_window.log_message(f"❌ Manual file selection failed: {str(e)}")
        return []


def merge_multiple_imgs(main_window, img_files: List[str], output_path: str) -> bool: #vers 1
    """Merge multiple IMG files into one"""
    try:
        main_window.log_message(f"🔗 Merging {len(img_files)} IMG files")
        
        # Load all IMG files
        loaded_imgs = []
        for i, file_path in enumerate(img_files):
            try:
                # Import IMG core classes
                from methods.img_core_classes import IMGFile
                
                img_file = IMGFile()
                if img_file.load_from_file(file_path):
                    loaded_imgs.append({
                        'img_file': img_file,
                        'file_path': file_path,
                        'name': os.path.basename(file_path)
                    })
                    main_window.log_message(f"✅ Loaded: {os.path.basename(file_path)}")
                else:
                    main_window.log_message(f"⚠️ Failed to load: {os.path.basename(file_path)}")
                    
            except Exception as e:
                main_window.log_message(f"❌ Error loading {os.path.basename(file_path)}: {str(e)}")

        if len(loaded_imgs) < 2:
            main_window.log_message("❌ Need at least 2 valid IMG files to merge")
            return False

        # Combine entries from all IMG files
        combined_entries, conflicts = _combine_img_entries(main_window, loaded_imgs)
        
        if not combined_entries:
            main_window.log_message("❌ No entries found to merge")
            return False

        # Handle conflicts if any
        if conflicts:
            if not _resolve_entry_conflicts(main_window, conflicts):
                main_window.log_message("❌ Entry conflict resolution failed")
                return False

        # Create merged IMG file
        success = create_merged_img(main_window, combined_entries, output_path)
        
        if success:
            main_window.log_message(f"✅ Merged IMG created: {os.path.basename(output_path)}")
            main_window.log_message(f"📊 Total entries: {len(combined_entries)}")
            return True
        else:
            return False

    except Exception as e:
        main_window.log_message(f"❌ Multiple IMG merge failed: {str(e)}")
        return False


def _combine_img_entries(main_window, loaded_imgs: List[Dict[str, Any]]) -> tuple: #vers 1
    """Combine entries from multiple IMG files"""
    try:
        combined_entries = []
        conflicts = []
        seen_names = set()
        
        entry_sources = {}  # Track which IMG each entry came from
        
        for img_data in loaded_imgs:
            img_file = img_data['img_file']
            img_name = img_data['name']
            
            if not hasattr(img_file, 'entries'):
                continue
                
            for entry in img_file.entries:
                entry_name = getattr(entry, 'name', '').lower()
                
                if entry_name in seen_names:
                    # Conflict found
                    conflicts.append({
                        'entry_name': entry_name,
                        'source1': entry_sources[entry_name],
                        'source2': img_name,
                        'entry1': next(e for e in combined_entries if getattr(e, 'name', '').lower() == entry_name),
                        'entry2': entry
                    })
                else:
                    # New entry
                    combined_entries.append(entry)
                    seen_names.add(entry_name)
                    entry_sources[entry_name] = img_name

        main_window.log_message(f"📊 Combined entries: {len(combined_entries)}, Conflicts: {len(conflicts)}")
        return combined_entries, conflicts

    except Exception as e:
        main_window.log_message(f"❌ Failed to combine entries: {str(e)}")
        return [], []


def _resolve_entry_conflicts(main_window, conflicts: List[Dict[str, Any]]) -> bool: #vers 1
    """Resolve entry name conflicts during merge"""
    try:
        if not conflicts:
            return True

        # Show conflict resolution dialog
        conflict_names = [c['entry_name'] for c in conflicts]
        conflict_list = '\n'.join([f"• {name}" for name in conflict_names[:10]])
        if len(conflicts) > 10:
            conflict_list += f"\n... and {len(conflicts) - 10} more"

        msg = QMessageBox(main_window)
        msg.setWindowTitle("Entry Name Conflicts")
        msg.setText(f"Found {len(conflicts)} entry name conflicts:\n\n{conflict_list}\n\n"
                   "How should conflicts be resolved?")
        
        # Add resolution options
        keep_first_btn = msg.addButton("Keep First", QMessageBox.ButtonRole.AcceptRole)
        keep_larger_btn = msg.addButton("Keep Larger", QMessageBox.ButtonRole.AcceptRole)
        rename_btn = msg.addButton("Rename Duplicates", QMessageBox.ButtonRole.AcceptRole)
        cancel_btn = msg.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
        
        msg.setDefaultButton(keep_larger_btn)
        msg.exec()
        
        clicked_button = msg.clickedButton()
        
        if clicked_button == cancel_btn:
            return False
        
        # Apply resolution strategy
        for conflict in conflicts:
            entry1 = conflict['entry1']
            entry2 = conflict['entry2']
            
            if clicked_button == keep_first_btn:
                # Keep first entry (already in combined_entries)
                pass
            elif clicked_button == keep_larger_btn:
                # Keep larger entry
                size1 = getattr(entry1, 'size', 0)
                size2 = getattr(entry2, 'size', 0)
                if size2 > size1:
                    # Replace first entry with second
                    entry1.__dict__.update(entry2.__dict__)
            elif clicked_button == rename_btn:
                # Rename second entry
                original_name = getattr(entry2, 'name', '')
                base_name, ext = os.path.splitext(original_name)
                new_name = f"{base_name}_dup{ext}"
                
                # Make sure new name is unique
                counter = 1
                while any(getattr(e, 'name', '').lower() == new_name.lower() for e in combined_entries):
                    new_name = f"{base_name}_dup{counter}{ext}"
                    counter += 1
                
                entry2.name = new_name
                combined_entries.append(entry2)

        main_window.log_message(f"✅ Resolved {len(conflicts)} entry conflicts")
        return True

    except Exception as e:
        main_window.log_message(f"❌ Conflict resolution failed: {str(e)}")
        return False


def create_merged_img(main_window, entries: List[Any], output_path: str) -> bool: #vers 1
    """Create the merged IMG file"""
    try:
        # Import IMG core classes
        from methods.img_core_classes import IMGFile
        
        # Create new IMG file
        merged_img = IMGFile()
        merged_img.entries = entries
        merged_img.file_path = output_path
        
        # Save the merged IMG
        if hasattr(merged_img, 'save_to_file'):
            success = merged_img.save_to_file(output_path)
        else:
            # Fallback to basic writing
            success = _write_merged_img_file(main_window, entries, output_path)
        
        if success and os.path.exists(output_path):
            # Verify file size
            file_size = os.path.getsize(output_path)
            if hasattr(main_window, 'format_file_size'):
                size_text = main_window.format_file_size(file_size)
            else:
                size_text = f"{file_size:,} bytes"
            
            main_window.log_message(f"📁 Merged file size: {size_text}")
            return True
        else:
            return False

    except Exception as e:
        main_window.log_message(f"❌ Failed to create merged IMG: {str(e)}")
        return False


def _write_merged_img_file(main_window, entries: List[Any], output_path: str) -> bool: #vers 1
    """Write merged IMG file using basic format"""
    try:
        with open(output_path, 'wb') as f:
            # Write IMG header
            f.write(b'VER2')  # Version signature
            f.write(len(entries).to_bytes(4, 'little'))  # Entry count

            # Calculate data start offset
            header_size = 8
            directory_size = len(entries) * 32  # 32 bytes per directory entry
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
                    # Try to read from original file
                    data = b''  # Placeholder
                
                if data:
                    f.write(data)

        return True

    except Exception as e:
        main_window.log_