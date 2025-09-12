#this belongs in Apps/Gui/img_tabs_system.py - Version: 1
# X-Seti - September12 2025 - IMG Factory 1.5 - IMG Tabs Manager

"""
IMG Tabs Manager - Multi-tab IMG file management system
Handles opening multiple IMG files in tabs, switching between them, and maintaining state
Integrates with existing gui_layout.py and core bridge system
"""

import os
from typing import Optional, Dict, Any, List
from PyQt6.QtWidgets import QTabWidget, QWidget, QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal

##Methods list -
# setup_img_tabs_system
# open_img_in_new_tab
# close_img_tab
# switch_to_tab
# get_current_img_archive
# get_tab_archive
# update_tab_title
# handle_tab_close_request
# save_tab_state
# restore_tab_state
# _create_tab_widget
# _setup_tab_signals

##Classes -
# IMGTabsManager
# IMGTabWidget

class IMGTabWidget(QWidget): #vers 1
    """Custom tab widget to hold IMG archive and state"""
    
    def __init__(self, archive_adapter, file_path):
        super().__init__()
        self.img_file = archive_adapter  # For compatibility with existing code
        self.archive_adapter = archive_adapter
        self.file_path = file_path
        self.is_modified = False
        
        # Pin/Lock state (for compatibility with pin system)
        self._pinned_entries = getattr(archive_adapter, '_pinned_entries', set())
        self._locked_entries = getattr(archive_adapter, '_locked_entries', set())
        self._pin_options = getattr(archive_adapter, '_pin_options', {})


