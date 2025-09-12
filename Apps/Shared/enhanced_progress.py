#this belongs in Apps/Shared/enhanced_progress.py - Version: 1  
# X-Seti - September12 2025 - IMG Factory 1.5 - Enhanced Progress System

"""
Enhanced Progress System - Unified progress dialogs and panels
Merges IMG Editor's progress_dialog.py with existing progress_functions.py
Provides both modal dialogs and embedded progress panels
"""

import os
from typing import Optional, Callable
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, 
    QPushButton, QFrame, QWidget, QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QThread, pyqtSlot
from PyQt6.QtGui import QFont

##Methods list -
# create_progress_dialog
# create_progress_panel  
# show_modal_progress
# update_embedded_progress
# setup_progress_system
# integrate_with_existing_functions
# _apply_progress_styling
# _handle_progress_cancellation
# execute_with_progress
# batch_operation_progress

##Classes -
# ProgressDialog
# EmbeddedProgressPanel
# ProgressManager
# ProgressWorkerThread

class ProgressDialog(QDialog): #vers 1
    """Mmodal progress dialog with cancellation"""
    
    # Signals
    cancelled = pyqtSignal()
    operation_completed = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, title="Operation in Progress", parent=None, allow_cancel=True):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(450, 180)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowTitleHint)
        
        self._cancelled = False
        self._allow_cancel = allow_cancel
        self._operation_running = False
        
        self._setup_ui()
        self._apply_styling()
    
    def _setup_ui(self): #vers 1
        """Setup the dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 15, 20, 15)
        
        # Status label
        self.status_label = QLabel("Initializing operation...")
        self.status_label.setWordWrap(True)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.status_label.setMinimumHeight(40)
        layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(18)
        layout.addWidget(self.progress_bar)
    
    def _apply_styling(self): #vers 1
        """Apply styling to embedded panel"""
        self.setStyleSheet("""
            QFrame {
                background-color: #353535;
                border: 1px solid #555;
                border-radius: 5px;
            }
            QLabel {
                color: white;
                background: transparent;
            }
            QProgressBar {
                border: 1px solid #555;
                border-radius: 2px;
                background-color: #404040;
                color: white;
                text-align: center;
                font-size: 10px;
            }
            QProgressBar::chunk {
                background-color: #0078d4;
                border-radius: 1px;
            }
            QPushButton {
                background-color: #444;
                border: 1px solid #666;
                border-radius: 2px;
                color: white;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #555;
            }
        """)
    
    def start_operation(self, title: str = "Operation in Progress"): #vers 1
        """Start operation and show panel"""
        self._operation_running = True
        self._cancelled = False
        
        self.title_label.setText(title)
        self.status_label.setText("Starting...")
        self.progress_bar.setValue(0)
        self.cancel_button.setText("Cancel")
        self.cancel_button.setEnabled(True)
        
        self.setVisible(True)
    
    def update_progress(self, percentage: int, message: str = ""): #vers 1
        """Update progress and status"""
        if self._cancelled:
            return
        
        percentage = max(0, min(100, percentage))
        self.progress_bar.setValue(percentage)
        
        if message:
            self.status_label.setText(message)
    
    def complete_operation(self, success: bool, message: str = ""): #vers 1
        """Complete operation and hide panel"""
        self._operation_running = False
        
        if success:
            self.progress_bar.setValue(100)
            self.status_label.setText(message or "Completed successfully!")
            # Auto-hide after short delay
            QTimer.singleShot(2000, self.hide)
        else:
            self.status_label.setText(message or "Operation failed!")
            self.cancel_button.setText("Close")
    
    def _on_cancel_clicked(self): #vers 1
        """Handle cancel button"""
        if self._operation_running and not self._cancelled:
            self._cancelled = True
            self.status_label.setText("Cancelling...")
            self.cancel_button.setText("Cancelling...")
            self.cancel_button.setEnabled(False)
            self.cancelled.emit()
        else:
            self.hide()
    
    def is_cancelled(self) -> bool: #vers 1
        """Check if cancelled"""
        return self._cancelled


class ProgressWorkerThread(QThread): #vers 1
    """Worker thread for running operations with progress"""
    
    # Signals
    progress_updated = pyqtSignal(int, str, str)  # percentage, message, details
    operation_completed = pyqtSignal(bool, str)   # success, result_message
    
    def __init__(self, operation_func: Callable, *args, **kwargs):
        super().__init__()
        self.operation_func = operation_func
        self.operation_args = args
        self.operation_kwargs = kwargs
        self._cancelled = False
    
    def run(self): #vers 1
        """Run the operation in thread"""
        try:
            # Add progress callback to kwargs
            self.operation_kwargs['progress_callback'] = self._progress_callback
            self.operation_kwargs['cancel_check'] = self._is_cancelled
            
            # Execute operation
            result = self.operation_func(*self.operation_args, **self.operation_kwargs)
            
            if not self._cancelled:
                if isinstance(result, tuple):
                    success, message = result
                else:
                    success, message = bool(result), "Operation completed"
                
                self.operation_completed.emit(success, message)
            
        except Exception as e:
            if not self._cancelled:
                self.operation_completed.emit(False, f"Operation failed: {str(e)}")
    
    def _progress_callback(self, percentage: int, message: str = "", details: str = ""): #vers 1
        """Internal progress callback"""
        if not self._cancelled:
            self.progress_updated.emit(percentage, message, details)
    
    def _is_cancelled(self) -> bool: #vers 1
        """Check if operation should be cancelled"""
        return self._cancelled
    
    def cancel_operation(self): #vers 1
        """Cancel the operation"""
        self._cancelled = True


class ProgressManager: #vers 1
    """Manages progress dialogs and panels for IMG Factory"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.current_dialog = None
        self.embedded_panel = None
        self.worker_thread = None
    
    def setup_embedded_panel(self, parent_widget: QWidget) -> EmbeddedProgressPanel: #vers 1
        """Setup embedded progress panel"""
        self.embedded_panel = EmbeddedProgressPanel(parent_widget)
        self.embedded_panel.cancelled.connect(self._handle_embedded_cancel)
        return self.embedded_panel
    
    def show_modal_progress(self, title: str = "Processing", allow_cancel: bool = True) -> EnhancedProgressDialog: #vers 1
        """Show modal progress dialog"""
        self.current_dialog = EnhancedProgressDialog(title, self.main_window, allow_cancel)
        self.current_dialog.cancelled.connect(self._handle_dialog_cancel)
        return self.current_dialog
    
    def execute_with_modal_progress(self, operation_func: Callable, title: str = "Processing", 
                                   allow_cancel: bool = True, *args, **kwargs) -> bool: #vers 1
        """Execute operation with modal progress dialog"""
        try:
            # Show progress dialog
            dialog = self.show_modal_progress(title, allow_cancel)
            dialog.start_operation("Starting operation...")
            dialog.show()
            
            # Create and start worker thread
            self.worker_thread = ProgressWorkerThread(operation_func, *args, **kwargs)
            
            # Connect worker signals
            self.worker_thread.progress_updated.connect(dialog.update_progress)
            self.worker_thread.operation_completed.connect(dialog.complete_operation)
            
            # Connect cancellation
            if allow_cancel:
                dialog.cancelled.connect(self.worker_thread.cancel_operation)
            
            # Start operation
            self.worker_thread.start()
            
            # Execute dialog
            result = dialog.exec()
            
            # Wait for thread to finish
            if self.worker_thread.isRunning():
                self.worker_thread.wait(3000)  # Wait up to 3 seconds
            
            return result == QDialog.DialogCode.Accepted
            
        except Exception as e:
            if hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"❌ Progress execution failed: {str(e)}")
            return False
    
    def execute_with_embedded_progress(self, operation_func: Callable, title: str = "Processing", 
                                     *args, **kwargs) -> bool: #vers 1
        """Execute operation with embedded progress panel"""
        try:
            if not self.embedded_panel:
                return False
            
            # Start progress panel
            self.embedded_panel.start_operation(title)
            
            # Create and start worker thread  
            self.worker_thread = ProgressWorkerThread(operation_func, *args, **kwargs)
            
            # Connect worker signals
            self.worker_thread.progress_updated.connect(
                lambda p, m, d: self.embedded_panel.update_progress(p, m)
            )
            self.worker_thread.operation_completed.connect(self.embedded_panel.complete_operation)
            
            # Connect cancellation
            self.embedded_panel.cancelled.connect(self.worker_thread.cancel_operation)
            
            # Start operation
            self.worker_thread.start()
            
            return True
            
        except Exception as e:
            if hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"❌ Embedded progress failed: {str(e)}")
            return False
    
    def _handle_dialog_cancel(self): #vers 1
        """Handle modal dialog cancellation"""
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.cancel_operation()
    
    def _handle_embedded_cancel(self): #vers 1
        """Handle embedded panel cancellation"""
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.cancel_operation()


