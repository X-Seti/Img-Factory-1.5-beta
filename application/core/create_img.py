#this belongs in Core/create_img.py - Version: 1
# X-Seti - September11 2025 - IMG Factory 1.5 - Core Create IMG Functions

"""
Core Create IMG Functions - New IMG file creation with templates and validation
Handles creating empty IMG files, template-based creation, and format selection
"""

import os
from typing import Optional, List, Dict, Any
from PyQt6.QtWidgets import QMessageBox, QFileDialog, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QCheckBox, QSpinBox

# Import from new structure
from shared.progress_functions import show_progress, update_progress, hide_progress
from shared.populate_img_table import populate_img_table_enhanced

##Methods list -
# create_new_img
# create_img_with_template
# show_create_img_dialog
# validate_new_img_path
# get_img_templates
# _create_empty_img_file
# _create_img_from_template
# _update_ui_for_new_img
# integrate_create_img_functions

##Classes -
# CreateIMGDialog

class CreateIMGDialog(QDialog): #vers 1
    """Dialog for creating new IMG files with options"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New IMG File")
        self.setMinimumWidth(500)
        self.img_path = ""
        self.img_version = "V2"
        self.img_template = "empty"
        self.setup_ui()
    
    def setup_ui(self): #vers 1
        """Setup dialog UI"""
        layout = QVBoxLayout(self)
        
        # File path section
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("Save Location:"))
        
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Select location for new IMG file...")
        path_layout.addWidget(self.path_input)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_location)
        path_layout.addWidget(browse_btn)
        
        layout.addLayout(path_layout)
        
        # IMG version section
        version_layout = QHBoxLayout()
        version_layout.addWidget(QLabel("IMG Version:"))
        
        self.version_combo = QComboBox()
        self.version_combo.addItems(["V1 (Classic)", "V2 (Compressed)"])
        self.version_combo.setCurrentText("V2 (Compressed)")
        self.version_combo.currentTextChanged.connect(self.on_version_changed)
        version_layout.addWidget(self.version_combo)
        
        layout.addLayout(version_layout)
        
        # Template section
        template_layout = QHBoxLayout()
        template_layout.addWidget(QLabel("Template:"))
        
        self.template_combo = QComboBox()
        templates = get_img_templates()
        for template_id, template_info in templates.items():
            self.template_combo.addItem(template_info['name'], template_id)
        self.template_combo.currentTextChanged.connect(self.on_template_changed)
        template_layout.addWidget(self.template_combo)
        
        layout.addLayout(template_layout)
        
        # Template description
        self.template_desc = QLabel("Empty IMG file with no entries")
        self.template_desc.setWordWrap(True)
        self.template_desc.setStyleSheet("color: #666; font-style: italic; padding: 5px;")
        layout.addWidget(self.template_desc)
        
        # Advanced options (initially hidden)
        self.advanced_group = QVBoxLayout()
        
        # Reserved entries
        reserved_layout = QHBoxLayout()
        self.reserved_check = QCheckBox("Pre-allocate entry slots:")
        reserved_layout.addWidget(self.reserved_check)
        
        self.reserved_spin = QSpinBox()
        self.reserved_spin.setRange(0, 1000)
        self.reserved_spin.setValue(100)
        self.reserved_spin.setEnabled(False)
        self.reserved_check.toggled.connect(self.reserved_spin.setEnabled)
        reserved_layout.addWidget(self.reserved_spin)
        
        self.advanced_group.addLayout(reserved_layout)
        
        # Compression level (for V2)
        compression_layout = QHBoxLayout()
        compression_layout.addWidget(QLabel("Compression Level:"))
        
        self.compression_combo = QComboBox()
        self.compression_combo.addItems(["None", "Low", "Medium", "High"])
        self.compression_combo.setCurrentText("Medium")
        compression_layout.addWidget(self.compression_combo)
        
        self.advanced_group.addLayout(compression_layout)
        
        # Add advanced options to main layout (hidden initially)
        for i in range(self.advanced_group.count()):
            item = self.advanced_group.itemAt(i)
            if item.widget():
                item.widget().setVisible(False)
            elif item.layout():
                self._set_layout_visible(item.layout(), False)
        
        layout.addLayout(self.advanced_group)
        
        # Show/Hide advanced button
        self.advanced_btn = QPushButton("Show Advanced Options")
        self.advanced_btn.clicked.connect(self.toggle_advanced)
        layout.addWidget(self.advanced_btn)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        create_btn = QPushButton("Create IMG")
        create_btn.clicked.connect(self.accept)
        create_btn.setDefault(True)
        button_layout.addWidget(create_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
    def browse_location(self): #vers 1
        """Browse for save location"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Create New IMG File",
            "",
            "IMG Files (*.img);;All Files (*.*)"
        )
        
        if file_path:
            if not file_path.lower().endswith('.img'):
                file_path += '.img'
            self.path_input.setText(file_path)
    
    def on_version_changed(self, version_text): #vers 1
        """Handle version selection change"""
        self.img_version = "V1" if "V1" in version_text else "V2"
        
        # Update compression options based on version
        compression_enabled = self.img_version == "V2"
        self.compression_combo.setEnabled(compression_enabled)
        
    def on_template_changed(self, template_name): #vers 1
        """Handle template selection change"""
        template_id = self.template_combo.currentData()
        self.img_template = template_id
        
        # Update description
        templates = get_img_templates()
        if template_id in templates:
            self.template_desc.setText(templates[template_id]['description'])
    
    def toggle_advanced(self): #vers 1
        """Toggle advanced options visibility"""
        advanced_visible = self.advanced_btn.text() == "Show Advanced Options"
        
        # Toggle visibility
        for i in range(self.advanced_group.count()):
            item = self.advanced_group.itemAt(i)
            if item.widget():
                item.widget().setVisible(advanced_visible)
            elif item.layout():
                self._set_layout_visible(item.layout(), advanced_visible)
        
        # Update button text
        self.advanced_btn.setText("Hide Advanced Options" if advanced_visible else "Show Advanced Options")
        
        # Resize dialog
        self.adjustSize()
    
    def _set_layout_visible(self, layout, visible): #vers 1
        """Set visibility for all widgets in a layout"""
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item.widget():
                item.widget().setVisible(visible)
    
    def get_options(self): #vers 1
        """Get creation options from dialog"""
        return {
            'path': self.path_input.text(),
            'version': self.img_version,
            'template': self.img_template,
            'reserved_entries': self.reserved_spin.value() if self.reserved_check.isChecked() else 0,
            'compression': self.compression_combo.currentText()
        }

