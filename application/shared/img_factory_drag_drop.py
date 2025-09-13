#this belongs in Tools/IMG_Factory/gui/img_factory_drag_drop.py - Version: 1
# X-Seti - September12 2025 - IMG Factory 1.5 - Drag Drop System

"""
Drag Drop System - File and folder drag-drop functionality
Ported from IMG Editor and adapted for IMG Factory's GUI system
Integrates with existing gui_layout.py and import systems
"""

import os
from typing import List, Optional
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
from PyQt6.QtWidgets import QWidget, QMessageBox

##Methods list -
# setup_drag_drop_system
# enable_drag_drop_for_widget
# handle_drag_enter
# handle_drop_event
# process_dropped_files
# process_img_file_drop
# process_asset_files_drop
# process_folder_drop
# validate_dropped_files
# show_drop_confirmation_dialog
# _get_file_type
# _is_valid_import_file

##Classes -
# DragDropHandler
# DropFileInfo

class DropFileInfo: #vers 1
    """Information about a dropped file"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.file_name = os.path.basename(file_path)
        self.file_ext = os.path.splitext(file_path)[1].lower()
        self.file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
        self.file_type = self._determine_file_type()
    
    def _determine_file_type(self) -> str: #vers 1
        """Determine the type of file"""
        if self.file_ext == '.img':
            return 'img_archive'
        elif self.file_ext in ['.dff', '.txd', '.col']:
            return 'game_asset'
        elif self.file_ext in ['.ide', '.ipl', '.dat']:
            return 'game_data'
        elif self.file_ext in ['.wav', '.mp3']:
            return 'audio'
        else:
            return 'unknown'


class DragDropHandler: #vers 1
    """Handles drag and drop operations for IMG Factory"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.supported_img_files = {'.img'}
        self.supported_asset_files = {'.dff', '.txd', '.col', '.ide', '.ipl', '.dat', '.wav', '.mp3'}
        self.supported_archives = {'.zip', '.rar', '.7z'}
    
    def handle_drag_enter(self, event: QDragEnterEvent) -> bool: #vers 1
        """Handle drag enter event"""
        try:
            if event.mimeData().hasUrls():
                urls = event.mimeData().urls()
                
                # Check if any files are supported
                for url in urls:
                    if url.isLocalFile():
                        file_path = url.toLocalFile()
                        if self._is_supported_file(file_path) or os.path.isdir(file_path):
                            event.acceptProposedAction()
                            return True
            
            event.ignore()
            return False
            
        except Exception as e:
            self.main_window.log_message(f"❌ Drag enter failed: {str(e)}")
            event.ignore()
            return False
    
    def handle_drop_event(self, event: QDropEvent) -> bool: #vers 1
        """Handle drop event"""
        try:
            if not event.mimeData().hasUrls():
                event.ignore()
                return False
            
            # Get dropped file paths
            file_paths = []
            folder_paths = []
            
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    path = url.toLocalFile()
                    if os.path.isfile(path):
                        file_paths.append(path)
                    elif os.path.isdir(path):
                        folder_paths.append(path)
            
            # Process drops
            success = self.process_dropped_items(file_paths, folder_paths)
            
            if success:
                event.acceptProposedAction()
            else:
                event.ignore()
            
            return success
            
        except Exception as e:
            self.main_window.log_message(f"❌ Drop event failed: {str(e)}")
            event.ignore()
            return False
    
    def process_dropped_items(self, file_paths: List[str], folder_paths: List[str]) -> bool: #vers 1
        """Process dropped files and folders"""
        try:
            total_success = True
            
            # Process individual files
            if file_paths:
                if not self.process_dropped_files(file_paths):
                    total_success = False
            
            # Process folders
            for folder_path in folder_paths:
                if not self.process_folder_drop(folder_path):
                    total_success = False
            
            return total_success
            
        except Exception as e:
            self.main_window.log_message(f"❌ Process dropped items failed: {str(e)}")
            return False
    
    def process_dropped_files(self, file_paths: List[str]) -> bool: #vers 1
        """Process dropped files"""
        try:
            # Categorize files
            img_files = []
            asset_files = []
            other_files = []
            
            for file_path in file_paths:
                file_info = DropFileInfo(file_path)
                
                if file_info.file_type == 'img_archive':
                    img_files.append(file_path)
                elif file_info.file_type in ['game_asset', 'game_data', 'audio']:
                    asset_files.append(file_path)
                else:
                    other_files.append(file_path)
            
            success = True
            
            # Handle IMG files (open in new tabs)
            for img_file in img_files:
                if not self.process_img_file_drop(img_file):
                    success = False
            
            # Handle asset files (import to current IMG)
            if asset_files:
                if not self.process_asset_files_drop(asset_files):
                    success = False
            
            # Report unsupported files
            if other_files:
                self.report_unsupported_files(other_files)
            
            return success
            
        except Exception as e:
            self.main_window.log_message(f"❌ Process files failed: {str(e)}")
            return False
    
    def process_img_file_drop(self, img_file_path: str) -> bool: #vers 1
        """Process dropped IMG file - open in new tab"""
        try:
            self.main_window.log_message(f"📂 Opening IMG file: {os.path.basename(img_file_path)}")
            
            # Use tabs system if available
            if hasattr(self.main_window, 'open_img_in_new_tab'):
                return self.main_window.open_img_in_new_tab(img_file_path)
            elif hasattr(self.main_window, 'open_img_file'):
                return self.main_window.open_img_file(img_file_path)
            else:
                self.main_window.log_message("❌ No IMG opening function available")
                return False
                
        except Exception as e:
            self.main_window.log_message(f"❌ IMG file drop failed: {str(e)}")
            return False
    
    def process_asset_files_drop(self, asset_files: List[str]) -> bool: #vers 1
        """Process dropped asset files - import to current IMG"""
        try:
            # Check if there's an active IMG to import to
            current_archive = None
            if hasattr(self.main_window, 'get_current_img_archive'):
                current_archive = self.main_window.get_current_img_archive()
            
            if not current_archive:
                # Ask user what to do
                reply = self.show_no_img_dialog(len(asset_files))
                
                if reply == QMessageBox.StandardButton.Yes:
                    # Create new IMG
                    if hasattr(self.main_window, 'create_new_img'):
                        if not self.main_window.create_new_img():
                            return False
                        current_archive = self.main_window.get_current_img_archive()
                    else:
                        self.main_window.log_message("❌ Cannot create new IMG")
                        return False
                else:
                    return False
            
            # Show import confirmation
            if not self.show_import_confirmation(asset_files):
                return False
            
            # Import files using existing import system
            if hasattr(self.main_window, 'import_files'):
                return self.main_window.import_files(asset_files)
            elif hasattr(main_window, 'import_files_with_core'):
                return self.main_window.import_files_with_core(current_archive, asset_files) > 0
            else:
                self.main_window.log_message("❌ No import function available")
                return False
                
        except Exception as e:
            self.main_window.log_message(f"❌ Asset files drop failed: {str(e)}")
            return False
    
    def process_folder_drop(self, folder_path: str) -> bool: #vers 1
        """Process dropped folder - import all supported files"""
        try:
            self.main_window.log_message(f"📁 Processing folder: {os.path.basename(folder_path)}")
            
            # Scan folder for supported files
            supported_files = []
            img_files = []
            
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_ext = os.path.splitext(file)[1].lower()
                    
                    if file_ext in self.supported_img_files:
                        img_files.append(file_path)
                    elif file_ext in self.supported_asset_files:
                        supported_files.append(file_path)
            
            if not supported_files and not img_files:
                self.main_window.log_message(f"⚠️ No supported files found in folder")
                return False
            
            # Show folder processing dialog
            if not self.show_folder_confirmation(supported_files, img_files, folder_path):
                return False
            
            success = True
            
            # Open IMG files in tabs
            for img_file in img_files:
                if not self.process_img_file_drop(img_file):
                    success = False
            
            # Import asset files
            if supported_files:
                if not self.process_asset_files_drop(supported_files):
                    success = False
            
            return success
            
        except Exception as e:
            self.main_window.log_message(f"❌ Folder drop failed: {str(e)}")
            return False
    
    def show_no_img_dialog(self, file_count: int) -> QMessageBox.StandardButton: #vers 1
        """Show dialog when no IMG is open for import"""
        try:
            reply = QMessageBox.question(
                self.main_window,
                "No IMG File Open",
                f"You're trying to import {file_count} file(s), but no IMG file is open.\n\n"
                "Create a new IMG file for import?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            
            return reply
            
        except Exception as e:
            self.main_window.log_message(f"❌ No IMG dialog failed: {str(e)}")
            return QMessageBox.StandardButton.No
    
    def show_import_confirmation(self, asset_files: List[str]) -> bool: #vers 1
        """Show import confirmation dialog"""
        try:
            file_list = "\n".join([f"• {os.path.basename(f)}" for f in asset_files[:10]])
            if len(asset_files) > 10:
                file_list += f"\n... and {len(asset_files) - 10} more"
            
            reply = QMessageBox.question(
                self.main_window,
                "Import Files",
                f"Import {len(asset_files)} file(s) to current IMG?\n\n{file_list}",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            
            return reply == QMessageBox.StandardButton.Yes
            
        except Exception as e:
            self.main_window.log_message(f"❌ Import confirmation failed: {str(e)}")
            return False
    
    def show_folder_confirmation(self, asset_files: List[str], img_files: List[str], folder_path: str) -> bool: #vers 1
        """Show folder processing confirmation"""
        try:
            message = f"Process folder: {os.path.basename(folder_path)}\n\n"
            
            if img_files:
                message += f"• Open {len(img_files)} IMG file(s) in tabs\n"
            
            if asset_files:
                message += f"• Import {len(asset_files)} asset file(s) to current IMG\n"
            
            message += "\nContinue?"
            
            reply = QMessageBox.question(
                self.main_window,
                "Process Folder",
                message,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            
            return reply == QMessageBox.StandardButton.Yes
            
        except Exception as e:
            self.main_window.log_message(f"❌ Folder confirmation failed: {str(e)}")
            return False
    
    def report_unsupported_files(self, other_files: List[str]): #vers 1
        """Report unsupported files to user"""
        try:
            file_list = "\n".join([f"• {os.path.basename(f)}" for f in other_files[:5]])
            if len(other_files) > 5:
                file_list += f"\n... and {len(other_files) - 5} more"
            
            QMessageBox.information(
                self.main_window,
                "Unsupported Files",
                f"{len(other_files)} file(s) not supported:\n\n{file_list}"
            )
            
        except Exception as e:
            self.main_window.log_message(f"❌ Report unsupported failed: {str(e)}")
    
    def _is_supported_file(self, file_path: str) -> bool: #vers 1
        """Check if file is supported"""
        ext = os.path.splitext(file_path)[1].lower()
        return ext in self.supported_img_files or ext in self.supported_asset_files
    
    def _get_file_category(self, file_path: str) -> str: #vers 1
        """Get file category for processing"""
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext in self.supported_img_files:
            return 'img'
        elif ext in self.supported_asset_files:
            return 'asset'
        else:
            return 'unknown'


def setup_drag_drop_system(main_window) -> bool: #vers 1
    """Setup drag and drop system for IMG Factory"""
    try:
        # Create drag drop handler
        drag_drop_handler = DragDropHandler(main_window)
        main_window.drag_drop_handler = drag_drop_handler
        
        # Enable drag and drop for main window
        main_window.setAcceptDrops(True)
        
        # Override drag/drop event handlers
        original_drag_enter = getattr(main_window, 'dragEnterEvent', None)
        original_drop_event = getattr(main_window, 'dropEvent', None)
        
        def drag_enter_event(event):
            if drag_drop_handler.handle_drag_enter(event):
                return
            if original_drag_enter:
                original_drag_enter(event)
        
        def drop_event(event):
            if drag_drop_handler.handle_drop_event(event):
                return
            if original_drop_event:
                original_drop_event(event)
        
        main_window.dragEnterEvent = drag_enter_event
        main_window.dropEvent = drop_event
        
        # Enable for table widget if available
        if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'table'):
            enable_drag_drop_for_widget(main_window.gui_layout.table, drag_drop_handler)
        
        main_window.log_message("✅ Drag & Drop system initialized")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Drag & Drop setup failed: {str(e)}")
        return False


def enable_drag_drop_for_widget(widget: QWidget, drag_drop_handler: DragDropHandler) -> bool: #vers 1
    """Enable drag and drop for a specific widget"""
    try:
        widget.setAcceptDrops(True)
        
        # Store original handlers
        original_drag_enter = getattr(widget, 'dragEnterEvent', None)
        original_drop_event = getattr(widget, 'dropEvent', None)
        
        def widget_drag_enter_event(event):
            if drag_drop_handler.handle_drag_enter(event):
                return
            if original_drag_enter:
                original_drag_enter(event)
        
        def widget_drop_event(event):
            if drag_drop_handler.handle_drop_event(event):
                return
            if original_drop_event:
                original_drop_event(event)
        
        widget.dragEnterEvent = widget_drag_enter_event
        widget.dropEvent = widget_drop_event
        
        return True
        
    except Exception as e:
        return False


def get_drag_drop_statistics(main_window) -> dict: #vers 1
    """Get drag and drop system statistics"""
    try:
        if not hasattr(main_window, 'drag_drop_handler'):
            return {'enabled': False}
        
        handler = main_window.drag_drop_handler
        
        stats = {
            'enabled': True,
            'supported_img_files': list(handler.supported_img_files),
            'supported_asset_files': list(handler.supported_asset_files),
            'total_supported_types': len(handler.supported_img_files) + len(handler.supported_asset_files)
        }
        
        return stats
        
    except Exception as e:
        return {'enabled': False, 'error': str(e)}