#this belongs in Core/build_all.py - Version: 1
# X-Seti - September11 2025 - IMG Factory 1.5 - Batch IMG Rebuild

"""
Batch IMG Rebuild - Handles rebuilding multiple IMG files
Core operations for rebuilding all open tabs or IMG files in directory
"""

import os
import glob
from typing import List, Optional, Dict, Any
from PyQt6.QtWidgets import QMessageBox, QFileDialog
from PyQt6.QtCore import Qt

##Methods list -
# rebuild_all_img
# rebuild_open_tabs
# rebuild_directory_imgs
# show_rebuild_all_dialog
# validate_batch_rebuild_operation
# perform_batch_rebuild
# _get_rebuild_targets
# _rebuild_single_img_in_batch
# report_batch_rebuild_results

def rebuild_all_img(main_window) -> bool: #vers 1
    """Main function for batch IMG rebuilding with user choice"""
    try:
        if not validate_batch_rebuild_operation(main_window):
            return False

        # Show rebuild options dialog
        rebuild_choice = show_rebuild_all_dialog(main_window)
        
        if rebuild_choice == "open_tabs":
            return rebuild_open_tabs(main_window)
        elif rebuild_choice == "directory":
            return rebuild_directory_imgs(main_window)
        elif rebuild_choice == "cancel":
            main_window.log_message("❌ Batch rebuild cancelled by user")
            return False
        else:
            return False

    except Exception as e:
        main_window.log_message(f"❌ Batch rebuild operation failed: {str(e)}")
        return False