class IMGTabsManager: #vers 1
    """Manages multiple IMG file tabs"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.tab_widget = None
        self.active_tabs = {}  # tab_index -> IMGTabWidget
        self.tab_counter = 0
        
        self.setup_tab_system()
    
    def setup_tab_system(self): #vers 1
        """Initialize the tab system"""
        try:
            # Create tab widget if it doesn't exist
            if not hasattr(self.main_window, 'tab_widget'):
                self._create_tab_widget()
            else:
                self.tab_widget = self.main_window.tab_widget
            
            # Setup tab signals
            self._setup_tab_signals()
            
            return True
            
        except Exception as e:
            self.main_window.log_message(f"❌ Tab system setup failed: {e}")
            return False
    
    def _create_tab_widget(self): #vers 1
        """Create the main tab widget"""
        try:
            self.tab_widget = QTabWidget()
            self.tab_widget.setTabsClosable(True)
            self.tab_widget.setMovable(True)
            
            # Store in main window for access by other systems
            self.main_window.tab_widget = self.tab_widget
            
            # Add to main window layout if gui_layout exists
            if hasattr(self.main_window, 'gui_layout'):
                # This should integrate with existing gui_layout.py
                pass
            
            return True
            
        except Exception as e:
            self.main_window.log_message(f"❌ Tab widget creation failed: {e}")
            return False
    
    def _setup_tab_signals(self): #vers 1
        """Setup tab widget signals"""
        try:
            self.tab_widget.currentChanged.connect(self.on_tab_changed)
            self.tab_widget.tabCloseRequested.connect(self.on_tab_close_requested)
            
            return True
            
        except Exception as e:
            self.main_window.log_message(f"❌ Tab signals setup failed: {e}")
            return False
    
    def on_tab_changed(self, index): #vers 1
        """Handle tab change"""
        try:
            if index >= 0 and index in self.active_tabs:
                tab_widget = self.active_tabs[index]
                
                # Update current archive reference
                self.main_window.current_img_archive = tab_widget.archive_adapter
                
                # Refresh table with new tab's data
                if hasattr(self.main_window, 'populate_img_table'):
                    self.main_window.populate_img_table(tab_widget.archive_adapter)
                
                # Update window title
                file_name = os.path.basename(tab_widget.file_path)
                self.main_window.setWindowTitle(f"IMG Factory 1.5 - {file_name}")
                
                # Update info bar
                if hasattr(self.main_window, 'update_info_bar'):
                    entry_count = len(tab_widget.archive_adapter.entries)
                    self.main_window.update_info_bar(f"Entries: {entry_count}")
                
                self.main_window.log_message(f"📂 Switched to: {file_name}")
            
        except Exception as e:
            self.main_window.log_message(f"❌ Tab change failed: {e}")
    
    def on_tab_close_requested(self, index): #vers 1
        """Handle tab close request"""
        try:
            if index >= 0 and index in self.active_tabs:
                tab_widget = self.active_tabs[index]
                
                # Check for unsaved changes
                if self.has_unsaved_changes(tab_widget):
                    result = self.show_save_dialog(tab_widget)
                    if result == QMessageBox.StandardButton.Cancel:
                        return  # Don't close
                    elif result == QMessageBox.StandardButton.Save:
                        if not self.save_tab(tab_widget):
                            return  # Don't close if save failed
                
                # Close the tab
                self.close_tab(index)
                
        except Exception as e:
            self.main_window.log_message(f"❌ Tab close failed: {e}")
    
    def has_unsaved_changes(self, tab_widget) -> bool: #vers 1
        """Check if tab has unsaved changes"""
        try:
            return getattr(tab_widget.archive_adapter, 'modified', False) or tab_widget.is_modified
        except:
            return False
    
    def show_save_dialog(self, tab_widget) -> QMessageBox.StandardButton: #vers 1
        """Show save confirmation dialog"""
        try:
            file_name = os.path.basename(tab_widget.file_path)
            
            reply = QMessageBox.question(
                self.main_window,
                "Unsaved Changes",
                f"'{file_name}' has unsaved changes.\n\nSave before closing?",
                QMessageBox.StandardButton.Save | 
                QMessageBox.StandardButton.Discard | 
                QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Save
            )
            
            return reply
            
        except Exception as e:
            self.main_window.log_message(f"❌ Save dialog failed: {e}")
            return QMessageBox.StandardButton.Cancel
    
    def save_tab(self, tab_widget) -> bool: #vers 1
        """Save tab's IMG file"""
        try:
            if hasattr(self.main_window, 'save_img_with_core'):
                return self.main_window.save_img_with_core(tab_widget.archive_adapter)
            elif hasattr(tab_widget.archive_adapter, 'save_to_file'):
                return tab_widget.archive_adapter.save_to_file()
            else:
                return False
                
        except Exception as e:
            self.main_window.log_message(f"❌ Tab save failed: {e}")
            return False


def open_img_in_new_tab(main_window, file_path: str) -> bool: #vers 1
    """Open IMG file in new tab"""
    try:
        if not hasattr(main_window, 'tabs_manager'):
            setup_img_tabs_system(main_window)
        
        # Check if file already open
        for tab_widget in main_window.tabs_manager.active_tabs.values():
            if tab_widget.file_path == file_path:
                # Switch to existing tab
                for index, widget in main_window.tabs_manager.active_tabs.items():
                    if widget == tab_widget:
                        main_window.tab_widget.setCurrentIndex(index)
                        main_window.log_message(f"📂 Switched to existing tab: {os.path.basename(file_path)}")
                        return True
        
        # Load IMG file using core bridge
        archive_adapter = None
        if hasattr(main_window, 'open_img_with_core'):
            archive_adapter = main_window.open_img_with_core(file_path)
        
        if not archive_adapter:
            # Fallback to IMG Factory's existing system
            if hasattr(main_window, 'load_img_file'):
                from methods.img_core_classes import IMGFile
                fallback_img = IMGFile()
                if fallback_img.load_from_file(file_path):
                    archive_adapter = fallback_img
        
        if not archive_adapter:
            main_window.log_message(f"❌ Failed to load IMG: {os.path.basename(file_path)}")
            return False
        
        # Create tab widget
        tab_widget = IMGTabWidget(archive_adapter, file_path)
        
        # Add tab
        tab_title = os.path.basename(file_path)
        tab_index = main_window.tab_widget.addTab(tab_widget, tab_title)
        
        # Store in manager
        main_window.tabs_manager.active_tabs[tab_index] = tab_widget
        main_window.tabs_manager.tab_counter += 1
        
        # Switch to new tab
        main_window.tab_widget.setCurrentIndex(tab_index)
        
        main_window.log_message(f"✅ Opened in new tab: {tab_title}")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Open in tab failed: {str(e)}")
        return False


