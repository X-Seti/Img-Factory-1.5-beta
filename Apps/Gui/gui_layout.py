#this belongs in Gui/gui_layout.py - Version: 1
# X-Seti - September11 2025 - IMG Factory 1.5 - GUI Layout System

"""
GUI Layout System - Main GUI layout with IMG Editor Tool integration
Handles button creation, theming, and method mapping to Tools/img_editor_tool.py
"""

import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QSplitter, 
                            QPushButton, QTableWidget, QTextEdit, QProgressBar,
                            QFrame, QLabel, QSpacerItem, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

# Import from new structure
from Tools.img_editor_tool import IMGEditorTool
from Shared.theme_system import get_current_theme, is_dark_theme
from Shared.progress_functions import show_progress, hide_progress
from Core.validation_functions import validate_img_structure

##Methods list -
# __init__
# _create_button_with_theme
# _create_main_layout
# _create_method_mappings
# _create_splitter_layout
# _create_table_widget
# _darken_color
# _get_button_theme_template
# _get_short_text
# _is_dark_theme
# _lighten_color
# _log_missing_method
# _safe_log
# _setup_button_panel
# _setup_gui_theme
# _setup_progress_system
# adapt_buttons_to_width
# handle_resize_event
# hide_progress
# integrate_gui_layout
# show_progress

##class GUILayout: -
# __init__
# _create_button_with_theme
# _create_main_layout
# _create_method_mappings
# _create_splitter_layout
# _create_table_widget
# _darken_color
# _get_button_theme_template
# _get_short_text
# _is_dark_theme
# _lighten_color
# _log_missing_method
# _safe_log
# _setup_button_panel
# _setup_gui_theme
# _setup_progress_system
# adapt_buttons_to_width
# handle_resize_event
# hide_progress
# show_progress

