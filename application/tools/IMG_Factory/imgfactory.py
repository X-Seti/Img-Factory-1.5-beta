#this belongs in application/Tools/IMG_Factory/imgfactory.py - Version: 1
# X-Seti - September12 2025 - IMG Factory 1.5 - Main Application

"""
IMG Factory 1.5 - Complete IMG Editor Application
Enhanced version integrating IMG Editor's proven core with IMG Factory's design
Features: Multi-tab support, drag & drop, advanced progress, modern UI
"""

import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QMenuBar, QMenu, QMessageBox, QWidget, QProgressBar)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QAction, QIcon, QFont, QPalette, QColor, QScreen

# IMG Factory Core imports

from application.styles import ModernDarkTheme
from application.file_explorer import FileExplorer
from application.tools_panel import ToolsPanel
from application.content_area import ContentArea
from application.status_bar import StatusBarWidget
from application.responsive_utils import get_responsive_manager
from application.debug_system import get_debug_logger, LogLevel, LogCategory, debug_function

from Shared.populate_img_table import populate_img_table
from Shared.progress_dialog import integrate_progress_dialog_system

# GUI imports
from Gui.gui_layout import IMGFactoryGUILayout
from Gui.gui_menu import IMGFactoryMenuBar
from Gui.gui_settings import apply_theme_to_app
from Gui.drag_drop_system import setup_drag_drop_system
from Gui.img_tabs_system import setup_img_tabs_system, integrate_tabs_with_existing_functions
from Gui.ui_interaction_handlers import setup_ui_interaction_handlers, integrate_with_existing_handlers
from Gui.img_ui_components import setup_responsive_ui_components, create_img_file_info_panel, create_filter_panel

# Core function imports
from Core.img_core_bridge import integrate_img_editor_core
from Core.impotr import integrate_import_functions
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
# RenderwareModdingSuite


def initialize_debug_system():
    """Initialize debug system for IMG Factory"""
    try:
        print("[INIT] Initializing debug system...")

        # Find application directory
        current_dir = Path(__file__).parent if hasattr(Path, '__file__') else Path.cwd()

        # Check possible application directory locations
        apps_locations = [
            current_dir / 'application',
            current_dir.parent / 'application',
            Path.cwd() / 'application'
        ]

        apps_dir = None
        for location in apps_locations:
            if location.exists() and (location / 'Debug').exists():
                apps_dir = location
                break

        if not apps_dir:
            print("[WARNING] application/Debug directory not found, using fallback debug")
            create_fallback_debug()
            return True

        # Add application to Python path
        apps_str = str(apps_dir)
        if apps_str not in sys.path:
            sys.path.insert(0, apps_str)
            print(f"[INIT] Added {apps_str} to Python path")

        # Import and setup the debug patcher
        debug_dir = apps_dir / 'Debug'
        sys.path.insert(0, str(debug_dir))

        # Try to import the debug system
        try:
            from Debug.import_patcher import patch_debug_imports
            if patch_debug_imports():
                print("[INIT] ✅ Debug system initialized successfully")
                return True
        except ImportError:
            pass

        # Fallback: Create simple debug module
        create_fallback_debug()
        return True

    except Exception as e:
        print(f"[ERROR] Debug initialization failed: {e}")
        create_fallback_debug()
        return False

def create_fallback_debug():
    """Create a simple fallback debug system"""
    print("[INIT] Creating fallback debug system...")

    # Create a simple debug module
    import types

    # Simple debugger class
    class SimpleDebugger:
        def __init__(self):
            self.enabled = True

        def debug(self, msg):
            if self.enabled: print(f"[DEBUG] {msg}")
        def info(self, msg):
            if self.enabled: print(f"[INFO] {msg}")
        def warning(self, msg):
            if self.enabled: print(f"[WARNING] {msg}")
        def error(self, msg):
            if self.enabled: print(f"[ERROR] {msg}")
        def success(self, msg):
            if self.enabled: print(f"[SUCCESS] {msg}")

    # Create debug module
    debug_module = types.ModuleType('debug')

    # Create img_debug_functions submodule
    img_debug_module = types.ModuleType('debug.img_debug_functions')
    img_debug_module.img_debugger = SimpleDebugger()
    img_debug_module.set_col_debug_enabled = lambda x: None
    img_debug_module.is_col_debug_enabled = lambda: False

    # Add to sys.modules
    sys.modules['debug'] = debug_module
    sys.modules['debug.img_debug_functions'] = img_debug_module

    print("[INIT] ✅ Fallback debug system created")

