#this belongs in gui/gui_layout.py - Version: 27
# X-Seti - September13 2025 - Img Factory 1.5 - GUI Layout Module with Fixed Function Mappings

import os
import re
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QSplitter,
    QTableWidget, QTableWidgetItem, QTextEdit, QGroupBox, QLabel,
    QPushButton, QComboBox, QLineEdit, QHeaderView, QAbstractItemView,
    QMenuBar, QStatusBar, QProgressBar, QTabWidget, QCheckBox, QSpinBox,
    QMessageBox, QSizePolicy, QButtonGroup, QListWidget, QListWidgetItem,
    QFormLayout, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, QTimer, QSize, pyqtSignal, QPoint
from PyQt6.QtGui import QFont, QAction, QIcon, QShortcut, QKeySequence, QPalette, QTextCursor
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass, field

# Import button layout module
from application.Gui.gui_button_layout import (
    get_button_theme_template, get_img_buttons_data, get_entry_buttons_data,
    get_options_buttons_data, apply_button_theme_styling, get_short_text_mappings,
    get_button_tooltips, is_dark_theme_check
)

def edit_txd_file(main_window): #vers 2
    """Edit selected TXD file with TXD Editor"""
    try:
        entries_table = main_window.gui_layout.table
        selected_items = entries_table.selectedItems()
        if not selected_items:
            main_window.log_message("No TXD file selected")
            return

        row = selected_items[0].row()
        filename_item = entries_table.item(row, 0)
        filename = filename_item.text()

        if not filename.lower().endswith('.txd'):
            main_window.log_message("Selected file is not a TXD file")
            return

        from components.Txd_Editor.txd_editor import TXDEditor
        txd_editor = TXDEditor()
        txd_editor.show()
        main_window.log_message(f"TXD Editor opened for: {filename}")

    except Exception as e:
        main_window.log_message(f"Error opening TXD Editor: {e}")


