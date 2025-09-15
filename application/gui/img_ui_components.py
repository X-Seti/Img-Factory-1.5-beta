#this belongs in application.shared/img_ui_components.py - Version: 1
# X-Seti - September12 2025 - IMG Factory 1.5 - IMG UI Components

"""
IMG UI Components - UI building blocks for IMG Factory
Enhanced version of ui_components.py with integration for existing populate_img_table.py
Provides file info panels, styling, and table components
"""

import os
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QComboBox, QLineEdit, QPushButton, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

##Methods list -
# create_img_file_info_panel
# update_file_info_display
# create_filter_panel
# apply_modern_styling
# format_file_size_display
# get_rw_version_display
# integrate_with_populate_table
# setup_responsive_ui
# _apply_theme_styling
# _create_modification_status

##Classes -
# IMGFileInfoPanel
# FilterPanel  
# ModificationStatusPanel
# TableStyleManager

class IMGFileInfoPanel(QGroupBox): #vers 1
    """Enhanced file info panel with RW version tracking"""
    
    def __init__(self, parent=None):
        super().__init__("📁 IMG File Information", parent)
        self.current_img_info = None
        self._setup_ui()
        self._apply_styling()
    
    def _setup_ui(self): #vers 1
        """Setup the UI components"""
        layout = QVBoxLayout(self)
        
        # Basic file information
        self.file_path_label = QLabel("Path: No IMG file loaded")
        self.version_label = QLabel("Version: -")
        self.entry_count_label = QLabel("Entries: 0")
        self.total_size_label = QLabel("Total Size: 0 bytes")
        self.modified_label = QLabel("Modified: No")
        
        # RenderWare version summary
        self.rw_files_label = QLabel("RenderWare Files: 0")
        self.rw_versions_label = QLabel("RW Versions: None")
        
        # Modification tracking
        self.new_entries_label = QLabel("New Entries: 0")
        self.deleted_entries_label = QLabel("Deleted Entries: 0")
        self.needs_save_label = QLabel("Needs Save: No")
        
        # Add all labels to layout
        layout.addWidget(self.file_path_label)
        layout.addWidget(self.version_label)
        layout.addWidget(self.entry_count_label)
        layout.addWidget(self.total_size_label)
        layout.addWidget(self.modified_label)
        
        # RW info separator
        rw_separator = QFrame()
        rw_separator.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(rw_separator)
        
        layout.addWidget(self.rw_files_label)
        layout.addWidget(self.rw_versions_label)
        
        # Modification separator
        mod_separator = QFrame()
        mod_separator.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(mod_separator)
        
        layout.addWidget(self.new_entries_label)
        layout.addWidget(self.deleted_entries_label)
        layout.addWidget(self.needs_save_label)
    
    def _apply_styling(self): #vers 1
        """Apply modern styling to panel"""
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QLabel {
                color: white;
                font-size: 12px;
                padding: 2px 8px;
            }
            QFrame[frameShape="4"] {
                color: #555;
                margin: 5px 0px;
            }
        """)
    
    def update_info(self, img_info=None, rw_summary=None, mod_summary=None): #vers 1
        """Update panel with IMG file information"""
        if not img_info:
            self._reset_to_default()
            return
        
        self.current_img_info = img_info
        
        # Update basic file info
        file_path = img_info.get('path', 'Unknown')
        self.file_path_label.setText(f"Path: {os.path.basename(file_path)}")
        self.version_label.setText(f"Version: {img_info.get('version', 'Unknown')}")
        self.entry_count_label.setText(f"Entries: {img_info.get('entry_count', 0):,}")
        
        # Format file size
        total_size = img_info.get('total_size', 0)
        size_text = self._format_file_size(total_size)
        self.total_size_label.setText(f"Total Size: {size_text}")
        
        modified = "Yes" if img_info.get('modified', False) else "No"
        self.modified_label.setText(f"Modified: {modified}")
        
        # Update RenderWare summary
        if rw_summary:
            rw_file_count = rw_summary.get('rw_file_count', 0)
            self.rw_files_label.setText(f"RenderWare Files: {rw_file_count}")
            
            rw_versions = rw_summary.get('versions_found', [])
            if rw_versions:
                versions_text = ', '.join(rw_versions[:3])  # Show first 3 versions
                if len(rw_versions) > 3:
                    versions_text += f" (+{len(rw_versions) - 3} more)"
                self.rw_versions_label.setText(f"RW Versions: {versions_text}")
            else:
                self.rw_versions_label.setText("RW Versions: None detected")
        
        # Update modification summary
        if mod_summary:
            new_entries = mod_summary.get('new_entries', 0)
            deleted_entries = mod_summary.get('deleted_entries', 0)
            needs_save = mod_summary.get('needs_save', False)
            
            self.new_entries_label.setText(f"New Entries: {new_entries}")
            self.deleted_entries_label.setText(f"Deleted Entries: {deleted_entries}")
            self.needs_save_label.setText(f"Needs Save: {'Yes' if needs_save else 'No'}")
    
    def _reset_to_default(self): #vers 1
        """Reset panel to default state"""
        self.file_path_label.setText("Path: No IMG file loaded")
        self.version_label.setText("Version: -")
        self.entry_count_label.setText("Entries: 0")
        self.total_size_label.setText("Total Size: 0 bytes")
        self.modified_label.setText("Modified: No")
        self.rw_files_label.setText("RenderWare Files: 0")
        self.rw_versions_label.setText("RW Versions: None")
        self.new_entries_label.setText("New Entries: 0")
        self.deleted_entries_label.setText("Deleted Entries: 0")
        self.needs_save_label.setText("Needs Save: No")
    
    def _format_file_size(self, size_bytes: int) -> str: #vers 1
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 bytes"
        
        for unit in ['bytes', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                if unit == 'bytes':
                    return f"{int(size_bytes)} {unit}"
                else:
                    return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        
        return f"{size_bytes:.1f} TB"


class FilterPanel(QWidget): #vers 1
    """Enhanced filter panel with type and search filtering"""
    
    filter_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_filter_type = "All Files"
        self.current_search_text = ""
        self._setup_ui()
        self._apply_styling()
    
    def _setup_ui(self): #vers 1
        """Setup filter UI components"""
        layout = QVBoxLayout(self)
        
        # File type filter
        type_group = QGroupBox("File Type Filter")
        type_layout = QHBoxLayout(type_group)
        
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "All Files",
            "Models (DFF)",
            "Textures (TXD)",
            "Collision (COL)",
            "Animations (IFP)",
            "Audio (WAV)",
            "Scripts (SCM)",
            "Data Files (IDE/IPL/DAT)"
        ])
        self.type_combo.currentTextChanged.connect(self._on_filter_changed)
        type_layout.addWidget(self.type_combo)
        
        layout.addWidget(type_group)
        
        # Search filter
        search_group = QGroupBox("Search Filter")
        search_layout = QHBoxLayout(search_group)
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Enter filename to search...")
        self.search_edit.textChanged.connect(self._on_filter_changed)
        search_layout.addWidget(self.search_edit)
        
        # Clear button
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self._clear_filters)
        search_layout.addWidget(clear_btn)
        
        layout.addWidget(search_group)
    
    def _apply_styling(self): #vers 1
        """Apply filter panel styling"""
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #555;
                border-radius: 5px;
                margin-top: 8px;
                padding-top: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 3px 0 3px;
            }
            QComboBox, QLineEdit {
                padding: 4px;
                border: 1px solid #555;
                border-radius: 3px;
                background-color: #2b2b2b;
                color: white;
            }
            QPushButton {
                padding: 4px 8px;
                border: 1px solid #555;
                border-radius: 3px;
                background-color: #3c3c3c;
                color: white;
            }
            QPushButton:hover {
                background-color: #4c4c4c;
            }
        """)
    
    def _on_filter_changed(self): #vers 1
        """Handle filter changes"""
        self.current_filter_type = self.type_combo.currentText()
        self.current_search_text = self.search_edit.text().lower()
        self.filter_changed.emit()
    
    def _clear_filters(self): #vers 1
        """Clear all filters"""
        self.type_combo.setCurrentIndex(0)
        self.search_edit.clear()
    
    def get_filter_criteria(self) -> Dict[str, Any]: #vers 1
        """Get current filter criteria"""
        return {
            'type': self.current_filter_type,
            'search': self.current_search_text
        }
    
    def matches_filter(self, entry_name: str) -> bool: #vers 1
        """Check if entry matches current filter"""
        # Type filter
        if self.current_filter_type != "All Files":
            entry_ext = os.path.splitext(entry_name)[1].lower()
            type_extensions = {
                "Models (DFF)": ['.dff'],
                "Textures (TXD)": ['.txd'],
                "Collision (COL)": ['.col'],
                "Animations (IFP)": ['.ifp'],
                "Audio (WAV)": ['.wav', '.mp3'],
                "Scripts (SCM)": ['.scm'],
                "Data Files (IDE/IPL/DAT)": ['.ide', '.ipl', '.dat']
            }
            
            if entry_ext not in type_extensions.get(self.current_filter_type, []):
                return False
        
        # Search filter
        if self.current_search_text and self.current_search_text not in entry_name.lower():
            return False
        
        return True