# Initialize debug system immediately
initialize_debug_system()

# Test the debug system
try:
    from debug.img_debug_functions import img_debugger
    img_debugger.info("IMG Factory debug system ready")
except ImportError as e:
    print(f"[ERROR] Debug system test failed: {e}")

print("[INIT] Debug initialization complete")

class RenderwareModdingSuite(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()

        # Initialize debug logger
        self.debug_logger = get_debug_logger()
        self.debug_logger.info(LogCategory.SYSTEM, "Initializing Renderware Modding Suite")

        # Start application setup timer
        setup_timer = self.debug_logger.start_performance_timer("Application Initialization")

        self.setup_ui()
        self.setup_connections()

        # End setup timer
        self.debug_logger.end_performance_timer(setup_timer)

        # Memory monitoring timer
        self.memory_timer = QTimer()
        self.memory_timer.timeout.connect(self.update_memory_usage)
        self.memory_timer.start(5000)  # Update every 5 seconds

        # Monitor screen changes for multi-monitor setups
        if QApplication.instance():
            try:
                app = QApplication.instance()
                if hasattr(app, 'screenAdded'):
                    app.screenAdded.connect(self.handle_screen_change)
                if hasattr(app, 'screenRemoved'):
                    app.screenRemoved.connect(self.handle_screen_change)
                if hasattr(app, 'primaryScreenChanged'):
                    app.primaryScreenChanged.connect(self.handle_screen_change)

                # Monitor primary screen geometry changes
                primary_screen = app.primaryScreen()
                if primary_screen and hasattr(primary_screen, 'geometryChanged'):
                    primary_screen.geometryChanged.connect(self.handle_screen_change)
            except Exception as e:
                self.debug_logger.warning(LogCategory.UI, f"Could not set up screen monitoring: {e}")

        self.debug_logger.info(LogCategory.SYSTEM, "Application initialization completed")


    def setup_ui(self):
        """Setup the user interface with responsive sizing"""
        self.debug_logger.debug(LogCategory.UI, "Setting up main UI")

        rm = get_responsive_manager()

        # Set responsive window size and title
        window_size = rm.get_window_size()
        self.setWindowTitle("Renderware Modding Suite - GTA 3D Era Tool")
        self.setGeometry(100, 100, window_size[0], window_size[1])

        self.debug_logger.info(LogCategory.UI, "Window configured", {
            "size": f"{window_size[0]}x{window_size[1]}",
            "breakpoint": rm.breakpoint
        })

        # Print debug info for development


        # Set application icon
        self.set_window_icon()

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # Get responsive margins
        margins = rm.get_content_margins()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(margins[0], margins[1], margins[2], margins[3])

        # Create horizontal splitter for main content
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Get panel widths
        panel_min, panel_max = rm.get_panel_width()

        # Left panel (File Explorer)
        self.debug_logger.debug(LogCategory.UI, "Creating File Explorer panel")
        self.file_explorer = FileExplorer()
        self.file_explorer.setMaximumWidth(panel_max)
        self.file_explorer.setMinimumWidth(panel_min)

        # Center area (Content)
        self.debug_logger.debug(LogCategory.UI, "Creating Content Area")
        self.content_area = ContentArea()

        # Right panel (Tools)
        self.debug_logger.debug(LogCategory.UI, "Creating Tools panel")
        self.tools_panel = ToolsPanel()
        self.tools_panel.setMaximumWidth(panel_max)
        self.tools_panel.setMinimumWidth(panel_min)

        # Add panels to splitter
        splitter.addWidget(self.file_explorer)
        splitter.addWidget(self.content_area)
        splitter.addWidget(self.tools_panel)

        # Set responsive splitter proportions based on screen size
        if rm.breakpoint == "small":
            # On small screens, give more space to content
            splitter.setSizes([panel_min, window_size[0] - (2 * panel_min), panel_min])
        else:
            # On larger screens, use balanced proportions
            content_width = window_size[0] - (2 * panel_max)
            splitter.setSizes([panel_max, content_width, panel_max])

        # Status bar
        self.status_bar = StatusBarWidget()

        # Add to main layout
        main_layout.addWidget(splitter)
        main_layout.addWidget(self.status_bar)

        # Create menu bar after all components are initialized
        self.create_menu_bar()

    def set_window_icon(self):
        """Set the application window icon"""
        try:
            # Try to find icon in different possible locations
            possible_paths = [
                # When running as executable
                os.path.join(os.path.dirname(sys.executable), "icon.ico"),
                # When running from source
                os.path.join(os.path.dirname(__file__), "..", "icon.ico"),
                # Alternative source location
                os.path.join(os.path.dirname(__file__), "..", "..", "icon.ico"),
                # Current working directory
                "icon.ico"
            ]

            icon_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    icon_path = path
                    break

            if icon_path:
                icon = QIcon(icon_path)
                if not icon.isNull():
                    self.setWindowIcon(icon)
                    self.debug_logger.info(LogCategory.UI, f"Application icon loaded", {"icon_path": icon_path})
                else:
                    self.debug_logger.warning(LogCategory.UI, "Icon file found but couldn't be loaded", {"icon_path": icon_path})
            else:
                self.debug_logger.warning(LogCategory.UI, "Icon file not found in any expected location")

        except Exception as e:
            self.debug_logger.error(LogCategory.UI, f"Error setting window icon: {e}")

    def create_menu_bar(self):
        """Create application menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu('&File')

        open_action = QAction('&Open File...', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.file_explorer.browse_files)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        exit_action = QAction('E&xit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Tools menu
        tools_menu = menubar.addMenu('&Tools')

        batch_action = QAction('&Batch Converter', self)
        batch_action.triggered.connect(lambda: self.tools_panel.toolRequested.emit("batch_converter", {}))
        tools_menu.addAction(batch_action)

        validate_action = QAction('&Validate Files', self)
        validate_action.triggered.connect(lambda: self.tools_panel.toolRequested.emit("file_validator", {}))
        tools_menu.addAction(validate_action)

        # Window menu for tab management
        window_menu = menubar.addMenu('&Window')

        close_tab_action = QAction('&Close Tab', self)
        close_tab_action.setShortcut('Ctrl+W')
        close_tab_action.triggered.connect(self.content_area.close_current_tab)
        window_menu.addAction(close_tab_action)

        close_all_action = QAction('Close &All Tabs', self)
        close_all_action.setShortcut('Ctrl+Shift+W')
        close_all_action.triggered.connect(self.content_area.close_all_tabs_except_welcome)
        window_menu.addAction(close_all_action)

        window_menu.addSeparator()

        next_tab_action = QAction('&Next Tab', self)
        next_tab_action.setShortcut('Ctrl+Tab')
        next_tab_action.triggered.connect(self.switch_to_next_tab)
        window_menu.addAction(next_tab_action)

        prev_tab_action = QAction('&Previous Tab', self)
        prev_tab_action.setShortcut('Ctrl+Shift+Tab')
        prev_tab_action.triggered.connect(self.switch_to_previous_tab)
        window_menu.addAction(prev_tab_action)

        window_menu.addSeparator()

        # UI Scale options
        zoom_in_action = QAction('Zoom &In', self)
        zoom_in_action.setShortcut('Ctrl++')
        zoom_in_action.triggered.connect(self.zoom_in)
        window_menu.addAction(zoom_in_action)

        zoom_out_action = QAction('Zoom &Out', self)
        zoom_out_action.setShortcut('Ctrl+-')
        zoom_out_action.triggered.connect(self.zoom_out)
        window_menu.addAction(zoom_out_action)

        reset_zoom_action = QAction('&Reset Zoom', self)
        reset_zoom_action.setShortcut('Ctrl+0')
        reset_zoom_action.triggered.connect(self.reset_zoom)
        window_menu.addAction(reset_zoom_action)

        # Help menu
        help_menu = menubar.addMenu('&Help')

        about_action = QAction('&About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def setup_connections(self):
        """Setup signal connections between components"""
        # File Explorer signals
        self.file_explorer.fileSelected.connect(self.load_file)
        self.file_explorer.openInTool.connect(self.handle_tool_request)

        # Tools Panel signals
        self.tools_panel.toolRequested.connect(self.handle_tool_request)

    def load_file(self, file_path):
        """Load file in content area"""
        self.debug_logger.log_user_action("Load File", {"file_path": file_path})

        load_timer = self.debug_logger.start_performance_timer(f"Load File: {os.path.basename(file_path)}")

        self.status_bar.set_status(f"Loading {os.path.basename(file_path)}...")
        self.status_bar.set_file_info(file_path)

        try:
            # Load file in content area
            self.content_area.load_file(file_path)
            self.status_bar.show_success(f"Loaded {os.path.basename(file_path)}")

            self.debug_logger.log_file_operation("load", file_path, True, {
                "file_size": os.path.getsize(file_path) if os.path.exists(file_path) else 0
            })

        except Exception as e:
            self.debug_logger.log_exception(LogCategory.FILE_IO, f"Failed to load file: {file_path}", e)
            self.status_bar.show_error(f"Error loading file: {str(e)}")

            # Still try to show file in UI
            self.content_area.load_file(file_path)

        finally:
            self.debug_logger.end_performance_timer(load_timer)

    def handle_tool_request(self, tool_name, params):
        """Handle tool request from tools panel"""
        self.debug_logger.log_user_action("Open Tool", {"tool_name": tool_name, "params": params})

        tool_timer = self.debug_logger.start_performance_timer(f"Open Tool: {tool_name}")

        self.status_bar.set_status(f"Opening {tool_name.replace('_', ' ').title()}...")

        try:
            # Show tool interface
            self.content_area.show_tool_interface(tool_name, params)
            self.status_bar.show_success(f"Opened {tool_name.replace('_', ' ').title()}")

            self.debug_logger.log_tool_operation(tool_name, "opened", params)

        except Exception as e:
            self.debug_logger.log_exception(LogCategory.TOOL, f"Failed to open tool: {tool_name}", e)
            self.status_bar.show_error(f"Error opening tool: {str(e)}")

        finally:
            self.debug_logger.end_performance_timer(tool_timer)

    def switch_to_next_tab(self):
        """Switch to the next tab"""
        current_index = self.content_area.tab_widget.currentIndex()
        tab_count = self.content_area.tab_widget.count()

        if tab_count > 1:  # Only switch if there are multiple tabs
            next_index = (current_index + 1) % tab_count
            self.content_area.tab_widget.setCurrentIndex(next_index)

    def switch_to_previous_tab(self):
        """Switch to the previous tab"""
        current_index = self.content_area.tab_widget.currentIndex()
        tab_count = self.content_area.tab_widget.count()

        if tab_count > 1:  # Only switch if there are multiple tabs
            prev_index = (current_index - 1) % tab_count
            self.content_area.tab_widget.setCurrentIndex(prev_index)

    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About Renderware Modding Suite",
            """<h3>Renderware Modding Suite</h3>
            <p>Professional modding tools for GTA 3D era games</p>
            <p><b>Supported Games:</b><br>
            • Grand Theft Auto III<br>
            • Grand Theft Auto: Vice City<br>
            • Grand Theft Auto: San Andreas</p>

            <p><b>Supported Formats:</b><br>
            • DFF (3D Models)<br>
            • TXD (Textures)<br>
            • COL (Collision)<br>
            • IFP (Animations)<br>
            • IDE (Definitions)<br>
            • IPL (Placements)</p>

            <p><b>Version:</b> 1.0<br>
            <b>Frontend:</b> PyQt6</p>"""
        )

    def update_memory_usage(self):
        """Update memory usage display"""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024

            # Log memory usage to debug system
            self.debug_logger.log_memory_usage("Main Application", memory_mb)

            # Update status bar with memory usage - pass the float value directly
            if hasattr(self, 'status_bar'):
                self.status_bar.set_memory_usage(memory_mb)

        except ImportError:
            # psutil not available, skip memory monitoring
            pass
        except Exception as e:
            self.debug_logger.error(LogCategory.MEMORY, f"Error updating memory usage: {e}")

    def handle_screen_change(self, screen=None):
        """Handle screen changes (resolution, DPI, etc.)"""
        self.debug_logger.info(LogCategory.UI, "Screen configuration changed, refreshing UI scaling")

        try:
            # Refresh responsive manager with new screen info
            from application.responsive_utils import refresh_responsive_manager
            refresh_responsive_manager()

            # Update UI scaling
            self.refresh_ui_scaling()

            self.status_bar.set_status("Screen configuration updated", temporary=True)
        except Exception as e:
            self.debug_logger.error(LogCategory.UI, f"Error handling screen change: {e}")

    def closeEvent(self, event):
        """Handle application close event to ensure proper cleanup"""
        try:
            self.debug_logger.info(LogCategory.SYSTEM, "Application shutting down - cleaning up resources")

            # Clean up content area (which includes all tool tabs)
            if hasattr(self, 'content_area'):
                self.content_area.cleanup_all_tools()

            # Stop memory monitoring timer
            if hasattr(self, 'memory_timer'):
                self.memory_timer.stop()

            self.debug_logger.info(LogCategory.SYSTEM, "Application cleanup completed")

        except Exception as e:
            self.debug_logger.log_exception(LogCategory.SYSTEM, "Error during application cleanup", e)

        # Accept the close event
        event.accept()

    def aboutToQuit(self):
        """Handle application quit event"""
        try:
            self.debug_logger.info(LogCategory.SYSTEM, "Application about to quit - final cleanup...")

            # Force cleanup of all resources
            if hasattr(self, 'content_area'):
                self.content_area.cleanup_all_tools()

            self.debug_logger.info(LogCategory.SYSTEM, "Final cleanup completed")

        except Exception as e:
            self.debug_logger.error(LogCategory.SYSTEM, f"Error during final cleanup: {e}")

    def __del__(self):
        """Destructor to ensure cleanup when the application is destroyed"""
        try:
            # Using logger may not always be safe during interpreter shutdown, but attempt it
            if hasattr(self, 'debug_logger'):
                self.debug_logger.info(LogCategory.SYSTEM, "Main application destructor called - cleaning up...")

            # Force cleanup of all resources
            if hasattr(self, 'content_area'):
                self.content_area.cleanup_all_tools()

            if hasattr(self, 'debug_logger'):
                self.debug_logger.info(LogCategory.SYSTEM, "Main application cleanup completed")

        except Exception as e:
            if hasattr(self, 'debug_logger'):
                self.debug_logger.error(LogCategory.SYSTEM, f"Error in main application destructor: {e}")

    def zoom_in(self):
        """Increase UI scale"""
        rm = get_responsive_manager()
        rm.scale_factor = min(2.0, rm.scale_factor * 1.1)
        self.refresh_ui_scaling()
        self.status_bar.show_success(f"Zoom increased to {rm.scale_factor:.1f}x")

    def zoom_out(self):
        """Decrease UI scale"""
        rm = get_responsive_manager()
        rm.scale_factor = max(0.5, rm.scale_factor * 0.9)
        self.refresh_ui_scaling()
        self.status_bar.show_success(f"Zoom decreased to {rm.scale_factor:.1f}x")

    def reset_zoom(self):
        """Reset UI scale to default"""
        rm = get_responsive_manager()
        rm.scale_factor = rm._calculate_scale_factor()  # Reset to calculated default
        self.refresh_ui_scaling()
        self.status_bar.show_success(f"Zoom reset to {rm.scale_factor:.1f}x")

    def refresh_ui_scaling(self):
        """Refresh the UI with new scaling"""
        try:
            # Reapply the stylesheet with new scaling
            theme = ModernDarkTheme()
            QApplication.instance().setStyleSheet(theme.get_main_stylesheet())

            # Reapply dark palette to ensure theme consistency
            theme.apply_dark_palette(QApplication.instance())

            # Update font
            rm = get_responsive_manager()
            font_config = rm.get_font_config()
            new_font = QFont("Fira Code", font_config['body']['size'])
            QApplication.instance().setFont(new_font)

            self.debug_logger.info(LogCategory.UI, "UI refreshed", {"scale_factor": f"{rm.scale_factor:.2f}"})
        except Exception as e:
            self.debug_logger.error(LogCategory.UI, f"Error refreshing UI scaling: {e}")


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
            
            # Integrate the progress system
            integrate_progress_dialog_system(self)

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


def main(): #vers 2
    """Main application entry point"""
    # Initialize debug logger early
    debug_logger = get_debug_logger()
    debug_logger.info(LogCategory.SYSTEM, "Starting Renderware Modding Suite")

    # Set critical Qt attributes before creating QApplication to force dark theme
    os.environ['QT_FONT_DPI'] = '96'  # Force consistent DPI
    os.environ['QT_SCALE_FACTOR'] = '1'  # Prevent auto-scaling issues

    # Force dark theme independent of system theme
    os.environ['QT_QPA_PLATFORM_THEME'] = ''  # Disable system theme integration
    os.environ['QT_STYLE_OVERRIDE'] = 'Fusion'  # Use Fusion as base style
    os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '0'  # Disable auto-scaling

    debug_logger.debug(LogCategory.SYSTEM, "Qt environment variables configured")

    # Additional environment variables to prevent system theme interference
    os.environ.pop('QT_QPA_PLATFORMTHEME', None)  # Remove any existing platform theme
    os.environ.pop('QT_QUICK_CONTROLS_STYLE', None)  # Remove quick controls style
    os.environ.pop('QT_QUICK_CONTROLS_MATERIAL_THEME', None)  # Remove material theme

    # CRITICAL: Enable high DPI support BEFORE creating QApplication
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    # Note: In PyQt6, high DPI scaling is enabled by default

    app = QApplication(sys.argv)
    debug_logger.debug(LogCategory.SYSTEM, "QApplication created")

    # Set application properties
    app.setApplicationName("Renderware Modding Suite")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("GTA Modding Community")
    debug_logger.info(LogCategory.SYSTEM, "Application properties set")

    # Set application icon globally
    try:
        # Try to find icon in different possible locations
        possible_paths = [
            os.path.join(os.path.dirname(sys.executable), "icon.ico") if getattr(sys, 'frozen', False) else None,
            os.path.join(os.path.dirname(__file__), "..", "icon.ico"),
            "icon.ico"
        ]

        for path in possible_paths:
            if path and os.path.exists(path):
                app_icon = QIcon(path)
                if not app_icon.isNull():
                    app.setWindowIcon(app_icon)
                    debug_logger.info(LogCategory.UI, "Global application icon set", {"icon_path": path})
                    break
    except Exception as e:
        debug_logger.error(LogCategory.UI, f"Error setting global application icon: {e}")

    # Apply modern dark theme
    theme = ModernDarkTheme()
    app.setStyleSheet(theme.get_main_stylesheet())

    # Force dark palette to override any system theme interference
    theme.apply_dark_palette(app)
    debug_logger.info(LogCategory.UI, "Dark theme applied successfully")

    # Set responsive font with fallbacks
    try:
        rm = get_responsive_manager()
        font_config = rm.get_font_config()

        font_families = ["Fira Code", "Consolas", "Courier New", "monospace"]
        for font_family in font_families:
            professional_font = QFont(font_family, font_config['body']['size'])
            if professional_font.exactMatch():
                app.setFont(professional_font)
                debug_logger.info(LogCategory.UI, "Font set", {"font_family": font_family})
                break
        else:
            professional_font = QFont("monospace", font_config['body']['size'])
            app.setFont(professional_font)
            debug_logger.warning(LogCategory.UI, "Using system default monospace font")

    except Exception as e:
        debug_logger.error(LogCategory.UI, f"Error setting font: {e}")

    # Create and show main window
    window = RenderwareModdingSuite()
    window.show()

    # Start event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    sys.exit(main())
