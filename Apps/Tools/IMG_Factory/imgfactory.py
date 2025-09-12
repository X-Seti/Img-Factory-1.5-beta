#this belongs in Apps/Tools/IMG_Factory/imgfactory.py - Version: 1
# X-Seti - September12 2025 - IMG Factory 1.5 - Main Application

"""
IMG Factory 1.5 - Complete IMG Editor Application
Enhanced version integrating IMG Editor's proven core with IMG Factory's design
Features: Multi-tab support, drag & drop, advanced progress, modern UI
"""

import sys
import os
from pathlib import Path

# Add Apps directory to Python path
apps_dir = Path(__file__).parent.parent.parent
if str(apps_dir) not in sys.path:
    sys.path.insert(0, str(apps_dir))

# PyQt6 imports
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QSplitter
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon

# IMG Factory Core imports
from Shared.img_ui_components import setup_responsive_ui_components, create_img_file_info_panel, create_filter_panel
from Shared.enhanced_progress import setup_progress_system, integrate_with_existing_functions as integrate_progress
from Shared.ui_interaction_handlers import setup_ui_interaction_handlers, integrate_with_existing_handlers
from Shared.populate_img_table import populate_img_table
from Shared.progress_functions import setup_progress_system as setup_legacy_progress

# GUI imports
from Gui.gui_layout import IMGFactoryGUILayout
from Gui.gui_menu import IMGFactoryMenuBar
from Gui.gui_settings import apply_theme_to_app
from Gui.drag_drop_system import setup_drag_drop_system
from Gui.img_tabs_system import setup_img_tabs_system, integrate_tabs_with_existing_functions

# Core function imports
from Core.img_core_bridge import integrate_img_editor_core
from Core.import import integrate_import_functions
from Core.export import integrate_export_functions
from Core.remove import integrate_remove_functions
from Core.close import integrate_close_functions
from Core.save_entry import integrate_save_entry_function
from Core.reload import integrate_reload_functions
from Core.build import integrate_build_functions
from Core.build_all import integrate_build_all_functions
from Core.replace import integrate_replace_functions
from Core.merge import integrate_merge_functions
from Core.split_via import integrate_split_functions
from Core.convert import integrate_convert_functions
from Core.sort_entries import integrate_sort_functions
from Core.pin import integrate_pin_functions

# Utility imports
from utils.app_settings_system import IMGFactorySettings

##Methods list -
# __init__
# setup_application_core
# setup_gui_system
# setup_core_integrations
# setup_advanced_features
# initialize_img_factory
# setup_theme_system
# create_main_layout
# setup_menu_system
# setup_status_system
# _create_ui
# _restore_settings
# _save_settings_on_close

##Classes -
# IMGFactoryApplication