class TableStyleManager: #vers 1
    """Manages table styling and appearance"""
    
    @staticmethod
    def apply_modern_table_style(table: QTableWidget): #vers 1
        """Apply modern styling to table widget"""
        table.setStyleSheet("""
            QTableWidget {
                background-color: #2b2b2b;
                alternate-background-color: #353535;
                color: white;
                gridline-color: #555;
                selection-background-color: #0078d4;
                selection-color: white;
                border: 1px solid #555;
            }
            QTableWidget::item {
                padding: 5px;
                border-bottom: 1px solid #555;
            }
            QTableWidget::item:selected {
                background-color: #0078d4;
            }
            QHeaderView::section {
                background-color: #404040;
                color: white;
                padding: 8px;
                border: 1px solid #555;
                font-weight: bold;
            }
        """)
        
        # Configure table behavior
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        table.horizontalHeader().setStretchLastSection(True)


def create_img_file_info_panel(parent=None) -> IMGFileInfoPanel: #vers 1
    """Create standardized IMG file info panel"""
    return IMGFileInfoPanel(parent)


def create_filter_panel(parent=None) -> FilterPanel: #vers 1
    """Create standardized filter panel"""
    return FilterPanel(parent)


def integrate_with_populate_table(main_window, file_info_panel: IMGFileInfoPanel) -> bool: #vers 1
    """Integrate file info panel with existing populate_img_table.py"""
    try:
        # Store reference for populate_img_table to use
        main_window.file_info_panel = file_info_panel
        
        # Hook into table population
        if hasattr(main_window, 'populate_img_table'):
            original_populate = main_window.populate_img_table
            
            def enhanced_populate(img_file):
                # Call original populate function
                result = original_populate(img_file)
                
                # Update file info panel
                if hasattr(img_file, 'file_path'):
                    img_info = {
                        'path': getattr(img_file, 'file_path', ''),
                        'version': getattr(img_file, 'version', 'Unknown'),
                        'entry_count': len(getattr(img_file, 'entries', [])),
                        'total_size': _calculate_total_size(img_file),
                        'modified': getattr(img_file, 'modified', False)
                    }
                    
                    # Get RW summary if available
                    rw_summary = None
                    if hasattr(main_window, 'get_rw_version_summary'):
                        rw_summary = main_window.get_rw_version_summary(img_file)
                    
                    # Get modification summary if available
                    mod_summary = None
                    if hasattr(img_file, 'deleted_entries'):
                        mod_summary = {
                            'new_entries': len([e for e in img_file.entries if getattr(e, 'is_new', False)]),
                            'deleted_entries': len(getattr(img_file, 'deleted_entries', [])),
                            'needs_save': getattr(img_file, 'modified', False)
                        }
                    
                    file_info_panel.update_info(img_info, rw_summary, mod_summary)
                else:
                    file_info_panel.update_info()
                
                return result
            
            # Replace with enhanced version
            main_window.populate_img_table = enhanced_populate
        
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ File info integration failed: {str(e)}")
        return False