def create_progress_dialog(title: str = "Processing", parent=None, allow_cancel: bool = True) -> EnhancedProgressDialog: #vers 1
    """Create enhanced progress dialog"""
    return EnhancedProgressDialog(title, parent, allow_cancel)


def create_progress_panel(parent=None) -> EmbeddedProgressPanel: #vers 1
    """Create embedded progress panel"""
    return EmbeddedProgressPanel(parent)


def setup_progress_system(main_window) -> ProgressManager: #vers 1
    """Setup complete progress system for IMG Factory"""
    try:
        progress_manager = ProgressManager(main_window)
        main_window.progress_manager = progress_manager
        
        # Create embedded panel if GUI layout exists
        if hasattr(main_window, 'gui_layout'):
            # This should be added to the main GUI layout
            embedded_panel = progress_manager.setup_embedded_panel(main_window)
            # Store reference for layout integration
            main_window.embedded_progress_panel = embedded_panel
        
        return progress_manager
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Progress system setup failed: {str(e)}")
        return None


def integrate_with_existing_functions(main_window) -> bool: #vers 1
    """Integrate enhanced progress with existing progress_functions.py"""
    try:
        if not hasattr(main_window, 'progress_manager'):
            setup_progress_system(main_window)
        
        progress_manager = main_window.progress_manager
        
        # Enhanced wrapper functions
        def show_progress_dialog(title: str = "Processing", allow_cancel: bool = True):
            """Show modal progress dialog"""
            return progress_manager.show_modal_progress(title, allow_cancel)
        
        def update_progress(percentage: int, message: str = "", details: str = ""):
            """Update current progress display"""
            if progress_manager.current_dialog:
                progress_manager.current_dialog.update_progress(percentage, message, details)
            elif progress_manager.embedded_panel and progress_manager.embedded_panel.isVisible():
                progress_manager.embedded_panel.update_progress(percentage, message)
        
        def complete_progress(success: bool, message: str = ""):
            """Complete current progress operation"""
            if progress_manager.current_dialog:
                progress_manager.current_dialog.complete_operation(success, message)
            elif progress_manager.embedded_panel and progress_manager.embedded_panel.isVisible():
                progress_manager.embedded_panel.complete_operation(success, message)
        
        def execute_with_progress(operation_func: Callable, title: str = "Processing", 
                                modal: bool = True, allow_cancel: bool = True, *args, **kwargs):
            """Execute operation with progress (modal or embedded)"""
            if modal:
                return progress_manager.execute_with_modal_progress(
                    operation_func, title, allow_cancel, *args, **kwargs
                )
            else:
                return progress_manager.execute_with_embedded_progress(
                    operation_func, title, *args, **kwargs
                )
        
        # Add functions to main window
        main_window.show_progress_dialog = show_progress_dialog
        main_window.update_progress = update_progress  
        main_window.complete_progress = complete_progress
        main_window.execute_with_progress = execute_with_progress
        
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Progress integration failed: {str(e)}")
        return False