def close_img_tab(main_window, tab_index: int = None) -> bool: #vers 1
    """Close specific IMG tab or current tab"""
    try:
        if not hasattr(main_window, 'tabs_manager'):
            return False
        
        if tab_index is None:
            tab_index = main_window.tab_widget.currentIndex()
        
        if tab_index < 0 or tab_index not in main_window.tabs_manager.active_tabs:
            return False
        
        # Remove from manager
        tab_widget = main_window.tabs_manager.active_tabs.pop(tab_index, None)
        
        # Remove tab from widget
        main_window.tab_widget.removeTab(tab_index)
        
        # Update remaining tab indices
        new_active_tabs = {}
        for i in range(main_window.tab_widget.count()):
            widget = main_window.tab_widget.widget(i)
            # Find the corresponding tab_widget
            for old_index, old_widget in main_window.tabs_manager.active_tabs.items():
                if main_window.tab_widget.widget(i) == old_widget:
                    new_active_tabs[i] = old_widget
                    break
        
        main_window.tabs_manager.active_tabs = new_active_tabs
        
        # Clear table if no tabs remain
        if main_window.tab_widget.count() == 0:
            if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'table'):
                main_window.gui_layout.table.setRowCount(0)
            main_window.setWindowTitle("IMG Factory 1.5")
        
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Tab close failed: {str(e)}")
        return False


def get_current_img_archive(main_window): #vers 1
    """Get currently active IMG archive"""
    try:
        if not hasattr(main_window, 'tab_widget'):
            return None
        
        current_index = main_window.tab_widget.currentIndex()
        if current_index >= 0:
            tab_widget = main_window.tab_widget.widget(current_index)
            if hasattr(tab_widget, 'archive_adapter'):
                return tab_widget.archive_adapter
            elif hasattr(tab_widget, 'img_file'):
                return tab_widget.img_file
        
        return None
        
    except Exception as e:
        main_window.log_message(f"❌ Get current archive failed: {str(e)}")
        return None


def switch_to_tab(main_window, tab_index: int) -> bool: #vers 1
    """Switch to specific tab"""
    try:
        if not hasattr(main_window, 'tab_widget'):
            return False
        
        if 0 <= tab_index < main_window.tab_widget.count():
            main_window.tab_widget.setCurrentIndex(tab_index)
            return True
        
        return False
        
    except Exception as e:
        main_window.log_message(f"❌ Tab switch failed: {str(e)}")
        return False


def update_tab_title(main_window, tab_index: int, title: str) -> bool: #vers 1
    """Update tab title"""
    try:
        if not hasattr(main_window, 'tab_widget'):
            return False
        
        if 0 <= tab_index < main_window.tab_widget.count():
            main_window.tab_widget.setTabText(tab_index, title)
            return True
        
        return False
        
    except Exception as e:
        main_window.log_message(f"❌ Tab title update failed: {str(e)}")
        return False