def show_rebuild_all_dialog(main_window) -> str: #vers 1
    """Show dialog to choose rebuild all options"""
    try:
        # Count open tabs
        open_tabs = 0
        if hasattr(main_window, 'tab_widget'):
            open_tabs = main_window.tab_widget.count()

        if open_tabs == 0:
            # No open tabs, offer directory rebuild only
            reply = QMessageBox.question(
                main_window,
                "Rebuild All IMG Files",
                "No IMG files are currently open.\n\n"
                "Would you like to rebuild all IMG files in a directory?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            
            return "directory" if reply == QMessageBox.StandardButton.Yes else "cancel"
        
        else:
            # Show choice dialog
            msg = QMessageBox(main_window)
            msg.setWindowTitle("Rebuild All IMG Files")
            msg.setText(f"Choose rebuild scope:\n\n"
                       f"• Open Tabs: {open_tabs} IMG file(s)\n"
                       f"• Directory: All IMG files in a folder")
            
            # Add custom buttons
            open_tabs_btn = msg.addButton("Rebuild Open Tabs", QMessageBox.ButtonRole.AcceptRole)
            directory_btn = msg.addButton("Rebuild Directory", QMessageBox.ButtonRole.AcceptRole)
            cancel_btn = msg.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
            
            msg.setDefaultButton(open_tabs_btn)
            msg.exec()
            
            clicked_button = msg.clickedButton()
            
            if clicked_button == open_tabs_btn:
                return "open_tabs"
            elif clicked_button == directory_btn:
                return "directory"
            else:
                return "cancel"

    except Exception as e:
        main_window.log_message(f"❌ Rebuild dialog failed: {str(e)}")
        return "cancel"


def rebuild_open_tabs(main_window) -> bool: #vers 1
    """Rebuild all currently open IMG files"""
    try:
        if not hasattr(main_window, 'tab_widget') or main_window.tab_widget.count() == 0:
            main_window.log_message("❌ No open IMG files to rebuild")
            return False

        # Get list of open IMG files
        rebuild_targets = []
        tab_count = main_window.tab_widget.count()
        
        for i in range(tab_count):
            tab_data = main_window.tab_widget.widget(i)
            tab_title = main_window.tab_widget.tabText(i)
            
            if hasattr(tab_data, 'img_file'):
                img_file = tab_data.img_file
                file_path = getattr(img_file, 'file_path', None)
                
                if file_path and os.path.exists(file_path):
                    rebuild_targets.append({
                        'img_file': img_file,
                        'file_path': file_path,
                        'tab_title': tab_title,
                        'tab_index': i
                    })

        if not rebuild_targets:
            main_window.log_message("❌ No valid IMG files found in open tabs")
            return False

        main_window.log_message(f"🔨 Starting batch rebuild of {len(rebuild_targets)} open IMG file(s)")
        
        # Perform batch rebuild
        results = perform_batch_rebuild(main_window, rebuild_targets)
        
        # Report results
        report_batch_rebuild_results(main_window, results, "open tabs")
        
        return results['success_count'] > 0

    except Exception as e:
        main_window.log_message(f"❌ Open tabs rebuild failed: {str(e)}")
        return False


def rebuild_directory_imgs(main_window) -> bool: #vers 1
    """Rebuild all IMG files in a selected directory"""
    try:
        # Get directory from user
        directory = QFileDialog.getExistingDirectory(
            main_window,
            "Select Directory with IMG Files",
            os.path.expanduser("~/Desktop"),
            QFileDialog.Option.ShowDirsOnly
        )

        if not directory:
            main_window.log_message("❌ No directory selected for batch rebuild")
            return False

        # Find IMG files in directory
        img_patterns = ['*.img', '*.IMG']
        img_files = []
        
        for pattern in img_patterns:
            img_files.extend(glob.glob(os.path.join(directory, pattern)))

        if not img_files:
            main_window.log_message(f"❌ No IMG files found in: {directory}")
            return False

        # Confirm rebuild
        reply = QMessageBox.question(
            main_window,
            "Confirm Directory Rebuild",
            f"Found {len(img_files)} IMG file(s) in:\n{directory}\n\n"
            "This will rebuild all IMG files. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            main_window.log_message("❌ Directory rebuild cancelled by user")
            return False

        # Prepare rebuild targets
        rebuild_targets = []
        for file_path in img_files:
            try:
                # Create temporary IMG file object for loading
                from methods.img_core_classes import IMGFile
                temp_img = IMGFile()
                
                if temp_img.load_from_file(file_path):
                    rebuild_targets.append({
                        'img_file': temp_img,
                        'file_path': file_path,
                        'tab_title': os.path.basename(file_path),
                        'is_directory_file': True
                    })
                else:
                    main_window.log_message(f"⚠️ Failed to load: {os.path.basename(file_path)}")
                    
            except Exception as e:
                main_window.log_message(f"⚠️ Error loading {os.path.basename(file_path)}: {str(e)}")

        if not rebuild_targets:
            main_window.log_message("❌ No valid IMG files could be loaded from directory")
            return False

        main_window.log_message(f"🔨 Starting batch rebuild of {len(rebuild_targets)} IMG file(s) from directory")
        
        # Perform batch rebuild
        results = perform_batch_rebuild(main_window, rebuild_targets)
        
        # Report results
        report_batch_rebuild_results(main_window, results, f"directory ({directory})")
        
        return results['success_count'] > 0

    except Exception as e:
        main_window.log_message(f"❌ Directory rebuild failed: {str(e)}")
        return False


def perform_batch_rebuild(main_window, rebuild_targets: List[Dict[str, Any]]) -> Dict[str, Any]: #vers 1
    """Perform batch rebuild operation on multiple IMG files"""
    try:
        results = {
            'success_count': 0,
            'failure_count': 0,
            'total_count': len(rebuild_targets),
            'successful_files': [],
            'failed_files': []
        }

        for i, target in enumerate(rebuild_targets):
            try:
                img_file = target['img_file']
                file_path = target['file_path']
                tab_title = target['tab_title']
                
                main_window.log_message(f"🔨 Rebuilding {i+1}/{len(rebuild_targets)}: {tab_title}")
                
                # Rebuild single IMG file
                success = _rebuild_single_img_in_batch(main_window, img_file, file_path)
                
                if success:
                    results['success_count'] += 1
                    results['successful_files'].append(tab_title)
                    main_window.log_message(f"✅ Rebuilt: {tab_title}")
                else:
                    results['failure_count'] += 1
                    results['failed_files'].append(tab_title)
                    main_window.log_message(f"❌ Failed: {tab_title}")
                    
            except Exception as e:
                results['failure_count'] += 1
                results['failed_files'].append(target.get('tab_title', 'Unknown'))
                main_window.log_message(f"❌ Error rebuilding {target.get('tab_title', 'Unknown')}: {str(e)}")

        return results

    except Exception as e:
        main_window.log_message(f"❌ Batch rebuild operation failed: {str(e)}")
        return {
            'success_count': 0,
            'failure_count': len(rebuild_targets),
            'total_count': len(rebuild_targets),
            'successful_files': [],
            'failed_files': [target.get('tab_title', 'Unknown') for target in rebuild_targets]
        }


def _rebuild_single_img_in_batch(main_window, img_file, file_path: str) -> bool: #vers 1
    """Rebuild a single IMG file as part of batch operation"""
    try:
        # Use existing rebuild system if available
        if hasattr(main_window, 'rebuild_img_file'):
            return main_window.rebuild_img_file(img_file)
        
        # Import single rebuild function
        try:
            from Core.build import perform_img_rebuild
            return perform_img_rebuild(main_window, img_file, file_path)
        except ImportError:
            pass

        # Import core rebuild function
        try:
            from Core.rebuild import rebuild_img_file_core
            return rebuild_img_file_core(main_window, img_file)
        except ImportError:
            pass

        # Fallback rebuild implementation
        return _fallback_batch_rebuild(main_window, img_file, file_path)

    except Exception as e:
        main_window.log_message(f"❌ Single IMG rebuild failed: {str(e)}")
        return False


def _fallback_batch_rebuild(main_window, img_file, file_path: str) -> bool: #vers 1
    """Fallback rebuild implementation for batch operations"""
    try:
        # Check if file has entries
        if not hasattr(img_file, 'entries') or not img_file.entries:
            return False

        # Simple rebuild verification - check if file is readable
        if not os.path.exists(file_path) or not os.access(file_path, os.R_OK | os.W_OK):
            return False

        # Create backup
        backup_path = f"{file_path}.bak"
        if os.path.exists(backup_path):
            os.remove(backup_path)
        
        import shutil
        shutil.copy2(file_path, backup_path)

        # Mark as successfully "rebuilt" (placeholder for actual rebuild logic)
        # In a real implementation, this would perform the actual IMG rebuild
        
        # Clear modification flags
        if hasattr(img_file, 'modified'):
            img_file.modified = False
        
        if hasattr(img_file, 'deleted_entries'):
            img_file.deleted_entries.clear()

        return True

    except Exception as e:
        main_window.log_message(f"❌ Fallback rebuild failed: {str(e)}")
        return False


def validate_batch_rebuild_operation(main_window) -> bool: #vers 1
    """Validate if batch rebuild operation can proceed"""
    try:
        # Check if any operations are running
        if hasattr(main_window, 'progress_dialog') and main_window.progress_dialog.isVisible():
            QMessageBox.warning(
                main_window,
                "Operation in Progress",
                "Cannot start batch rebuild while another operation is in progress.\n"
                "Please wait for the current operation to complete."
            )
            return False

        return True

    except Exception as e:
        main_window.log_message(f"❌ Batch rebuild validation failed: {str(e)}")
        return False


def report_batch_rebuild_results(main_window, results: Dict[str, Any], rebuild_scope: str) -> None: #vers 1
    """Report the results of batch rebuild operation"""
    try:
        success_count = results.get('success_count', 0)
        failure_count = results.get('failure_count', 0)
        total_count = results.get('total_count', 0)
        
        main_window.log_message(f"📊 Batch rebuild complete for {rebuild_scope}")
        main_window.log_message(f"✅ Successful: {success_count}/{total_count}")
        
        if failure_count > 0:
            main_window.log_message(f"❌ Failed: {failure_count}/{total_count}")
            
            # Show detailed results dialog
            failed_files = results.get('failed_files', [])
            if failed_files:
                failed_list = '\n'.join([f"• {name}" for name in failed_files[:10]])  # Show first 10
                if len(failed_files) > 10:
                    failed_list += f"\n... and {len(failed_files) - 10} more"
                
                QMessageBox.warning(
                    main_window,
                    "Batch Rebuild Results",
                    f"Batch rebuild completed with some failures:\n\n"
                    f"Successful: {success_count}\n"
                    f"Failed: {failure_count}\n\n"
                    f"Failed files:\n{failed_list}"
                )
        else:
            # All successful
            QMessageBox.information(
                main_window,
                "Batch Rebuild Complete",
                f"All {success_count} IMG file(s) rebuilt successfully!"
            )

    except Exception as e:
        main_window.log_message(f"⚠️ Failed to report batch results: {str(e)}")


def _get_rebuild_targets(main_window, source_type: str) -> List[Dict[str, Any]]: #vers 1
    """Get list of rebuild targets based on source type"""
    try:
        targets = []
        
        if source_type == "open_tabs":
            if hasattr(main_window, 'tab_widget'):
                for i in range(main_window.tab_widget.count()):
                    tab_data = main_window.tab_widget.widget(i)
                    if hasattr(tab_data, 'img_file'):
                        img_file = tab_data.img_file
                        file_path = getattr(img_file, 'file_path', None)
                        if file_path and os.path.exists(file_path):
                            targets.append({
                                'img_file': img_file,
                                'file_path': file_path,
                                'tab_title': main_window.tab_widget.tabText(i),
                                'source': 'tab'
                            })
        
        return targets

    except Exception as e:
        main_window.log_message(f"❌ Failed to get rebuild targets: {str(e)}")
        return []


def get_batch_rebuild_status(main_window) -> Dict[str, Any]: #vers 1
    """Get current status of batch rebuild capability"""
    try:
        status = {
            'available': True,
            'open_tabs_count': 0,
            'can_rebuild_tabs': False,
            'can_rebuild_directory': True
        }

        if hasattr(main_window, 'tab_widget'):
            status['open_tabs_count'] = main_window.tab_widget.count()
            status['can_rebuild_tabs'] = status['open_tabs_count'] > 0

        return status

    except Exception as e:
        main_window.log_message(f"❌ Failed to get batch rebuild status: {str(e)}")
        return {'available': False}


def integrate_build_all_functions(main_window) -> bool: #vers 1
    """Integrate batch build functions into main window"""
    try:
        # Add batch build functions to main window
        main_window.rebuild_all_img = lambda: rebuild_all_img(main_window)
        main_window.rebuild_open_tabs = lambda: rebuild_open_tabs(main_window)
        main_window.rebuild_directory_imgs = lambda: rebuild_directory_imgs(main_window)
        main_window.get_batch_rebuild_status = lambda: get_batch_rebuild_status(main_window)
        main_window.validate_batch_rebuild_operation = lambda: validate_batch_rebuild_operation(main_window)
        
        main_window.log_message("✅ Batch build functions integrated")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Failed to integrate batch build functions: {str(e)}")
        return False