class IMGFactoryGUILayout:
    """Handles the complete GUI layout for IMG Factory 1.5 with updated function mappings"""

    def __init__(self, main_window): #vers 3
        """Initialize GUI layout with updated function mappings"""
        self.main_window = main_window
        self.table = None
        self.log = None
        self.main_splitter = None
        self.img_buttons = []
        self.entry_buttons = []
        self.options_buttons = []

        # Status bar components
        self.status_bar = None
        self.status_label = None
        self.progress_bar = None
        self.img_info_label = None

        # Tab-related components
        self.main_type_tabs = None
        self.tab_widget = None
        self.left_vertical_splitter = None
        self.status_window = None
        self.info_bar = None
        self.tearoff_button = None

        # Initialize method_mappings FIRST before buttons
        self.method_mappings = self._create_method_mappings()

    def _create_method_mappings(self): #vers 6
        """Create comprehensive method mappings with priority system"""
        method_mappings = {}
        
        # === PRIORITY 1: application/Core/ Functions (Button-Ready with Dialogs) ===
        try:
            # Import all available Core functions
            from application.Core.img_creator import create_new_img, open_file_dialog
            from application.Core.close import close_img_file, close_all_img
            from application.Core.rebuild import rebuild_current_img_native
            from application.Core.rebuild_all import show_batch_rebuild_dialog
            from application.Core.export import export_entries_function
            from application.Core.dump import dump_entries_function
            from application.Core.remove import remove_entries_function
            from application.Core.impotr import import_files_function
            from application.Core.export_via import export_via_function
            from application.Core.rename import rename_entry
            from application.Core.reload import reload_current_file
            from application.Core.convert import convert_img_format
            from application.Core.img_split import split_img
            from application.Core.img_merger import merge_img_function
            from application.Core.quick_export import quick_export_function
            
            # Map Core functions (PRIMARY)
            core_mappings = {
                # File Operations
                'create_new_img': lambda: create_new_img(self.main_window),
                'open_img_file': lambda: open_file_dialog(self.main_window),
                'reload_table': lambda: reload_current_file(self.main_window),
                'close_img_file': lambda: close_img_file(self.main_window),
                'close_all_img': lambda: close_all_img(self.main_window),
                'rebuild_img': lambda: rebuild_current_img_native(self.main_window),
                'rebuild_all_img': lambda: show_batch_rebuild_dialog(self.main_window),
                'convert_img_format': lambda: convert_img_format(self.main_window),
                'merge_img': lambda: merge_img_function(self.main_window),
                'split_img': lambda: split_img(self.main_window),
                
                # Entry Operations  
                'import_files': lambda: import_files_function(self.main_window),
                'export_selected': lambda: export_entries_function(self.main_window),
                'export_selected_via': lambda: export_via_function(self.main_window),
                'quick_export_selected': lambda: quick_export_function(self.main_window),
                'dump_entries': lambda: dump_entries_function(self.main_window),
                'remove_selected': lambda: remove_entries_function(self.main_window),
                'rename_selected': lambda: rename_entry(self.main_window),
            }
            
            method_mappings.update(core_mappings)
            self._safe_log(f"✅ Loaded {len(core_mappings)} application/Core functions")
            
        except ImportError as e:
            self._safe_log(f"⚠️ application/Core functions not available: {str(e)}")
            
            # Fallback to original imports
            try:
                from core.impotr import import_files_function as fallback_import
                from core.export import export_selected_function as fallback_export
                from core.remove import remove_selected_function as fallback_remove
                from core.rebuild import rebuild_current_img_native as fallback_rebuild
                from core.img_creator import create_new_img as fallback_create, open_file_dialog as fallback_open
                from core.close import close_img_file as fallback_close, close_all_img as fallback_close_all
                from core.reload import reload_current_file as fallback_reload
                from core.convert import convert_img_format as fallback_convert
                from core.img_split import split_img as fallback_split
                from core.img_merger import merge_img_function as fallback_merge
                from core.quick_export import quick_export_function as fallback_quick_export
                from core.dump import dump_all_function as fallback_dump
                from core.rename import rename_entry as fallback_rename
                
                fallback_mappings = {
                    'create_new_img': lambda: fallback_create(self.main_window),
                    'open_img_file': lambda: fallback_open(self.main_window),
                    'reload_table': lambda: fallback_reload(self.main_window),
                    'close_img_file': lambda: fallback_close(self.main_window),
                    'close_all_img': lambda: fallback_close_all(self.main_window),
                    'rebuild_img': lambda: fallback_rebuild(self.main_window),
                    'convert_img_format': lambda: fallback_convert(self.main_window),
                    'merge_img': lambda: fallback_merge(self.main_window),
                    'split_img': lambda: fallback_split(self.main_window),
                    'import_files': lambda: fallback_import(self.main_window),
                    'export_selected': lambda: fallback_export(self.main_window),
                    'quick_export_selected': lambda: fallback_quick_export(self.main_window),
                    'dump_entries': lambda: fallback_dump(self.main_window),
                    'remove_selected': lambda: fallback_remove(self.main_window),
                    'rename_selected': lambda: fallback_rename(self.main_window),
                }
                
                method_mappings.update(fallback_mappings)
                self._safe_log(f"✅ Loaded {len(fallback_mappings)} fallback core functions")
                
            except ImportError:
                self._safe_log("❌ Both application/Core and core fallback imports failed")
        
        # === PRIORITY 2: Shared/ Legacy Functions ===
        try:
            from methods.refresh_table_functions import refresh_table
            
            legacy_mappings = {
                'refresh_table': lambda: refresh_table(self.main_window),
            }
            
            # Try additional imports
            try:
                from core.import_via import import_via_function
                legacy_mappings['import_files_via'] = lambda: import_via_function(self.main_window)
            except ImportError:
                try:
                    from Shared.import_functions import import_files_via_function
                    legacy_mappings['import_files_via'] = lambda: import_files_via_function(self.main_window)
                except ImportError:
                    legacy_mappings['import_files_via'] = lambda: self._log_missing_method('import_files_via')
            
            try:
                from core.remove_via import remove_via_function as remove_via_entries_function
                legacy_mappings['remove_via_entries'] = lambda: remove_via_entries_function(self.main_window)
            except ImportError:
                try:
                    from Shared.remove_functions import remove_via_entries_function
                    legacy_mappings['remove_via_entries'] = lambda: remove_via_entries_function(self.main_window)
                except ImportError:
                    legacy_mappings['remove_via_entries'] = lambda: self._log_missing_method('remove_via_entries')
            
            # Add legacy mappings
            for key, func in legacy_mappings.items():
                if key not in method_mappings:
                    method_mappings[key] = func
            
            self._safe_log(f"✅ Added {len(legacy_mappings)} legacy functions")
            
        except ImportError as e:
            self._safe_log(f"⚠️ Legacy functions not available: {str(e)}")
        
        # === PRIORITY 3: Main Window Direct Methods ===
        # These are methods that exist directly on main_window
        main_window_methods = {
            'save_img_entry': lambda: self.main_window.save_img_entry() if hasattr(self.main_window, 'save_img_entry') else self._log_missing_method('save_img_entry'),
            'rebuild_all_img': lambda: self.main_window.rebuild_all_open_tabs() if hasattr(self.main_window, 'rebuild_all_open_tabs') else self._log_missing_method('rebuild_all_img'),
        }
        
        # Add main window methods only if not already defined
        for key, func in main_window_methods.items():
            if key not in method_mappings:
                method_mappings[key] = func
        
        # === PRIORITY 4: GUI-Specific Functions (Table operations) ===
        gui_mappings = {
            'select_all_entries': lambda: self._select_all_entries(),
            'select_inverse': lambda: self._select_inverse(),
            'sort_entries': lambda: self._sort_entries(),
            'pin_selected_entries': lambda: self._pin_selected_entries(),
            'replace_selected': lambda: self._replace_selected(),
        }
        
        method_mappings.update(gui_mappings)
        
        # === PRIORITY 5: Editor Functions ===
        try:
            from gui.gui_context import open_col_editor_dialog
            from components.Ide_Editor.ide_editor import open_ide_editor
            
            editor_mappings = {
                'edit_col_file': lambda: open_col_editor_dialog(self.main_window),
                'edit_txd_file': lambda: edit_txd_file(self.main_window),
                'edit_ide_file': lambda: open_ide_editor(self.main_window),
                'edit_dff_file': lambda: self._log_missing_method('edit_dff_file'),
                'edit_ipf_file': lambda: self._log_missing_method('edit_ipf_file'),
                'edit_ipl_file': lambda: self._log_missing_method('edit_ipl_file'),
                'edit_dat_file': lambda: self._log_missing_method('edit_dat_file'),
                'edit_zones_cull': lambda: self._log_missing_method('edit_zones_cull'),
                'edit_weap_file': lambda: self._log_missing_method('edit_weap_file'),
                'edit_vehi_file': lambda: self._log_missing_method('edit_vehi_file'),
                'edit_peds_file': lambda: self._log_missing_method('edit_peds_file'),
                'edit_radar_map': lambda: self._log_missing_method('edit_radar_map'),
                'edit_paths_map': lambda: self._log_missing_method('edit_paths_map'),
                'edit_waterpro': lambda: self._log_missing_method('edit_waterpro'),
                'edit_weather': lambda: self._log_missing_method('edit_weather'),
                'edit_handling': lambda: self._log_missing_method('edit_handling'),
                'edit_objects': lambda: self._log_missing_method('edit_objects'),
                'editscm': lambda: self._log_missing_method('editscm'),
                'editgxt': lambda: self._log_missing_method('editgxt'),
                'editmenu': lambda: self._log_missing_method('editmenu'),
            }
            
            method_mappings.update(editor_mappings)
            
        except ImportError:
            # Add placeholder editor functions
            editor_functions = ['edit_col_file', 'edit_txd_file', 'edit_ide_file', 'edit_dff_file', 'edit_ipf_file',
                              'edit_ipl_file', 'edit_dat_file', 'edit_zones_cull', 'edit_weap_file', 'edit_vehi_file',
                              'edit_peds_file', 'edit_radar_map', 'edit_paths_map', 'edit_waterpro', 'edit_weather',
                              'edit_handling', 'edit_objects', 'editscm', 'editgxt', 'editmenu']
            
            for func_name in editor_functions:
                if func_name not in method_mappings:
                    method_mappings[func_name] = lambda fn=func_name: self._log_missing_method(fn)
        
        # === PRIORITY 6: Placeholder Functions ===
        placeholder_mappings = {
            'useless_button': lambda: self._safe_log("🎯 useless_button!"),
        }
        
        method_mappings.update(placeholder_mappings)
        
        self._safe_log(f"✅ Total method mappings created: {len(method_mappings)} methods")
        return method_mappings

    # === GUI-Specific Function Implementations ===
    def _select_all_entries(self): #vers 1
        """Select all entries in the table"""
        if self.table:
            self.table.selectAll()
            self._safe_log("Selected all table entries")

    def _select_inverse(self): #vers 1
        """Invert current selection"""
        if self.table:
            # Get current selection
            selected_rows = set(item.row() for item in self.table.selectedItems())
            
            # Clear current selection
            self.table.clearSelection()
            
            # Select inverse
            for row in range(self.table.rowCount()):
                if row not in selected_rows:
                    self.table.selectRow(row)
            
            self._safe_log(f"Inverted selection: {self.table.rowCount() - len(selected_rows)} rows now selected")

    def _sort_entries(self): #vers 1
        """Sort entries in table"""
        if self.table:
            # Sort by first column (filename)
            self.table.sortItems(0)
            self._safe_log("Sorted table entries by filename")

    def _pin_selected_entries(self): #vers 1
        """Pin selected entries (placeholder implementation)"""
        if self.table:
            selected_count = len(self.table.selectedItems()) // max(1, self.table.columnCount())
            self._safe_log(f"Pin function not implemented yet. {selected_count} entries selected.")

    def _replace_selected(self): #vers 1
        """Replace selected entries (placeholder implementation)"""
        if self.table:
            selected_count = len(self.table.selectedItems()) // max(1, self.table.columnCount())
            self._safe_log(f"Replace function not implemented yet. {selected_count} entries selected.")

    def _log_missing_method(self, method_name): #vers 1
        """Log missing method - unified placeholder"""
        if hasattr(self.main_window, 'log_message') and hasattr(self.main_window, 'gui_layout'):
            self.main_window.log_message(f"⚠️ Method '{method_name}' not yet implemented")
        else:
            print(f"⚠️ Method '{method_name}' not yet implemented")

    def _get_button_theme_template(self, theme_name="default"): #vers 3
        """Get button color templates based on theme - Now using external module"""
        return get_button_theme_template(self.main_window, theme_name)

    def _get_img_buttons_data(self): #vers 4
        """Get IMG buttons data with theme colors - Updated to use external module"""
        colors = self._get_button_theme_template()
        img_buttons = get_img_buttons_data()
        
        # Convert to old format with colors
        return [
            (label, method_name.replace('_', ''), "document-" + method_name.replace('_', '-'), 
             colors.get(theme_key, colors['placeholder']), method_name)
            for label, method_name, theme_key in img_buttons
        ]

    def _get_entry_buttons_data(self): #vers 4
        """Get Entry buttons data with theme colors - Updated to use external module"""
        colors = self._get_button_theme_template()
        entry_buttons = get_entry_buttons_data()
        
        # Convert to old format with colors and add the missing buttons from original
        converted_buttons = []
        for label, method_name, theme_key in entry_buttons:
            converted_buttons.append((
                label, method_name.replace('_', ''), "document-" + method_name.replace('_', '-'), 
                colors.get(theme_key, colors['placeholder']), method_name
            ))
        
        # Add the missing buttons that were in the original
        additional_buttons = [
            ("Replace", "replace", "edit-copy", colors['edit_action'], "replace_selected"),
            ("Rename", "rename", "edit-rename", colors['edit_action'], "rename_selected"),
            ("Select All", "select_all", "edit-select-all", colors['select_action'], "select_all_entries"),
            ("Inverse", "sel_inverse", "edit-select", colors['select_action'], "select_inverse"),
            ("Sort via", "sort", "view-sort", colors['select_action'], "sort_entries"),
            ("Pin selected", "pin_selected", "pin", colors['select_action'], "pin_selected_entries"),
        ]
        
        converted_buttons.extend(additional_buttons)
        return converted_buttons

    def _get_options_buttons_data(self): #vers 4
        """Get Options buttons data with theme colors - Keep all original editor buttons"""
        colors = self._get_button_theme_template()
        return [
            ("Col Edit", "col_edit", "col-edit", colors['editor_col'], "edit_col_file"),
            ("Txd Edit", "txd_edit", "txd-edit", colors['editor_txd'], "edit_txd_file"),
            ("Dff Edit", "dff_edit", "dff-edit", colors['editor_dff'], "edit_dff_file"),
            ("Ipf Edit", "ipf_edit", "ipf-edit", colors['editor_data'], "edit_ipf_file"),
            ("IDE Edit", "ide_edit", "ide-edit", colors['editor_data'], "edit_ide_file"),
            ("IPL Edit", "ipl_edit", "ipl-edit", colors['editor_data'], "edit_ipl_file"),
            ("Dat Edit", "dat_edit", "dat-edit", colors['editor_data'], "edit_dat_file"),
            ("Zons Cull Ed", "zones_cull", "zones-cull", colors['editor_data'], "edit_zones_cull"),
            ("Weap Edit", "weap_edit", "weap-edit", colors['editor_vehicle'], "edit_weap_file"),
            ("Vehi Edit", "vehi_edit", "vehi-edit", colors['editor_vehicle'], "edit_vehi_file"),
            ("Peds Edit", "peds_edit", "peds-edit", colors['editor_vehicle'], "edit_peds_file"),
            ("Radar Map", "radar_map", "radar-map", colors['editor_map'], "edit_radar_map"),
            ("Paths Map", "paths_map", "paths-map", colors['editor_map'], "edit_paths_map"),
            ("Waterpro", "timecyc", "timecyc", colors['editor_data'], "edit_waterpro"),
            ("Weather", "timecyc", "timecyc", colors['editor_data'], "edit_weather"),
            ("Handling", "handling", "handling", colors['editor_vehicle'], "edit_handling"),
            ("Objects", "ojs_breakble", "ojs-breakble", colors['editor_data'], "edit_objects"),
            ("SCM code", "scm_code", "scm-code", colors['editor_script'], "editscm"),
            ("GXT font", "gxt_font", "gxt-font", colors['editor_script'], "editgxt"),
            ("Menu Edit", "menu_font", "menu-font", colors['editor_script'], "editmenu"),
        ]

    def _is_dark_theme(self): #vers 3
        """Detect if the application is using a dark theme - Now using external module"""
        return is_dark_theme_check(self.main_window)

    def set_theme_mode(self, theme_name): #vers 2
        """Set the current theme mode and refresh all styling"""
        self.theme_mode = 'dark' if 'dark' in theme_name.lower() else 'light'
        print(f"Theme mode set to: {self.theme_mode}")

        # Force refresh all buttons with new theme colors
        self._refresh_all_buttons()

        # Apply all window themes
        self.apply_all_window_themes()

    def _setup_tearoff_button_for_tabs(self): #vers 1
        """Setup tearoff button in tab widget corner"""
        try:
            # Create tearoff button with square arrow icon
            self.tearoff_button = QPushButton("⧉")  # Square with arrow symbol
            self.tearoff_button.setFixedSize(24, 24)
            self.tearoff_button.setToolTip("Tear off tab widget to separate window")

            # Apply theme-aware styling
            self._apply_tearoff_button_theme()

            # Connect to tearoff handler
            self.tearoff_button.clicked.connect(self._handle_tab_widget_tearoff)

            # Set as corner widget on the right side of tabs
            self.tab_widget.setCornerWidget(self.tearoff_button, Qt.Corner.TopRightCorner)

            self.main_window.log_message("✅ Tearoff button added to tab widget corner")

        except Exception as e:
            self.main_window.log_message(f"❌ Error setting up tearoff button: {str(e)}")

    def _apply_tearoff_button_theme(self): #vers 1
        """Apply theme-aware styling to tearoff button"""
        if not self.tearoff_button:
            return

        is_dark = self._is_dark_theme()

        if is_dark:
            # Dark theme tearoff button
            button_style = """
                QPushButton {
                    border: 1px solid {border_color};
                    border-radius: 1px;
                    background-color: {button_bg};
                    color: {text_color};
                    font-size: 12px;
                    font-weight: bold;
                    padding: 0px;
                    margin: 2px;
                }
                QPushButton:hover {
                    background-color: {hover_bg};
                    border: 1px solid {border_color};
                    color: {text_secondary};
                }
                QPushButton:pressed {
                    background-color: {pressed_bg};
                    border: 1px solid {border_color};
                    color: {text_primary};
                }
            """
        else:
            # Light theme tearoff button
            button_style = """
                QPushButton {
                    border: 1px solid {border_color};
                    border-radius: 1px;
                    background-color: {button_bg};
                    color: {text_color};
                    font-size: 12px;
                    font-weight: bold;
                    padding: 0px;
                    margin: 2px;
                }
                QPushButton:hover {
                    background-color: {hover_bg};
                    border: 1px solid {border_color};
                    color: {text_secondary};
                }
                QPushButton:pressed {
                    background-color: {pressed_bg};
                    border: 1px solid {border_color};
                    color: {text_primary};
                }

            """

        self.tearoff_button.setStyleSheet(button_style)

    # FIXED TEAROFF METHODS

    def _handle_tab_widget_tearoff(self): #vers 2
        """Handle tearoff button click for tab widget - FIXED"""
        try:
            if not self.tab_widget:
                return

            # Check if already torn off
            if hasattr(self.tab_widget, 'is_torn_off') and self.tab_widget.is_torn_off:
                # Dock it back
                self._dock_tab_widget_back()
                return

            # Store original parent info BEFORE removing from layout
            original_parent = self.tab_widget.parent()
            original_layout = original_parent.layout() if original_parent else None

            if not original_parent or not original_layout:
                self.main_window.log_message("❌ Cannot tear off: no parent layout found")
                return

            # Store references on tab widget BEFORE manipulation
            self.tab_widget.original_parent = original_parent
            self.tab_widget.original_layout = original_layout

            # Import tearoff system
            try:
                from gui.tear_off import TearOffPanel
            except ImportError:
                self.main_window.log_message("❌ TearOffPanel not available")
                return

            # Create tearoff panel WITHOUT a layout initially
            panel_id = "file_tabs_panel"
            title = "File Tabs"
            tearoff_panel = TearOffPanel(panel_id, title, self.main_window)

            # Create layout for tearoff panel if it doesn't have one
            if not tearoff_panel.layout():
                tearoff_panel_layout = QVBoxLayout(tearoff_panel)
                tearoff_panel_layout.setContentsMargins(2, 2, 2, 2)
            else:
                tearoff_panel_layout = tearoff_panel.layout()

            # Remove tab widget from current parent layout
            original_layout.removeWidget(self.tab_widget)

            # Add tab widget to tearoff panel
            tearoff_panel_layout.addWidget(self.tab_widget)

            # Store tearoff panel reference
            self.tab_widget.tearoff_panel = tearoff_panel
            self.tab_widget.is_torn_off = True

            # Update button appearance
            self._update_tearoff_button_state(True)

            # Show tearoff panel
            tearoff_panel.show()
            tearoff_panel.raise_()

            # Position near cursor
            from PyQt6.QtGui import QCursor
            cursor_pos = QCursor.pos()
            tearoff_panel.move(cursor_pos.x() - 100, cursor_pos.y() - 50)

            self.main_window.log_message("🔗 Tab widget torn off to separate window")

        except Exception as e:
            self.main_window.log_message(f"❌ Error handling tab widget tearoff: {str(e)}")
            import traceback
            traceback.print_exc()

    def _dock_tab_widget_back(self): #vers 2
        """Dock torn off tab widget back to main window - FIXED"""
        try:
            # Check if actually torn off
            if not hasattr(self.tab_widget, 'is_torn_off') or not self.tab_widget.is_torn_off:
                self.main_window.log_message("⚠️ Tab widget is not torn off")
                return

            # Get stored references with safety checks
            original_parent = getattr(self.tab_widget, 'original_parent', None)
            original_layout = getattr(self.tab_widget, 'original_layout', None)
            tearoff_panel = getattr(self.tab_widget, 'tearoff_panel', None)

            # Validate we have the required references
            if not original_parent:
                self.main_window.log_message("❌ Cannot dock back: no original parent stored")
                return

            if not original_layout:
                self.main_window.log_message("❌ Cannot dock back: no original layout stored")
                return

            # Verify original parent still exists and has layout
            try:
                if original_parent.layout() != original_layout:
                    self.main_window.log_message("⚠️ Original layout changed, using current layout")
                    original_layout = original_parent.layout()
                    if not original_layout:
                        self.main_window.log_message("❌ Original parent no longer has a layout