def setup_img_tabs_system(main_window) -> bool: #vers 1
    """Initialize the IMG tabs system"""
    try:
        # Create tabs manager
        tabs_manager = IMGTabsManager(main_window)
        main_window.tabs_manager = tabs_manager
        
        # Add tab functions to main window
        main_window.open_img_in_new_tab = lambda file_path: open_img_in_new_tab(main_window, file_path)
        main_window.close_img_tab = lambda tab_index=None: close_img_tab(main_window, tab_index)
        main_window.get_current_img_archive = lambda: get_current_img_archive(main_window)
        main_window.switch_to_tab = lambda tab_index: switch_to_tab(main_window, tab_index)
        main_window.update_tab_title = lambda tab_index, title: update_tab_title(main_window, tab_index, title)
        
        main_window.log_message("✅ IMG tabs system initialized")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Tabs system setup failed: {str(e)}")
        return False


def get_all_open_img_files(main_window) -> List[str]: #vers 1
    """Get list of all open IMG file paths"""
    try:
        if not hasattr(main_window, 'tabs_manager'):
            return []
        
        file_paths = []
        for tab_widget in main_window.tabs_manager.active_tabs.values():
            if hasattr(tab_widget, 'file_path'):
                file_paths.append(tab_widget.file_path)
        
        return file_paths
        
    except Exception as e:
        main_window.log_message(f"❌ Get open files failed: {str(e)}")
        return []


def close_all_img_tabs(main_window) -> bool: #vers 1
    """Close all open IMG tabs"""
    try:
        if not hasattr(main_window, 'tab_widget'):
            return True
        
        # Get count before closing (count changes as we close)
        tab_count = main_window.tab_widget.count()
        closed_count = 0
        
        # Close from last to first to avoid index issues
        for i in range(tab_count - 1, -1, -1):
            if close_img_tab(main_window, i):
                closed_count += 1
        
        main_window.log_message(f"✅ Closed {closed_count} IMG tabs")
        return closed_count == tab_count
        
    except Exception as e:
        main_window.log_message(f"❌ Close all tabs failed: {str(e)}")
        return False


def save_all_img_tabs(main_window) -> bool: #vers 1
    """Save all modified IMG tabs"""
    try:
        if not hasattr(main_window, 'tabs_manager'):
            return True
        
        saved_count = 0
        failed_count = 0
        
        for tab_widget in main_window.tabs_manager.active_tabs.values():
            if main_window.tabs_manager.has_unsaved_changes(tab_widget):
                if main_window.tabs_manager.save_tab(tab_widget):
                    saved_count += 1
                else:
                    failed_count += 1
        
        if saved_count > 0:
            main_window.log_message(f"✅ Saved {saved_count} IMG files")
        
        if failed_count > 0:
            main_window.log_message(f"❌ Failed to save {failed_count} IMG files")
        
        return failed_count == 0
        
    except Exception as e:
        main_window.log_message(f"❌ Save all tabs failed: {str(e)}")
        return False


def get_tab_statistics(main_window) -> Dict[str, Any]: #vers 1
    """Get statistics about open tabs"""
    try:
        if not hasattr(main_window, 'tabs_manager'):
            return {'total_tabs': 0}
        
        stats = {
            'total_tabs': len(main_window.tabs_manager.active_tabs),
            'modified_tabs': 0,
            'total_entries': 0,
            'tab_files': []
        }
        
        for tab_widget in main_window.tabs_manager.active_tabs.values():
            # Count modified tabs
            if main_window.tabs_manager.has_unsaved_changes(tab_widget):
                stats['modified_tabs'] += 1
            
            # Count total entries
            if hasattr(tab_widget.archive_adapter, 'entries'):
                stats['total_entries'] += len(tab_widget.archive_adapter.entries)
            
            # Store file info
            stats['tab_files'].append({
                'path': tab_widget.file_path,
                'name': os.path.basename(tab_widget.file_path),
                'modified': main_window.tabs_manager.has_unsaved_changes(tab_widget),
                'entries': len(getattr(tab_widget.archive_adapter, 'entries', []))
            })
        
        return stats
        
    except Exception as e:
        main_window.log_message(f"❌ Tab statistics failed: {str(e)}")
        return {'total_tabs': 0, 'error': str(e)}