class GUILayout(QWidget): #vers 1
    """Main GUI layout system with IMG Editor Tool integration"""
    
    def __init__(self, main_window): #vers 1
        super().__init__()
        self.main_window = main_window
        self.img_editor_tool = None
        self.main_splitter = None
        self.table = None
        self.progress_bar = None
        self.status_label = None
        
        # Button collections
        self.img_buttons = []
        self.entry_buttons = []
        self.options_buttons = []
        
        # Initialize IMG Editor Tool
        self._setup_img_editor_tool()
        
        # Create GUI layout
        self._create_main_layout()
        
        # Setup theming
        self._setup_gui_theme()
        
        # Setup progress system
        self._setup_progress_system()

    def _setup_img_editor_tool(self): #vers 1
        """Initialize IMG Editor Tool integration"""
        try:
            self.img_editor_tool = IMGEditorTool()
            if hasattr(self.main_window, 'log_message'):
                self.main_window.log_message("✅ IMG Editor Tool initialized")
        except Exception as e:
            if hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"❌ IMG Editor Tool failed: {str(e)}")

    def _create_main_layout(self): #vers 1
        """Create main splitter layout"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)
        
        # Create splitter
        self.main_splitter = self._create_splitter_layout()
        main_layout.addWidget(self.main_splitter)
        
        # Create progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumHeight(20)
        main_layout.addWidget(self.progress_bar)

    def _create_splitter_layout(self): #vers 1
        """Create main splitter with table and button panel"""
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(6)
        
        # Left panel - table widget
        self.table = self._create_table_widget()
        splitter.addWidget(self.table)
        
        # Right panel - button panel
        button_panel = self._setup_button_panel()
        splitter.addWidget(button_panel)
        
        # Set initial sizes
        splitter.setSizes([600, 280])
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 0)
        
        return splitter

    def _create_table_widget(self): #vers 1
        """Create main table widget"""
        table = QTableWidget()
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setGridStyle(Qt.PenStyle.SolidLine)
        table.verticalHeader().setVisible(False)
        table.setMinimumWidth(400)
        
        # Set default IMG headers
        headers = ["Index", "Name", "Offset", "Size", "Data Size", "Type", "RW Ver", "Info"]
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        
        return table

    def _setup_button_panel(self): #vers 1
        """Setup right-side button panel"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.StyledPanel)
        panel.setMaximumWidth(300)
        panel.setMinimumWidth(200)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        
        # Get method mappings
        method_mappings = self._create_method_mappings()
        
        # IMG Operations section
        img_group = QLabel("IMG Operations")
        img_group.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(img_group)
        
        img_buttons_data = [
            ("Create", "create_img_file", "create_action"),
            ("Open", "open_img_file", "open_action"),
            ("Reload", "reload_img_file", "reload_action"),
            ("Close", "close_img_file", "close_action"),
            ("Close All", "close_all_img", "close_action"),
            ("Rebuild", "rebuild_img", "build_action"),
            ("Rebuild All", "rebuild_all_img", "build_action"),
            ("Save Entry", "save_img_entry", "save_action"),
            ("Merge", "merge_img", "merge_action"),
            ("Split", "split_img", "merge_action"),
            ("Convert", "convert_img_format", "convert_action")
        ]
        
        for label, method_name, theme_key in img_buttons_data:
            btn = self._create_button_with_theme(label, method_name, method_mappings, theme_key)
            self.img_buttons.append(btn)
            layout.addWidget(btn)
        
        layout.addItem(QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))
        
        # Entry Operations section
        entry_group = QLabel("Entry Operations")
        entry_group.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(entry_group)
        
        entry_buttons_data = [
            ("Import", "import_files", "import_action"),
            ("Import via", "import_files_via", "import_action"),
            ("Refresh", "refresh_table", "reload_action"),
            ("Export", "export_selected", "export_action"),
            ("Export via", "export_selected_via", "export_action"),
            ("Quick Export", "quick_export_selected", "export_action"),
            ("Remove", "remove_selected", "remove_action"),
            ("Remove via", "remove_via_entries", "remove_action"),
            ("Dump", "dump_entries", "export_action")
        ]
        
        for label, method_name, theme_key in entry_buttons_data:
            btn = self._create_button_with_theme(label, method_name, method_mappings, theme_key)
            self.entry_buttons.append(btn)
            layout.addWidget(btn)
        
        layout.addItem(QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))
        
        # Selection & Edit section
        options_group = QLabel("Selection & Edit")
        options_group.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(options_group)
        
        options_buttons_data = [
            ("Select All", "select_all_entries", "open_action"),
            ("Select Inverse", "select_inverse", "open_action"),
            ("Sort Entries", "sort_entries", "open_action"),
            ("Pin Selected", "pin_selected_entries", "open_action"),
            ("Rename", "rename_selected", "convert_action"),
            ("Replace", "replace_selected", "convert_action")
        ]
        
        for label, method_name, theme_key in options_buttons_data:
            btn = self._create_button_with_theme(label, method_name, method_mappings, theme_key)
            self.options_buttons.append(btn)
            layout.addWidget(btn)
        
        layout.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        return panel

    def _create_method_mappings(self): #vers 1
        """Create method mappings using IMG Editor Tool and legacy functions"""
        method_mappings = {}
        
        if self.img_editor_tool:
            adapter = self.img_editor_tool.get_adapter()
            
            # IMG Editor Tool mappings
            method_mappings.update({
                # Core IMG operations - use IMG Editor Tool
                'create_img_file': lambda: adapter.create_img(),
                'open_img_file': lambda: adapter.open_img(),
                'reload_img_file': lambda: adapter.reload_img(),
                'close_img_file': lambda: adapter.close_img(),
                'close_all_img': lambda: adapter.close_img(),
                'rebuild_img': lambda: adapter.rebuild_img(),
                'save_img_entry': lambda: adapter.save_img(),
                'merge_img': lambda: self._log_missing_method('merge_img'),
                'split_img': lambda: self._log_missing_method('split_img'),
                'convert_img_format': lambda: self._log_missing_method('convert_img_format'),
                
                # Import/Export - use IMG Editor Tool
                'import_files': lambda: adapter.import_files(),
                'export_selected': lambda: adapter.export_selected(),
                'quick_export_selected': lambda: adapter.export_selected(),
                'dump_entries': lambda: adapter.export_all(),
                
                # Entry management - use IMG Editor Tool
                'remove_selected': lambda: adapter.delete_selected(),
            })
        
        # Legacy functions from existing structure
        try:
            # Import from Shared (converted from methods/)
            from Shared.refresh_table_functions import refresh_table
            from Shared.import_functions import import_files_via_function, import_via_function
            from Shared.export_functions import export_selected_via, export_via_function
            from Shared.remove_functions import remove_via_entries_function
            
            method_mappings.update({
                'refresh_table': lambda: refresh_table(self.main_window),
                'import_files_via': lambda: import_files_via_function(self.main_window),
                'export_selected_via': lambda: export_selected_via(self.main_window),
                'remove_via_entries': lambda: remove_via_entries_function(self.main_window),
            })
            
        except ImportError as e:
            self._safe_log(f"Some legacy functions not available: {str(e)}")
        
        # Rebuild functions from Core
        try:
            from Core.rebuild_all import rebuild_all_open_tabs, show_batch_rebuild_dialog
            
            method_mappings.update({
                'rebuild_all_img': lambda: show_batch_rebuild_dialog(self.main_window),
            })
            
        except ImportError:
            method_mappings['rebuild_all_img'] = lambda: self._log_missing_method('rebuild_all_img')
        
        # Selection methods (not in IMG Editor Tool)
        method_mappings.update({
            'select_all_entries': lambda: self._select_all_entries(),
            'select_inverse': lambda: self._select_inverse(),
            'sort_entries': lambda: self._sort_entries(),
            'pin_selected_entries': lambda: self._pin_selected_entries(),
            'rename_selected': lambda: self._rename_selected(),
            'replace_selected': lambda: self._replace_selected(),
        })
        
        return method_mappings

    def _create_button_with_theme(self, label, method_name, method_mappings, theme_key): #vers 1
        """Create themed button with method connection"""
        btn = QPushButton(label)
        btn.setMinimumHeight(32)
        btn.setMaximumHeight(36)
        
        # Store text variants for responsive design
        btn.full_text = label
        btn.short_text = self._get_short_text(label)
        
        # Apply theme
        theme_template = self._get_button_theme_template()
        if theme_key in theme_template:
            base_color = theme_template[theme_key]
            hover_color = self._lighten_color(base_color, 1.2)
            pressed_color = self._darken_color(base_color, 0.8)
            
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {base_color};
                    color: {'#FFFFFF' if self._is_dark_theme() else '#000000'};
                    border: 1px solid {'#555555' if self._is_dark_theme() else '#CCCCCC'};
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {hover_color};
                }}
                QPushButton:pressed {{
                    background-color: {pressed_color};
                }}
            """)
        
        # Connect method
        try:
            if method_name in method_mappings:
                btn.clicked.connect(method_mappings[method_name])
                if hasattr(self.main_window, 'log_message'):
                    print(f"✅ Connected '{label}' to method_mappings[{method_name}]")
            else:
                btn.clicked.connect(lambda: self._log_missing_method(method_name))
                if hasattr(self.main_window, 'log_message'):
                    print(f"⚠️ Method '{method_name}' not found in method_mappings for '{label}'")
        except Exception as e:
            if hasattr(self.main_window, 'log_message'):
                print(f"❌ Error connecting button '{label}': {e}")
            btn.clicked.connect(lambda: self._safe_log(f"Button '{label}' connection error"))
        
        return btn

    def _get_button_theme_template(self): #vers 1
        """Get button color templates based on theme"""
        if self._is_dark_theme():
            return {
                'create_action': '#3D5A5A',
                'open_action': '#3D4A5F', 
                'reload_action': '#2D4A3A',
                'close_action': '#5A4A3D',
                'build_action': '#2D4A3A',
                'save_action': '#4A2D4A',
                'merge_action': '#3A2D4A',
                'convert_action': '#4A4A2D',
                'import_action': '#2D4A4F',
                'export_action': '#2D4A3A',
                'remove_action': '#4A2D2D'
            }
        else:
            return {
                'create_action': '#E8F5E8',
                'open_action': '#E8F0FF',
                'reload_action': '#F0F8E8',
                'close_action': '#FFF0E8',
                'build_action': '#E8FFF0',
                'save_action': '#F8E8FF',
                'merge_action': '#FFE8F8',
                'convert_action': '#FFFEE8',
                'import_action': '#E8FFFF',
                'export_action': '#E8FFE8',
                'remove_action': '#FFE8E8'
            }

    def _is_dark_theme(self): #vers 1
        """Check if current theme is dark"""
        try:
            from Shared.theme_system import is_dark_theme
            return is_dark_theme()
        except ImportError:
            return False

    def _lighten_color(self, color, factor): #vers 1
        """Lighten a hex color by factor"""
        try:
            if not color.startswith('#'):
                return color
            
            color = color.lstrip('#')
            r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
            
            r = min(255, int(r + (255 - r) * (factor - 1.0)))
            g = min(255, int(g + (255 - g) * (factor - 1.0)))
            b = min(255, int(b + (255 - b) * (factor - 1.0)))
            
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return color

    def _darken_color(self, color, factor): #vers 1
        """Darken a hex color by factor"""
        try:
            if not color.startswith('#'):
                return color
                
            color = color.lstrip('#')
            r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
            
            r = max(0, int(r * factor))
            g = max(0, int(g * factor))
            b = max(0, int(b * factor))
            
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return color

    def _get_short_text(self, label): #vers 1
        """Get short text for button"""
        short_map = {
            "Create": "New",
            "Open": "Open", 
            "Reload": "Reload",
            "Close": "Close",
            "Close All": "Close A",
            "Rebuild": "Rebld",
            "Rebuild All": "Rebld A",
            "Save Entry": "Save",
            "Merge": "Merge",
            "Split": "Split",
            "Convert": "Conv",
            "Import": "Imp",
            "Import via": "Imp v",
            "Refresh": "Refresh",
            "Export": "Exp",
            "Export via": "Exp v", 
            "Quick Export": "Q Exp",
            "Remove": "Rem",
            "Remove via": "Rem v",
            "Dump": "Dump",
            "Select All": "Sel All",
            "Select Inverse": "Sel Inv",
            "Sort Entries": "Sort",
            "Pin Selected": "Pin",
            "Rename": "Rename",
            "Replace": "Replace",
            "COL Editor": "COL",
            "TXD Editor": "TXD",
            "DFF Editor": "DFF",
            "IFP Editor": "IFP",
            "IDE Editor": "IDE",
            "IPL Editor": "IPL",
            "DAT Editor": "DAT",
            "Zones/Cull": "Zones",
            "Weap Editor": "Weap",
            "Vehi Editor": "Vehi",
            "Peds Editor": "Peds",
            "Radar Map": "Radar",
            "Paths Map": "Paths",
            "Waterpro": "Water",
            "Weather": "Weather",
            "Handling": "Handle",
            "2DFX": "2DFX",
            "Objects": "Objects",
            "SCM Code": "SCM",
            "GXT Font": "GXT",
            "Menu Edit": "Menu"
        }
        return short_map.get(label, label[:6])

    def _setup_gui_theme(self): #vers 1
        """Setup GUI theming"""
        try:
            from Shared.theme_system import apply_theme_to_widget
            apply_theme_to_widget(self)
            apply_theme_to_widget(self.table)
        except ImportError:
            pass

    def _setup_progress_system(self): #vers 1
        """Setup progress bar system"""
        if self.progress_bar:
            self.progress_bar.setVisible(False)

    def show_progress(self, value, text="Working..."): #vers 1
        """Show progress using unified progress system"""
        try:
            from Shared.progress_functions import show_progress as unified_show_progress
            unified_show_progress(self.main_window, value, text)
        except ImportError:
            if self.progress_bar:
                self.progress_bar.setValue(value)
                self.progress_bar.setVisible(value >= 0)

    def hide_progress(self): #vers 1
        """Hide progress bar"""
        try:
            from Shared.progress_functions import hide_progress as unified_hide_progress
            unified_hide_progress(self.main_window)
        except ImportError:
            if self.progress_bar:
                self.progress_bar.setVisible(False)

    def handle_resize_event(self, event): #vers 1
        """Handle window resize to adapt button text"""
        if self.main_splitter:
            sizes = self.main_splitter.sizes()
            if len(sizes) > 1:
                right_panel_width = sizes[1]
                self.adapt_buttons_to_width(right_panel_width)

    def adapt_buttons_to_width(self, width): #vers 1
        """Adapt button text based on available width"""
        all_buttons = []
        all_buttons.extend(self.img_buttons)
        all_buttons.extend(self.entry_buttons)
        all_buttons.extend(self.options_buttons)
        
        for button in all_buttons:
            if hasattr(button, 'full_text'):
                if width > 280:
                    button.setText(button.full_text)
                elif width > 200:
                    text = button.full_text.replace(' via', ' v').replace(' All', ' A')
                    button.setText(text)
                elif width > 150:
                    button.setText(button.short_text)
                else:
                    button.setText("")

    # Selection methods (not in IMG Editor Tool)
    def _select_all_entries(self): #vers 1
        """Select all entries in table"""
        if self.table:
            self.table.selectAll()
            self._safe_log("All entries selected")

    def _select_inverse(self): #vers 1
        """Invert selection in table"""
        if self.table:
            selected_rows = set()
            for item in self.table.selectedItems():
                selected_rows.add(item.row())
            
            self.table.clearSelection()
            for row in range(self.table.rowCount()):
                if row not in selected_rows:
                    self.table.selectRow(row)
            
            self._safe_log("Selection inverted")

    def _sort_entries(self): #vers 1
        """Sort table entries"""
        if self.table:
            self.table.sortItems(1)  # Sort by name column
            self._safe_log("Entries sorted")

    def _pin_selected_entries(self): #vers 1
        """Pin selected entries (placeholder)"""
        self._log_missing_method('pin_selected_entries')

    def _rename_selected(self): #vers 1
        """Rename selected entries (placeholder)"""
        self._log_missing_method('rename_selected')

    def _replace_selected(self): #vers 1
        """Replace selected entries (placeholder)"""
        self._log_missing_method('replace_selected')

    def _log_missing_method(self, method_name): #vers 1
        """Log missing method - unified placeholder"""
        if hasattr(self.main_window, 'log_message'):
            self.main_window.log_message(f"⚠️ Method '{method_name}' not yet implemented")
        else:
            print(f"⚠️ Method '{method_name}' not yet implemented")

    def _safe_log(self, message): #vers 1
        """Safe logging method"""
        if hasattr(self.main_window, 'log_message'):
            self.main_window.log_message(message)
        else:
            print(message)

    def _setup_search_functionality(self): #vers 1
        """Setup search functionality using IMG Editor Tool"""
        try:
            self.search_manager = SearchManager(self.main_window)
            if hasattr(self.main_window, 'log_message'):
                self.main_window.log_message("✅ Search functionality initialized")
        except Exception as e:
            if hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"⚠️ Search functionality failed: {str(e)}")

    def _create_search_panel(self): #vers 1
        """Create search panel widget"""
        try:
            if self.search_manager:
                self.search_widget = SearchWidget(self.main_window)
                # Connect search widget to search manager
                self.search_widget.search_requested.connect(self.search_manager.perform_search)
                return self.search_widget
        except Exception as e:
            self._safe_log(f"Search panel creation failed: {str(e)}")
        
        # Fallback - create simple search widget
        from PyQt6.QtWidgets import QLineEdit, QHBoxLayout, QWidget
        search_panel = QWidget()
        search_layout = QHBoxLayout(search_panel)
        search_layout.setContentsMargins(4, 4, 4, 4)
        
        search_input = QLineEdit()
        search_input.setPlaceholderText("Search entries...")
        search_layout.addWidget(search_input)
        
        return search_panel

    def _create_status_bar(self): #vers 1
        """Create status bar with IMG info"""
        from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel
        
        status_frame = QFrame()
        status_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        status_frame.setMaximumHeight(25)
        
        status_layout = QHBoxLayout(status_frame)
        status_layout.setContentsMargins(8, 2, 8, 2)
        
        self.status_label = QLabel("Ready")
        status_layout.addWidget(self.status_label)
        
        status_layout.addStretch()
        
        # IMG info label (shows entry count, etc.)
        img_info_label = QLabel("")
        status_layout.addWidget(img_info_label)
        
        return status_frame

    def _setup_editor_functions(self): #vers 1
        """Setup editor function integration"""
        try:
            # Connect IMG Editor Tool to main window for editor access
            if self.img_editor_tool and hasattr(self.main_window, 'current_img'):
                self.img_editor_tool.set_main_window_reference(self.main_window)
                self._safe_log("✅ Editor functions integrated")
        except Exception as e:
            self._safe_log(f"⚠️ Editor integration failed: {str(e)}")

    def update_status_bar(self, message): #vers 1
        """Update status bar message"""
        if self.status_label:
            self.status_label.setText(message)

    def update_img_info(self, info_text): #vers 1
        """Update IMG info display"""
        # This would be connected to IMG Editor Tool signals
        self.update_status_bar(info_text)


def integrate_gui_layout(main_window) -> bool: #vers 1
    """Integrate GUI layout system into main window"""
    try:
        # Create GUI layout
        gui_layout = GUILayout(main_window)
        main_window.gui_layout = gui_layout
        
        # Set as central widget
        if hasattr(main_window, 'setCentralWidget'):
            main_window.setCentralWidget(gui_layout)
        
        # Connect resize events
        if hasattr(main_window, 'resizeEvent'):
            original_resize = main_window.resizeEvent
            def new_resize_event(event):
                original_resize(event)
                gui_layout.handle_resize_event(event)
            main_window.resizeEvent = new_resize_event
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("✅ GUI Layout integrated successfully")
        
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ GUI Layout integration failed: {str(e)}")
        return False


# Export functions
__all__ = [
    'GUILayout',
    'integrate_gui_layout'
]