def create_new_img(main_window, img_path: str = None, options: Dict = None) -> bool: #vers 1
    """Create new IMG file
    
    Args:
        main_window: Main window instance
        img_path: Path for new IMG file (shows dialog if None)
        options: Creation options dict
        
    Returns:
        bool: True if IMG created successfully
    """
    try:
        # Show creation dialog if no path provided
        if img_path is None:
            dialog_result = show_create_img_dialog(main_window)
            if not dialog_result:
                return False
            img_path, options = dialog_result

        # Validate path
        if not validate_new_img_path(main_window, img_path):
            return False

        # Show progress
        show_progress(main_window, 0, "Creating new IMG file...")

        # Create IMG file based on template
        update_progress(main_window, 30, "Setting up IMG structure...")
        
        if options and options.get('template') != 'empty':
            img_file = _create_img_from_template(main_window, img_path, options)
        else:
            img_file = _create_empty_img_file(main_window, img_path, options)

        if not img_file:
            hide_progress(main_window)
            return False

        # Update UI
        update_progress(main_window, 80, "Updating interface...")
        success = _update_ui_for_new_img(main_window, img_file, img_path)
        
        hide_progress(main_window)
        
        if success and hasattr(main_window, 'log_message'):
            filename = os.path.basename(img_path)
            main_window.log_message(f"📄 New IMG created: {filename}")

        return success

    except Exception as e:
        hide_progress(main_window)
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Create IMG error: {str(e)}")
        return False