def _calculate_total_size(img_file) -> int: #vers 1
    """Calculate total size of IMG file entries"""
    try:
        if not hasattr(img_file, 'entries'):
            return 0
        
        total_size = sum(getattr(entry, 'size', 0) for entry in img_file.entries)
        return total_size
        
    except:
        return 0


def apply_theme_to_components(components: list, theme_colors: dict) -> bool: #vers 1
    """Apply theme colors to UI components"""
    try:
        for component in components:
            if isinstance(component, (IMGFileInfoPanel, FilterPanel)):
                # Apply theme-specific styling
                component.setStyleSheet(component.styleSheet().replace(
                    '#2b2b2b', theme_colors.get('bg_primary', '#2b2b2b')
                ).replace(
                    '#555', theme_colors.get('border', '#555')
                ).replace(
                    'white', theme_colors.get('text_primary', 'white')
                ))
        
        return True
        
    except Exception as e:
        return False


def setup_responsive_ui_components(main_window) -> bool: #vers 1
    """Setup responsive UI components for IMG Factory"""
    try:
        # Create and integrate file info panel
        file_info_panel = create_img_file_info_panel(main_window)
        integrate_with_populate_table(main_window, file_info_panel)
        
        # Create filter panel
        filter_panel = create_filter_panel(main_window)
        
        # Apply table styling
        if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'table'):
            TableStyleManager.apply_modern_table_style(main_window.gui_layout.table)
        
        # Store components in main window
        main_window.file_info_panel = file_info_panel
        main_window.filter_panel = filter_panel
        
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ UI components setup failed: {str(e)}")
        return False