class IMGFactoryApplication(QMainWindow): #vers 1
    """Main IMG Factory application with full IMG Editor integration"""
    
    # Signals for application events
    img_loaded = pyqtSignal(object)
    img_closed = pyqtSignal()
    entries_updated = pyqtSignal(list)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Application properties
        self.setWindowTitle("IMG Factory 1.5")
        self.setMinimumSize(1000, 700)
        self.resize(1400, 900)
        
        # Initialize core systems
        self.app_settings = None
        self.gui_layout = None
        self.progress_manager = None
        self.tabs_manager = None
        self.core_bridge = None
        
        # State tracking
        self.current_img_archive = None
        self.last_save_directory = os.path.expanduser("~/Desktop")
        self.last_open_directory = os.path.expanduser("~/Desktop")
        
        # Initialize application
        self.initialize_img_factory()
    
    def initialize_img_factory(self) -> bool: #vers 1
        """Initialize IMG Factory with full integration"""
        try:
            self.log_message("🚀 Starting IMG Factory 1.5...")
            
            # Phase 1: Core application setup
            if not self.setup_application_core():
                return False
            
            # Phase 2: GUI system setup
            if not self.setup_gui_system():
                return False
            
            # Phase 3: Core integrations
            if not self.setup_core_integrations():
                return False
            
            # Phase 4: Advanced features
            if not self.setup_advanced_features():
                return False
            
            # Phase 5: Final initialization
            self._restore_settings()
            self.log_message("✅ IMG Factory 1.5 initialization complete!")
            
            return True
            
        except Exception as e:
            print(f"❌ IMG Factory initialization failed: {str(e)}")
            return False
    
    def setup_application_core(self) -> bool: #vers 1
        """Setup core application systems"""
        try:
            # Settings system
            self.app_settings = IMGFactorySettings()
            
            # Logging system
            self.log_messages = []
            
            return True
            
        except Exception as e:
            print(f"❌ Core setup failed: {str(e)}")
            return False
    
    def setup_gui_system(self) -> bool: #vers 1
        """Setup GUI system and layout"""
        try:
            # Create main GUI layout
            self.gui_layout = IMGFactoryGUILayout(self)
            
            # Create menu system
            self.setup_menu_system()
            
            # Create main UI
            self._create_ui()
            
            # Setup theme system
            self.setup_theme_system()
            
            # Setup responsive UI components
            setup_responsive_ui_components(self)
            
            return True
            
        except Exception as e:
            self.log_message(f"❌ GUI setup failed: {str(e)}")
            return False
    
    def setup_core_integrations(self) -> bool: #vers 1
        """Setup core IMG Factory integrations"""
        try:
            # IMG Editor core bridge
            integrate_img_editor_core(self)
            
            # Multi-tab system
            setup_img_tabs_system(self)
            integrate_tabs_with_existing_functions(self)
            
            # Progress system
            setup_progress_system(self)
            integrate_progress(self)
            
            # UI interaction handlers
            setup_ui_interaction_handlers(self)
            integrate_with_existing_handlers(self)
            
            # Core functions
            integrate_import_functions(self)
            integrate_export_functions(self)
            integrate_remove_functions(self)
            integrate_close_functions(self)
            integrate_save_entry_function(self)
            integrate_reload_functions(self)
            integrate_build_functions(self)
            integrate_build_all_functions(self)
            
            return True
            
        except Exception as e:
            self.log_message(f"❌ Core integrations failed: {str(e)}")
            return False
    
    def setup_advanced_features(self) -> bool: #vers 1
        """Setup advanced features"""
        try:
            # Advanced core functions
            integrate_replace_functions(self)
            integrate_merge_functions(self)
            integrate_split_functions(self)
            integrate_convert_functions(self)
            integrate_sort_functions(self)
            integrate_pin_functions(self)
            
            # Drag & drop system
            setup_drag_drop_system(self)
            
            return True
            
        except Exception as e:
            self.log_message(f"❌ Advanced features setup failed: {str(e)}")
            return False
    
    def _create_ui(self) -> bool: #vers 1
        """Create the main user interface"""
        try:
            # Create central widget
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            # Main layout
            main_layout = QVBoxLayout(central_widget)
            main_layout.setContentsMargins(5, 5, 5, 5)
            main_layout.setSpacing(5)
            
            # Create splitter for resizable panels
            main_splitter = QSplitter(Qt.Orientation.Horizontal)
            main_layout.addWidget(main_splitter)
            
            # Left panel - File info and filters
            left_panel = self._create_left_panel()
            main_splitter.addWidget(left_panel)
            
            # Center panel - Main content area
            center_panel = self._create_center_panel()
            main_splitter.addWidget(center_panel)
            
            # Set splitter proportions
            main_splitter.setStretchFactor(0, 25)  # Left panel 25%
            main_splitter.setStretchFactor(1, 75)  # Center panel 75%
            
            # Add embedded progress panel
            if hasattr(self, 'embedded_progress_panel'):
                main_layout.addWidget(self.embedded_progress_panel)
            
            # Status bar
            self.setup_status_system()
            
            return True
            
        except Exception as e:
            self.log_message(f"❌ UI creation failed: {str(e)}")
            return False
    
    def _create_left_panel(self) -> QWidget: #vers 1
        """Create left panel with file info and filters"""
        left_panel = QWidget()
        left_panel.setFixedWidth(300)
        left_layout = QVBoxLayout(left_panel)
        
        # File info panel
        if hasattr(self, 'file_info_panel'):
            left_layout.addWidget(self.file_info_panel)
        
        # Filter panel
        if hasattr(self, 'filter_panel'):
            left_layout.addWidget(self.filter_panel)
        
        # Button panel from gui_layout
        if hasattr(self.gui_layout, 'create_button_panel'):
            button_panel = self.gui_layout.create_button_panel()
            left_layout.addWidget(button_panel)
        
        left_layout.addStretch()
        return left_panel
    
    def _create_center_panel(self) -> QWidget: #vers 1
        """Create center panel with tabs and table"""
        center_panel = QWidget()
        center_layout = QVBoxLayout(center_panel)
        center_layout.setContentsMargins(0, 0, 0, 0)
        
        # Tab widget for multiple IMG files
        if hasattr(self, 'tab_widget'):
            center_layout.addWidget(self.tab_widget)
        
        # Main table (from gui_layout)
        if hasattr(self.gui_layout, 'table'):
            center_layout.addWidget(self.gui_layout.table)
        
        return center_panel
    
    def setup_menu_system(self) -> bool: #vers 1
        """Setup menu bar system"""
        try:
            self.menu_bar_system = IMGFactoryMenuBar(self)
            
            # Menu callbacks
            callbacks = {
                "about": self.show_about,
                "open_img": self.handle_open_img_file,
                "new_img": self.handle_create_new_img,
                "close_img": self.handle_close_current_img,
                "exit": self.close,
                "settings": self.show_settings,
                "theme_settings": self.show_theme_settings
            }
            
            self.menu_bar_system.set_callbacks(callbacks)
            
            return True
            
        except Exception as e:
            self.log_message(f"❌ Menu system setup failed: {str(e)}")
            return False
    
    def setup_theme_system(self) -> bool: #vers 1
        """Setup theme system"""
        try:
            if hasattr(self.app_settings, 'get_current_theme'):
                current_theme = self.app_settings.get_current_theme()
                apply_theme_to_app(QApplication.instance(), current_theme)
            
            return True
            
        except Exception as e:
            self.log_message(f"❌ Theme system setup failed: {str(e)}")
            return False
    
    def setup_status_system(self) -> bool: #vers 1
        """Setup status bar system"""
        try:
            status_bar = self.statusBar()
            status_bar.showMessage("IMG Factory 1.5 ready")
            
            # Store reference for updates
            self.status_bar = status_bar
            
            return True
            
        except Exception as e:
            self.log_message(f"❌ Status system setup failed: {str(e)}")
            return False
    
    def log_message(self, message: str): #vers 1
        """Log message to console and internal log"""
        print(message)
        
        # Store in internal log
        if hasattr(self, 'log_messages'):
            self.log_messages.append(message)
            # Keep only last 1000 messages
            if len(self.log_messages) > 1000:
                self.log_messages = self.log_messages[-1000:]
        
        # Update status bar
        if hasattr(self, 'status_bar'):
            # Extract clean message for status bar
            clean_message = message.replace('✅', '').replace('❌', '').replace('⚠️', '').strip()
            self.status_bar.showMessage(clean_message, 3000)
    
    def show_about(self): #vers 1
        """Show about dialog"""
        from PyQt6.QtWidgets import QMessageBox
        
        QMessageBox.about(
            self,
            "About IMG Factory 1.5",
            """
            <h3>IMG Factory 1.5</h3>
            <p>Advanced IMG Archive Editor</p>
            <p>Features:</p>
            <ul>
                <li>Multi-tab IMG file support</li>
                <li>Drag & drop import/export</li>
                <li>Advanced file operations</li>
                <li>Modern UI with theming</li>
                <li>RenderWare version tracking</li>
                <li>File locking and pinning</li>
            </ul>
            <p><b>X-Seti - September 2025</b></p>
            """
        )
    
    def show_settings(self): #vers 1
        """Show settings dialog"""
        try:
            if hasattr(self, 'gui_settings'):
                self.gui_settings.show_settings_dialog()
            else:
                self.log_message("⚠️ Settings dialog not available")
        except Exception as e:
            self.log_message(f"❌ Settings dialog failed: {str(e)}")
    
    def show_theme_settings(self): #vers 1
        """Show theme settings dialog"""
        try:
            if hasattr(self, 'gui_settings'):
                self.gui_settings.show_theme_dialog()
            else:
                self.log_message("⚠️ Theme settings not available")
        except Exception as e:
            self.log_message(f"❌ Theme settings failed: {str(e)}")
    
    def get_selected_entries(self) -> list: #vers 1
        """Get currently selected table entries"""
        try:
            selected_entries = []
            
            if hasattr(self, 'gui_layout') and hasattr(self.gui_layout, 'table'):
                table = self.gui_layout.table
                selected_rows = set()
                
                for item in table.selectedItems():
                    selected_rows.add(item.row())
                
                # Get current IMG archive
                current_archive = self.get_current_img_archive()
                if current_archive and hasattr(current_archive, 'entries'):
                    for row in selected_rows:
                        if row < len(current_archive.entries):
                            selected_entries.append(current_archive.entries[row])
            
            return selected_entries
            
        except Exception as e:
            self.log_message(f"❌ Get selected entries failed: {str(e)}")
            return []
    
    def update_selection_status(self, selected_count: int): #vers 1
        """Update status bar with selection info"""
        try:
            if selected_count == 0:
                self.status_bar.showMessage("No entries selected")
            elif selected_count == 1:
                self.status_bar.showMessage("1 entry selected")
            else:
                self.status_bar.showMessage(f"{selected_count} entries selected")
                
        except Exception as e:
            self.log_message(f"❌ Selection status update failed: {str(e)}")
    
    def get_rw_version_summary(self, img_file) -> Optional[dict]: #vers 1
        """Get RenderWare version summary for IMG file"""
        try:
            if not hasattr(img_file, 'entries'):
                return None
            
            rw_files = 0
            versions_found = set()
            
            for entry in img_file.entries:
                entry_name = getattr(entry, 'name', '').lower()
                
                # Check if it's a RenderWare file
                if entry_name.endswith(('.dff', '.txd', '.col')):
                    rw_files += 1
                    
                    # Try to get RW version if available
                    if hasattr(entry, 'rw_version'):
                        versions_found.add(entry.rw_version)
            
            return {
                'rw_file_count': rw_files,
                'versions_found': list(versions_found)
            }
            
        except Exception as e:
            self.log_message(f"❌ RW version summary failed: {str(e)}")
            return None
    
    def _restore_settings(self): #vers 1
        """Restore application settings"""
        try:
            if self.app_settings:
                # Restore window geometry
                geometry = self.app_settings.get_setting('window_geometry')
                if geometry:
                    self.restoreGeometry(geometry)
                
                # Restore last directories
                self.last_open_directory = self.app_settings.get_setting(
                    'last_open_directory', os.path.expanduser("~/Desktop")
                )
                self.last_save_directory = self.app_settings.get_setting(
                    'last_save_directory', os.path.expanduser("~/Desktop")
                )
                
                self.log_message("⚙️ Settings restored")
            
        except Exception as e:
            self.log_message(f"⚠️ Settings restore failed: {str(e)}")
    
    def _save_settings_on_close(self): #vers 1
        """Save application settings on close"""
        try:
            if self.app_settings:
                # Save window geometry
                self.app_settings.set_setting('window_geometry', self.saveGeometry())
                
                # Save last directories
                self.app_settings.set_setting('last_open_directory', self.last_open_directory)
                self.app_settings.set_setting('last_save_directory', self.last_save_directory)
                
                # Save settings
                self.app_settings.save_settings()
                
                self.log_message("⚙️ Settings saved")
            
        except Exception as e:
            self.log_message(f"⚠️ Settings save failed: {str(e)}")
    
    def closeEvent(self, event): #vers 1
        """Handle application close event"""
        try:
            # Check for unsaved changes in tabs
            if hasattr(self, 'tabs_manager'):
                stats = self.get_tab_statistics()
                if stats.get('modified_tabs', 0) > 0:
                    from PyQt6.QtWidgets import QMessageBox
                    
                    reply = QMessageBox.question(
                        self,
                        "Unsaved Changes",
                        f"There are {stats['modified_tabs']} unsaved IMG file(s).\n\n"
                        "Save all changes before closing?",
                        QMessageBox.StandardButton.Save | 
                        QMessageBox.StandardButton.Discard | 
                        QMessageBox.StandardButton.Cancel,
                        QMessageBox.StandardButton.Save
                    )
                    
                    if reply == QMessageBox.StandardButton.Cancel:
                        event.ignore()
                        return
                    elif reply == QMessageBox.StandardButton.Save:
                        if hasattr(self, 'save_all_img_tabs'):
                            if not self.save_all_img_tabs():
                                event.ignore()
                                return
            
            # Save settings
            self._save_settings_on_close()
            
            # Cleanup resources
            if hasattr(self, 'core_bridge') and self.core_bridge:
                if hasattr(self.core_bridge, 'cleanup'):
                    self.core_bridge.cleanup()
            
            self.log_message("👋 IMG Factory closing...")
            event.accept()
            
        except Exception as e:
            self.log_message(f"❌ Close event failed: {str(e)}")
            event.accept()


def create_img_factory_app() -> QApplication: #vers 1
    """Create IMG Factory application"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("IMG Factory")
    app.setApplicationVersion("1.5")
    app.setOrganizationName("X-Seti")
    
    # Set application icon if available
    icon_path = Path(__file__).parent / "icon.ico"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    
    return app


def main(): #vers 1
    """Main application entry point"""
    try:
        # Create application
        app = create_img_factory_app()
        
        # Create main window
        main_window = IMGFactoryApplication()
        main_window.show()
        
        # Run application
        return app.exec()
        
    except Exception as e:
        print(f"❌ Application startup failed: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())