def create_img_with_template(main_window, template_name: str, img_path: str) -> bool: #vers 1
    """Create IMG file using specific template
    
    Args:
        main_window: Main window instance
        template_name: Template to use
        img_path: Path for new IMG file
        
    Returns:
        bool: True if created successfully
    """
    try:
        templates = get_img_templates()
        if template_name not in templates:
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"❌ Unknown template: {template_name}")
            return False

        options = {
            'template': template_name,
            'version': 'V2',
            'compression': 'Medium'
        }

        return create_new_img(main_window, img_path, options)

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Template creation error: {str(e)}")
        return False

def show_create_img_dialog(main_window) -> Optional[tuple]: #vers 1
    """Show create IMG dialog and return path and options"""
    try:
        dialog = CreateIMGDialog(main_window)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            options = dialog.get_options()
            img_path = options['path']
            
            if not img_path:
                QMessageBox.warning(main_window, "No Path", "Please specify a location for the new IMG file")
                return None
            
            return img_path, options
        
        return None

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Create dialog error: {str(e)}")
        return None

def validate_new_img_path(main_window, img_path: str) -> bool: #vers 1
    """Validate path for new IMG file"""
    try:
        # Check path is not empty
        if not img_path or not img_path.strip():
            QMessageBox.warning(main_window, "Invalid Path", "Please specify a valid path for the IMG file")
            return False

        img_path = img_path.strip()

        # Check directory exists
        img_dir = os.path.dirname(img_path)
        if img_dir and not os.path.exists(img_dir):
            reply = QMessageBox.question(
                main_window,
                "Create Directory",
                f"Directory does not exist:\n{img_dir}\n\nCreate it?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    os.makedirs(img_dir, exist_ok=True)
                except Exception as e:
                    QMessageBox.critical(main_window, "Error", f"Cannot create directory:\n{str(e)}")
                    return False
            else:
                return False

        # Check for file overwrite
        if os.path.exists(img_path):
            reply = QMessageBox.question(
                main_window,
                "File Exists",
                f"File already exists:\n{img_path}\n\nOverwrite?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply != QMessageBox.StandardButton.Yes:
                return False

        # Check write permissions
        try:
            test_path = img_path + '.tmp'
            with open(test_path, 'w') as f:
                f.write('test')
            os.remove(test_path)
        except Exception as e:
            QMessageBox.critical(main_window, "Access Denied", f"Cannot write to location:\n{str(e)}")
            return False

        return True

    except Exception as e:
        QMessageBox.critical(main_window, "Validation Error", f"Error validating path:\n{str(e)}")
        return False

def get_img_templates() -> Dict[str, Dict]: #vers 1
    """Get available IMG templates"""
    return {
        'empty': {
            'name': 'Empty IMG',
            'description': 'Creates an empty IMG file with no entries. Ready for manual file addition.',
            'entries': []
        },
        'gta_sa_basic': {
            'name': 'GTA SA Basic',
            'description': 'Basic GTA San Andreas structure with common file placeholders.',
            'entries': []  # Would contain template entries
        },
        'gta_vc_basic': {
            'name': 'GTA VC Basic', 
            'description': 'Basic GTA Vice City structure with common file placeholders.',
            'entries': []
        },
        'vehicle_template': {
            'name': 'Vehicle Template',
            'description': 'Template for vehicle mods with DFF, TXD, and COL file placeholders.',
            'entries': []
        },
        'map_template': {
            'name': 'Map Template',
            'description': 'Template for map mods with IDE, IPL, and texture file placeholders.',
            'entries': []
        }
    }

def _create_empty_img_file(main_window, img_path: str, options: Dict) -> Optional[object]: #vers 1
    """Create empty IMG file"""
    try:
        # Try to use existing IMG creation methods
        try:
            from methods.img_core_classes import IMGFile
            
            # Create new IMG file
            img_file = IMGFile()
            img_file.file_path = img_path
            img_file.version = options.get('version', 'V2')
            img_file.entries = []
            
            # Pre-allocate entries if requested
            reserved_count = options.get('reserved_entries', 0)
            if reserved_count > 0:
                # This would pre-allocate space - implementation depends on IMG structure
                pass

            # Save empty IMG file
            if img_file.save(img_path):
                return img_file
            else:
                return None
                
        except ImportError:
            # Fallback to manual IMG creation
            return _create_img_manually(main_window, img_path, options)

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Empty IMG creation error: {str(e)}")
        return None

def _create_img_from_template(main_window, img_path: str, options: Dict) -> Optional[object]: #vers 1
    """Create IMG file from template"""
    try:
        template_name = options.get('template', 'empty')
        templates = get_img_templates()
        
        if template_name not in templates:
            return _create_empty_img_file(main_window, img_path, options)

        template = templates[template_name]
        
        # Create base IMG file
        img_file = _create_empty_img_file(main_window, img_path, options)
        if not img_file:
            return None

        # Add template entries (if any)
        template_entries = template.get('entries', [])
        for entry_info in template_entries:
            # This would add placeholder entries based on template
            # Implementation depends on IMG structure
            pass

        return img_file

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Template IMG creation error: {str(e)}")
        return None

def _create_img_manually(main_window, img_path: str, options: Dict) -> Optional[object]: #vers 1
    """Manually create IMG file (fallback method)"""
    try:
        version = options.get('version', 'V2')
        
        with open(img_path, 'wb') as f:
            if version == 'V1':
                # V1 IMG header (simplified)
                f.write(b'VER2')  # Version signature
                f.write((0).to_bytes(4, 'little'))  # Entry count
                # Additional V1 structure would go here
            else:
                # V2 IMG header (simplified)
                f.write(b'VER2')  # Version signature
                f.write((0).to_bytes(4, 'little'))  # Entry count
                # Additional V2 structure would go here

        # Create simple IMG object for return
        class SimpleIMG:
            def __init__(self, path):
                self.file_path = path
                self.entries = []
                self.version = version

        return SimpleIMG(img_path)

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Manual IMG creation error: {str(e)}")
        return None

def _update_ui_for_new_img(main_window, img_file, img_path: str) -> bool: #vers 1
    """Update UI for newly created IMG file"""
    try:
        # Set as current IMG
        main_window.current_img = img_file
        if hasattr(main_window, 'current_col'):
            main_window.current_col = None

        # Update window title
        filename = os.path.basename(img_path)
        main_window.setWindowTitle(f"IMG Factory 1.5 - {filename}")

        # Populate empty table
        if hasattr(main_window, 'populate_img_table_enhanced'):
            main_window.populate_img_table_enhanced(img_file)
        else:
            populate_img_table_enhanced(main_window, img_file)

        # Update status
        if hasattr(main_window, 'refresh_ui_status'):
            main_window.refresh_ui_status()

        return True

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ UI update error: {str(e)}")
        return False

def integrate_create_img_functions(main_window) -> bool: #vers 1
    """Integrate create IMG functions into main window"""
    try:
        # Add create methods
        main_window.create_new_img = lambda img_path=None, options=None: create_new_img(main_window, img_path, options)
        main_window.create_img_with_template = lambda template_name, img_path: create_img_with_template(main_window, template_name, img_path)
        main_window.show_create_img_dialog = lambda: show_create_img_dialog(main_window)
        main_window.validate_new_img_path = lambda img_path: validate_new_img_path(main_window, img_path)
        main_window.get_img_templates = get_img_templates

        # Aliases for backward compatibility
        main_window.create_img = main_window.create_new_img
        main_window.new_img = main_window.create_new_img

        if hasattr(main_window, 'log_message'):
            main_window.log_message("✅ Create IMG functions integrated")
            main_window.log_message("   • Empty IMG creation")
            main_window.log_message("   • Template-based creation")
            main_window.log_message("   • Interactive creation dialog")
            main_window.log_message("   • Version selection (V1/V2)")
            main_window.log_message("   • Path validation and safety checks")

        return True

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Create IMG integration failed: {str(e)}")
        return False

# Export functions
__all__ = [
    'CreateIMGDialog',
    'create_new_img',
    'create_img_with_template',
    'show_create_img_dialog',
    'validate_new_img_path',
    'get_img_templates',
    'integrate_create_img_functions'
]