#this belongs in Apps/Gui/gui_button_layout.py - Version: 1
# X-Seti - September13 2025 - IMG Factory 1.5 - GUI Button Layout System

"""
GUI Button Layout System - Button definitions, themes, and layout management
Separated from main GUI layout for better organization and maintenance
"""

##Methods list -
# get_button_theme_template
# get_img_buttons_data
# get_entry_buttons_data
# get_options_buttons_data
# get_editor_buttons_data
# is_dark_theme_check
# create_button_sections
# apply_button_theme_styling

def get_button_theme_template(main_window, theme_name="default"): #vers 2
    """Get button color templates based on theme"""
    if is_dark_theme_check(main_window):
        return {
            # Dark Theme Button Colors
            'create_action': '#3D5A5A',     # Dark teal for create/new actions
            'open_action': '#3D4A5F',       # Dark blue for open/load actions
            'reload_action': '#2D4A3A',     # Dark green for refresh/reload
            'close_action': '#5A4A3D',      # Dark orange for close actions
            'build_action': '#2D4A3A',      # Dark mint for build/rebuild
            'save_action': '#4A2D4A',       # Dark purple for save actions
            'merge_action': '#3A2D4A',      # Dark violet for merge/split
            'convert_action': '#4A4A2D',    # Dark yellow for convert
            'import_action': '#2D4A4F',     # Dark cyan for import
            'export_action': '#2D4A3A',     # Dark emerald for export
            'remove_action': '#4A2D2D',     # Dark red for remove/delete
            'edit_action': '#4A3A2D',       # Dark amber for edit actions
            'select_action': '#3A4A2D',     # Dark lime for select actions
            'editor_col': '#2D3A4F',        # Dark blue for COL editor
            'editor_txd': '#4A2D4A',        # Dark magenta for TXD editor
            'editor_dff': '#2D4A4F',        # Dark cyan for DFF editor
            'editor_data': '#3A4A2D',       # Dark olive for data editors
            'editor_map': '#4A2D4A',        # Dark purple for map editors
            'editor_vehicle': '#2D4A3A',    # Dark teal for vehicle editors
            'editor_script': '#4A3A2D',     # Dark gold for script editors
            'placeholder': '#2A2A2A',       # Dark gray for spacers
        }
    else:
        return {
            # Light Theme Button Colors
            'create_action': '#EEFAFA',     # Light teal for create/new actions
            'open_action': '#E3F2FD',       # Light blue for open/load actions
            'reload_action': '#E8F5E8',     # Light green for refresh/reload
            'close_action': '#FFF3E0',      # Light orange for close actions
            'build_action': '#E8F5E8',      # Light mint for build/rebuild
            'save_action': '#F8BBD9',       # Light pink for save actions
            'merge_action': '#F3E5F5',      # Light violet for merge/split
            'convert_action': '#FFF8E1',    # Light yellow for convert
            'import_action': '#E1F5FE',     # Light cyan for import
            'export_action': '#E8F5E8',     # Light emerald for export
            'remove_action': '#FFEBEE',     # Light red for remove/delete
            'edit_action': '#FFF8E1',       # Light amber for edit actions
            'select_action': '#F1F8E9',     # Light lime for select actions
            'editor_col': '#E3F2FD',        # Light blue for COL editor
            'editor_txd': '#F8BBD9',        # Light pink for TXD editor
            'editor_dff': '#E1F5FE',        # Light cyan for DFF editor
            'editor_data': '#D3F2AD',       # Light lime for data editors
            'editor_map': '#F8BBD9',        # Light pink for map editors
            'editor_vehicle': '#E3F2BD',    # Light olive for vehicle editors
            'editor_script': '#FFD0BD',     # Light peach for script editors
            'placeholder': '#FEFEFE',       # Light gray for spacers
        }

def is_dark_theme_check(main_window): #vers 1
    """Check if current theme is dark"""
    try:
        # Check if theme system is available
        from Shared.theme_system import is_dark_theme
        return is_dark_theme()
    except ImportError:
        # Fallback: check palette
        try:
            palette = main_window.palette()
            bg_color = palette.color(palette.ColorRole.Window)
            return bg_color.lightness() < 128
        except:
            return False  # Default to light theme