def batch_operation_progress(main_window, operations: list, title: str = "Batch Operation") -> bool: #vers 1
    """Execute multiple operations with unified progress tracking"""
    try:
        total_operations = len(operations)
        if total_operations == 0:
            return True
        
        # Show progress dialog
        dialog = main_window.show_progress_dialog(title, allow_cancel=True)
        dialog.start_operation(f"Processing {total_operations} operations...")
        dialog.show()
        
        completed_operations = 0
        failed_operations = 0
        
        for i, (operation_func, args, kwargs) in enumerate(operations):
            if dialog.is_cancelled():
                break
            
            operation_name = kwargs.get('operation_name', f'Operation {i+1}')
            
            # Update progress
            progress_percent = int((i / total_operations) * 100)
            dialog.update_progress(
                progress_percent,
                f"Executing: {operation_name}",
                f"Operation {i+1} of {total_operations}"
            )
            
            try:
                # Execute operation
                result = operation_func(*args, **kwargs)
                
                if result:
                    completed_operations += 1
                else:
                    failed_operations += 1
                    
            except Exception as e:
                failed_operations += 1
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"❌ {operation_name} failed: {str(e)}")
        
        # Complete progress
        if dialog.is_cancelled():
            dialog.complete_operation(False, "Batch operation cancelled")
            return False
        else:
            success = failed_operations == 0
            message = f"Completed: {completed_operations}, Failed: {failed_operations}"
            dialog.complete_operation(success, message)
            return success
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Batch operation failed: {str(e)}")
        return False_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(25)
        layout.addWidget(self.progress_bar)
        
        # Details label (optional)
        self.details_label = QLabel("")
        self.details_label.setWordWrap(True)
        self.details_label.setStyleSheet("color: #888; font-size: 10px;")
        layout.addWidget(self.details_label)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        if self._allow_cancel:
            self.cancel_button = QPushButton("Cancel Operation")
            self.cancel_button.clicked.connect(self._on_cancel_clicked)
            self.cancel_button.setFixedSize(120, 30)
            button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
    
    def _apply_styling(self): #vers 1
        """Apply modern styling to dialog"""
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                border: 1px solid #555;
            }
            QLabel {
                color: white;
                font-size: 12px;
            }
            QProgressBar {
                border: 1px solid #555;
                border-radius: 3px;
                background-color: #404040;
                color: white;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #0078d4;
                border-radius: 2px;
            }
            QPushButton {
                background-color: #3c3c3c;
                border: 1px solid #555;
                border-radius: 3px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4c4c4c;
            }
            QPushButton:pressed {
                background-color: #0078d4;
            }
        """)
    
    def start_operation(self, status_message: str = "Starting operation..."): #vers 1
        """Start the operation with initial status"""
        self._operation_running = True
        self._cancelled = False
        
        self.status_label.setText(status_message)
        self.progress_bar.setValue(0)
        self.details_label.setText("")
        
        if self._allow_cancel:
            self.cancel_button.setText("Cancel Operation")
            self.cancel_button.setEnabled(True)
    
    def update_progress(self, percentage: int, message: str = "", details: str = ""): #vers 1
        """Update progress bar and messages"""
        if self._cancelled:
            return
        
        # Clamp percentage to valid range
        percentage = max(0, min(100, percentage))
        
        self.progress_bar.setValue(percentage)
        
        if message:
            self.status_label.setText(message)
        
        if details:
            self.details_label.setText(details)
        
        # Force GUI update
        QApplication.processEvents()
    
    def complete_operation(self, success: bool, message: str = ""): #vers 1
        """Complete the operation"""
        self._operation_running = False
        
        if success:
            self.progress_bar.setValue(100)
            self.status_label.setText(message or "Operation completed successfully!")
            if self._allow_cancel:
                self.cancel_button.setText("Close")
        else:
            self.status_label.setText(message or "Operation failed!")
            if self._allow_cancel:
                self.cancel_button.setText("Close")
        
        self.operation_completed.emit(success, message)
        
        # Auto-close after short delay for successful operations
        if success:
            QTimer.singleShot(1500, self.accept)
    
    def _on_cancel_clicked(self): #vers 1
        """Handle cancel button click"""
        if self._operation_running and not self._cancelled:
            self._cancelled = True
            self.status_label.setText("Cancelling operation...")
            if self._allow_cancel:
                self.cancel_button.setText("Cancelling...")
                self.cancel_button.setEnabled(False)
            self.cancelled.emit()
        else:
            self.accept()
    
    def is_cancelled(self) -> bool: #vers 1
        """Check if operation was cancelled"""
        return self._cancelled
    
    def closeEvent(self, event): #vers 1
        """Handle dialog close event"""
        if self._operation_running and not self._cancelled:
            # Prevent closing during operation unless cancelled
            event.ignore()
            self._on_cancel_clicked()
        else:
            event.accept()


class EmbeddedProgressPanel(QFrame): #vers 1
    """Non-modal progress panel for embedding in main UI"""
    
    # Signals
    cancelled = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setVisible(False)  # Hidden by default
        self.setFixedHeight(80)
        
        self._cancelled = False
        self._operation_running = False
        
        self._setup_ui()
        self._apply_styling()
    
    def _setup_ui(self): #vers 1
        """Setup the panel UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(6)
        layout.setContentsMargins(10, 8, 10, 8)
        
        # Header with title and cancel button
        header_layout = QHBoxLayout()
        
        self.title_label = QLabel("Operation in Progress")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setFixedSize(70, 22)
        self.cancel_button.clicked.connect(self._on_cancel_clicked)
        header_layout.addWidget(self.cancel_button)
        
        layout.addLayout(header_layout)
        
        # Status and progress
        self.status_label = QLabel("Initializing...")
        self.status_label.setStyleSheet("font-size: 11px;")
        layout.addWidget(self.status_label)
        
        self.progress