def integrate_tabs_with_existing_functions(main_window) -> bool: #vers 1
    """Integrate tabs system with existing IMG Factory functions"""
    try:
        # Override existing single-file functions to work with tabs
        
        # Override open_img_file to use tabs
        original_open_img = getattr(main_window, 'open_img_file', None)
        def open_img_file_with_tabs(file_path=None):
            if not file_path:
                if original_open_img:
                    file_path = original_open_img()  # Get file path from dialog
                    if not file_path:
                        return False
                else:
                    return False
            
            return open_img_in_new_tab(main_window, file_path)
        
        main_window.open_img_file = lambda file_path=None: open_img_file_with_tabs(file_path)
        
        # Override close functions to work with tabs
        original_close_img = getattr(main_window, 'close_img_file', None)
        main_window.close_img_file = lambda: close_img_tab(main_window)
        main_window.close_all_img = lambda: close_all_img_tabs(main_window)
        
        # Add new tab-aware functions
        main_window.get_all_open_img_files = lambda: get_all_open_img_files(main_window)
        main_window.save_all_img_tabs = lambda: save_all_img_tabs(main_window)
        main_window.close_all_img_tabs = lambda: close_all_img_tabs(main_window)
        main_window.get_tab_statistics = lambda: get_tab_statistics(main_window)
        
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Tabs integration failed: {str(e)}")
        return False


def handle_tab_context_menu(main_window, tab_index: int, position) -> bool: #vers 1
    """Handle right-click context menu on tabs"""
    try:
        from PyQt6.QtWidgets import QMenu
        
        if tab_index < 0 or not hasattr(main_window, 'tabs_manager'):
            return False
        
        if tab_index not in main_window.tabs_manager.active_tabs:
            return False
        
        tab_widget = main_window.tabs_manager.active_tabs[tab_index]
        
        # Create context menu
        menu = QMenu(main_window)
        
        # Add menu actions
        close_action = menu.addAction("🗙 Close Tab")
        close_others_action = menu.addAction("🗙 Close Other Tabs")
        close_all_action = menu.addAction("🗙 Close All Tabs")
        menu.addSeparator()
        
        save_action = menu.addAction("💾 Save")
        save_as_action = menu.addAction("💾 Save As...")
        menu.addSeparator()
        
        properties_action = menu.addAction("📄 Properties")
        
        # Show menu and handle selection
        action = menu.exec(position)
        
        if action == close_action:
            close_img_tab(main_window, tab_index)
        elif action == close_others_action:
            # Close all tabs except this one
            for i in range(main_window.tab_widget.count() - 1, -1, -1):
                if i != tab_index:
                    close_img_tab(main_window, i)
        elif action == close_all_action:
            close_all_img_tabs(main_window)
        elif action == save_action:
            main_window.tabs_manager.save_tab(tab_widget)
        elif action == save_as_action:
            # Implement save as functionality
            pass
        elif action == properties_action:
            show_tab_properties(main_window, tab_widget)
        
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Tab context menu failed: {str(e)}")
        return False


def show_tab_properties(main_window, tab_widget) -> bool: #vers 1
    """Show properties dialog for tab"""
    try:
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
        
        dialog = QDialog(main_window)
        dialog.setWindowTitle(f"Properties - {os.path.basename(tab_widget.file_path)}")
        dialog.resize(400, 300)
        
        layout = QVBoxLayout(dialog)
        
        # File info
        layout.addWidget(QLabel(f"File: {tab_widget.file_path}"))
        layout.addWidget(QLabel(f"Size: {os.path.getsize(tab_widget.file_path):,} bytes"))
        layout.addWidget(QLabel(f"Entries: {len(tab_widget.archive_adapter.entries)}"))
        layout.addWidget(QLabel(f"Modified: {'Yes' if main_window.tabs_manager.has_unsaved_changes(tab_widget) else 'No'}"))
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.exec()
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Tab properties failed: {str(e)}")
        return False