def get_img_buttons_data(): #vers 1
    """Get IMG operations button data - Complete button list"""
    return [
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

def get_entry_buttons_data(): #vers 1
    """Get Entry operations button data - Complete button list"""
    return [
        ("Import", "import_files", "import_action"),
        ("Import via", "import_files_via", "import_action"),
        ("Refresh", "refresh_table", "reload_action"),  # Fixed from "Update List"
        ("Export", "export_selected", "export_action"),
        ("Export via", "export_selected_via", "export_action"),
        ("Quick Export", "quick_export_selected", "export_action"),
        ("Remove", "remove_selected", "remove_action"),
        ("Remove via", "remove_via_entries", "remove_action"),
        ("Dump", "dump_entries", "export_action")
    ]

def get_options_buttons_data(): #vers 1
    """Get Selection & Edit button data - Complete button list"""
    return [
        ("Select All", "select_all_entries", "select_action"),
        ("Select Inverse", "select_inverse", "select_action"),
        ("Sort Entries", "sort_entries", "select_action"),
        ("Pin Selected", "pin_selected_entries", "select_action"),
        ("Rename", "rename_selected", "edit_action"),
        ("Replace", "replace_selected", "edit_action")
    ]

def get_editor_buttons_data(): #vers 1
    """Get Editor tool buttons data - For future editor integration"""
    return [
        ("COL Editor", "open_col_editor", "editor_col"),
        ("TXD Editor", "open_txd_editor", "editor_txd"),
        ("DFF Editor", "open_dff_editor", "editor_dff"),
        ("Data Editor", "open_data_editor", "editor_data"),
        ("Map Editor", "open_map_editor", "editor_map"),
        ("Vehicle Editor", "open_vehicle_editor", "editor_vehicle"),
        ("Script Editor", "open_script_editor", "editor_script")
    ]

def create_button_sections(): #vers 1
    """Get all button sections organized by category"""
    return {
        'img_operations': {
            'title': 'IMG Operations',
            'buttons': get_img_buttons_data()
        },
        'entry_operations': {
            'title': 'Entry Operations', 
            'buttons': get_entry_buttons_data()
        },
        'selection_edit': {
            'title': 'Selection & Edit',
            'buttons': get_options_buttons_data()
        },
        'editors': {
            'title': 'File Editors',
            'buttons': get_editor_buttons_data()
        }
    }

def apply_button_theme_styling(btn, theme_key, main_window): #vers 1
    """Apply theme styling to a button"""
    colors = get_button_theme_template(main_window)
    color = colors.get(theme_key, colors['placeholder'])
    
    # Helper functions for color manipulation
    def lighten_color(hex_color):
        """Lighten a hex color"""
        try:
            hex_color = hex_color.lstrip('#')
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            lighter_rgb = tuple(min(255, int(c * 1.2)) for c in rgb)
            return f"#{''.join(f'{c:02x}' for c in lighter_rgb)}"
        except:
            return hex_color

    def darken_color(hex_color):
        """Darken a hex color"""
        try:
            hex_color = hex_color.lstrip('#')
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            darker_rgb = tuple(max(0, int(c * 0.8)) for c in rgb)
            return f"#{''.join(f'{c:02x}' for c in darker_rgb)}"
        except:
            return hex_color
    
    # Apply button styling
    btn.setStyleSheet(f"""
        QPushButton {{
            background-color: {color};
            border: 1px solid #ccc;
            border-radius: 4px;
            padding: 4px 8px;
            font-weight: bold;
            font-size: 11px;
        }}
        QPushButton:hover {{
            background-color: {lighten_color(color)};
            border: 1px solid #999;
        }}
        QPushButton:pressed {{
            background-color: {darken_color(color)};
            border: 1px solid #666;
        }}
        QPushButton:disabled {{
            background-color: #f0f0f0;
            color: #888;
            border: 1px solid #ddd;
        }}
    """)

def get_short_text_mappings(): #vers 1
    """Get text mappings for small button display"""
    return {
        "Select All": "All",
        "Select Inverse": "Inv", 
        "Sort Entries": "Sort",
        "Pin Selected": "Pin",
        "Quick Export": "QExp",
        "Remove via": "RemV",
        "Export via": "ExpV", 
        "Import via": "ImpV",
        "Close All": "ClAll",
        "Rebuild All": "RbAll",
        "Save Entry": "Save",
        "COL Editor": "COL",
        "TXD Editor": "TXD",
        "DFF Editor": "DFF",
        "Data Editor": "Data",
        "Map Editor": "Map",
        "Vehicle Editor": "Veh",
        "Script Editor": "Script"
    }

def get_button_tooltips(): #vers 1
    """Get tooltips for all buttons"""
    return {
        # IMG Operations
        "create_img_file": "Create a new IMG archive file",
        "open_img_file": "Open existing IMG archive file",
        "reload_img_file": "Reload current IMG file from disk",
        "close_img_file": "Close current IMG file",
        "close_all_img": "Close all open IMG files",
        "rebuild_img": "Rebuild current IMG file structure",
        "rebuild_all_img": "Rebuild all open IMG files",
        "save_img_entry": "Save changes to IMG entry",
        "merge_img": "Merge multiple IMG files",
        "split_img": "Split IMG file into parts",
        "convert_img_format": "Convert IMG file format",
        
        # Entry Operations
        "import_files": "Import files into IMG archive",
        "import_files_via": "Import files with advanced options",
        "refresh_table": "Refresh the entries table",
        "export_selected": "Export selected entries",
        "export_selected_via": "Export selected with advanced options",
        "quick_export_selected": "Quick export selected entries",
        "remove_selected": "Remove selected entries",
        "remove_via_entries": "Remove entries with confirmation",
        "dump_entries": "Dump entries to files",
        
        # Selection & Edit
        "select_all_entries": "Select all entries in table",
        "select_inverse": "Invert current selection",
        "sort_entries": "Sort entries by name",
        "pin_selected_entries": "Pin selected entries to top",
        "rename_selected": "Rename selected entry",
        "replace_selected": "Replace selected entry content",
        
        # Editors
        "open_col_editor": "Open COL collision editor",
        "open_txd_editor": "Open TXD texture editor",
        "open_dff_editor": "Open DFF model editor",
        "open_data_editor": "Open data file editor",
        "open_map_editor": "Open map editor",
        "open_vehicle_editor": "Open vehicle editor",
        "open_script_editor": "Open script editor"
    }

# Export functions
__all__ = [
    'get_button_theme_template',
    'get_img_buttons_data',
    'get_entry_buttons_data', 
    'get_options_buttons_data',
    'get_editor_buttons_data',
    'is_dark_theme_check',
    'create_button_sections',
    'apply_button_theme_styling',
    'get_short_text_mappings',
    'get_button_tooltips'
]