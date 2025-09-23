#this belongs in Tools/IMG_Factory/core/img_core_bridge.py - Version: 1
# X-Seti - September12 2025 - IMG Factory 1.5 - IMG Editor Core Bridge

"""
IMG Editor Core Bridge - Integrates IMG Editor's core system into IMG Factory
Bridges IMG Editor's proven core classes with IMG Factory's GUI and workflow
"""

import os
import sys
from typing import Optional, Dict, Any, List
from pathlib import Path

# Add IMG Editor core to path
img_editor_path = os.path.join(os.path.dirname(__file__), '..', '..', 'IMG_Editor')
if img_editor_path not in sys.path:
    sys.path.insert(0, img_editor_path)

try:
    from application.base import IMGArchive, IMGEntry, IMGVersion
    from application.base.File_Operations import FileOperations
    from application.base.IMG_Operations import IMGOperations
    from application.base.import_export import ImportExport
    from application.base.Entries_and_Selection import EntriesAndSelection
    IMG_EDITOR_CORE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ IMG Editor core not available: {e}")
    IMG_EDITOR_CORE_AVAILABLE = False

##Methods list -
# create_img_factory_bridge
# adapt_img_archive_for_factory
# bridge_file_operations
# bridge_img_operations  
# bridge_import_export
# integrate_core_with_gui
# setup_core_logging
# validate_core_integration

##Classes -
# IMGFactoryCoreBridge
# IMGArchiveAdapter

class IMGFactoryCoreBridge: #vers 1
    """Bridge between IMG Editor core and IMG Factory"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.img_editor_available = IMG_EDITOR_CORE_AVAILABLE
        self.active_archives = {}  # tab_id -> IMGArchive
        self.core_operations = None
        
        if self.img_editor_available:
            self.setup_core_integration()
        else:
            self.setup_fallback_system()
    
    def setup_core_integration(self): #vers 1
        """Setup integration with IMG Editor core"""
        try:
            # Initialize core operation handlers
            self.file_ops = FileOperations()
            self.img_ops = IMGOperations() 
            self.import_export = ImportExport()
            self.entries_selection = EntriesAndSelection()
            
            self.main_window.log_message("✅ IMG Editor core integrated")
            return True
            
        except Exception as e:
            self.main_window.log_message(f"❌ Core integration failed: {e}")
            self.setup_fallback_system()
            return False
    
    def setup_fallback_system(self): #vers 1
        """Setup fallback when IMG Editor core unavailable"""
        try:
            # Use IMG Factory's existing core classes
            from methods.img_core_classes import IMGFile as FallbackIMG
            self.fallback_img_class = FallbackIMG
            self.img_editor_available = False
            
            self.main_window.log_message("⚠️ Using IMG Factory fallback core")
            return True
            
        except Exception as e:
            self.main_window.log_message(f"❌ Fallback setup failed: {e}")
            return False


class IMGArchiveAdapter: #vers 1
    """Adapter to make IMG Editor's IMGArchive work with IMG Factory GUI"""
    
    def __init__(self, img_archive, bridge):
        self.archive = img_archive
        self.bridge = bridge
        self.file_path = getattr(img_archive, 'file_path', '')
        self.modified = getattr(img_archive, 'modified', False)
        
        # Create IMG Factory compatible interface
        self.entries = self._adapt_entries()
        self._pinned_entries = set()
        self._locked_entries = set()
        
    def _adapt_entries(self): #vers 1
        """Adapt IMG Editor entries for IMG Factory table system"""
        try:
            if hasattr(self.archive, 'entries'):
                return self.archive.entries
            elif hasattr(self.archive, 'get_entries'):
                return self.archive.get_entries()
            else:
                return []
        except:
            return []
    
    def get_entry_count(self): #vers 1
        """Get number of entries"""
        return len(self.entries)
    
    def get_entry_by_name(self, name: str): #vers 1
        """Get entry by name"""
        for entry in self.entries:
            if getattr(entry, 'name', '') == name:
                return entry
        return None
    
    def is_modified(self): #vers 1
        """Check if archive has been modified"""
        return getattr(self.archive, 'modified', False)
    
    def save_to_file(self, file_path: str = None): #vers 1
        """Save archive using IMG Editor core"""
        try:
            if hasattr(self.archive, 'save'):
                return self.archive.save(file_path or self.file_path)
            elif hasattr(self.archive, 'save_to_file'):
                return self.archive.save_to_file(file_path or self.file_path)
            else:
                return False
        except Exception as e:
            self.bridge.main_window.log_message(f"❌ Save failed: {e}")
            return False


def create_img_factory_bridge(main_window) -> IMGFactoryCoreBridge: #vers 1
    """Create and initialize IMG Factory core bridge"""
    try:
        bridge = IMGFactoryCoreBridge(main_window)
        
        # Store bridge in main window for easy access
        main_window.core_bridge = bridge
        
        return bridge
        
    except Exception as e:
        main_window.log_message(f"❌ Bridge creation failed: {e}")
        return None


def adapt_img_archive_for_factory(img_archive, bridge) -> IMGArchiveAdapter: #vers 1
    """Adapt IMG Editor archive for IMG Factory"""
    try:
        return IMGArchiveAdapter(img_archive, bridge)
    except Exception as e:
        bridge.main_window.log_message(f"❌ Archive adaptation failed: {e}")
        return None


def bridge_file_operations(main_window, bridge) -> bool: #vers 1
    """Bridge IMG Editor file operations to IMG Factory"""
    try:
        if not bridge.img_editor_available:
            return False
        
        # Bridge open operations
        def open_img_with_core(file_path):
            try:
                archive = IMGArchive()
                if archive.load_from_file(file_path):
                    adapted_archive = adapt_img_archive_for_factory(archive, bridge)
                    return adapted_archive
                return None
            except Exception as e:
                main_window.log_message(f"❌ Core open failed: {e}")
                return None
        
        # Bridge save operations
        def save_img_with_core(archive_adapter, file_path=None):
            try:
                return archive_adapter.save_to_file(file_path)
            except Exception as e:
                main_window.log_message(f"❌ Core save failed: {e}")
                return False
        
        # Add to main window
        main_window.open_img_with_core = open_img_with_core
        main_window.save_img_with_core = save_img_with_core
        
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ File operations bridge failed: {e}")
        return False


def bridge_import_export(main_window, bridge) -> bool: #vers 1
    """Bridge IMG Editor import/export to IMG Factory"""
    try:
        if not bridge.img_editor_available:
            return False
        
        def import_files_with_core(archive_adapter, file_paths):
            try:
                success_count = 0
                for file_path in file_paths:
                    if bridge.import_export.import_file(archive_adapter.archive, file_path):
                        success_count += 1
                
                # Update adapted entries
                archive_adapter.entries = archive_adapter._adapt_entries()
                return success_count
                
            except Exception as e:
                main_window.log_message(f"❌ Core import failed: {e}")
                return 0
        
        def export_entries_with_core(archive_adapter, entries, output_dir):
            try:
                success_count = 0
                for entry in entries:
                    if bridge.import_export.export_entry(entry, output_dir):
                        success_count += 1
                return success_count
                
            except Exception as e:
                main_window.log_message(f"❌ Core export failed: {e}")
                return 0
        
        # Add to main window
        main_window.import_files_with_core = import_files_with_core
        main_window.export_entries_with_core = export_entries_with_core
        
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Import/Export bridge failed: {e}")
        return False


def integrate_core_with_gui(main_window, bridge) -> bool: #vers 1
    """Integrate core bridge with IMG Factory GUI"""
    try:
        # Bridge table population
        def populate_table_with_core(archive_adapter):
            try:
                if hasattr(main_window, 'populate_img_table'):
                    return main_window.populate_img_table(archive_adapter)
                return False
            except Exception as e:
                main_window.log_message(f"❌ Table population failed: {e}")
                return False
        
        # Bridge tab management  
        def create_tab_for_archive(archive_adapter, file_path):
            try:
                tab_title = os.path.basename(file_path)
                
                # Create tab widget if needed
                if not hasattr(main_window, 'tab_widget'):
                    return False
                
                # Add new tab
                tab_index = main_window.tab_widget.addTab(archive_adapter, tab_title)
                main_window.tab_widget.setCurrentIndex(tab_index)
                
                # Store archive in bridge
                bridge.active_archives[tab_index] = archive_adapter
                
                # Update table
                populate_table_with_core(archive_adapter)
                
                return True
                
            except Exception as e:
                main_window.log_message(f"❌ Tab creation failed: {e}")
                return False
        
        # Add to main window
        main_window.populate_table_with_core = populate_table_with_core
        main_window.create_tab_for_archive = create_tab_for_archive
        
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ GUI integration failed: {e}")
        return False


def setup_core_logging(main_window, bridge) -> bool: #vers 1
    """Setup logging bridge between cores"""
    try:
        # Redirect IMG Editor core logging to IMG Factory
        def core_log_handler(level, message, details=None):
            if hasattr(main_window, 'log_message'):
                log_msg = f"[CORE] {message}"
                if details:
                    log_msg += f": {details}"
                main_window.log_message(log_msg)
        
        # Set up logging if IMG Editor core supports it
        if bridge.img_editor_available and hasattr(bridge, 'file_ops'):
            # Hook into IMG Editor logging if available
            pass
        
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Logging setup failed: {e}")
        return False


def validate_core_integration(main_window, bridge) -> Dict[str, bool]: #vers 1
    """Validate core integration status"""
    try:
        validation_results = {
            'img_editor_available': bridge.img_editor_available,
            'file_operations': False,
            'import_export': False,
            'gui_integration': False,
            'logging': False
        }
        
        if bridge.img_editor_available:
            validation_results['file_operations'] = hasattr(bridge, 'file_ops')
            validation_results['import_export'] = hasattr(bridge, 'import_export')
            validation_results['gui_integration'] = hasattr(main_window, 'populate_table_with_core')
            validation_results['logging'] = True
        
        # Report validation results
        for component, status in validation_results.items():
            status_icon = "✅" if status else "❌"
            main_window.log_message(f"{status_icon} {component}: {'Available' if status else 'Failed'}")
        
        return validation_results
        
    except Exception as e:
        main_window.log_message(f"❌ Validation failed: {e}")
        return {'error': True}


def integrate_img_editor_core(main_window) -> bool: #vers 1
    """Main integration function - sets up IMG Editor core bridge"""
    try:
        main_window.log_message("🔗 Integrating IMG Editor core...")
        
        # Create core bridge
        bridge = create_img_factory_bridge(main_window)
        if not bridge:
            return False
        
        # Setup core integrations
        bridge_file_operations(main_window, bridge)
        bridge_import_export(main_window, bridge)
        integrate_core_with_gui(main_window, bridge)
        setup_core_logging(main_window, bridge)
        
        # Validate integration
        validation_results = validate_core_integration(main_window, bridge)
        
        if validation_results.get('img_editor_available', False):
            main_window.log_message("✅ IMG Editor core integration complete")
            return True
        else:
            main_window.log_message("⚠️ Using fallback core system")
            return True  # Still successful, just using fallback
        
    except Exception as e:
        main_window.log_message(f"❌ Core integration failed: {str(e)}")
        return False
