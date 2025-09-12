#this belongs in Shared/progress_functions.py - Version: 1
# X-Seti - September11 2025 - IMG Factory 1.5 - Unified Progress Functions

"""
Unified Progress Functions - Enhanced progress system combining existing progressbar_functions 
with img_editor_tool progress capabilities for consistent progress reporting across all operations
"""

import os
from typing import Optional, Callable, Any
from PyQt6.QtCore import QTimer, QObject, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QPushButton

##Methods list -
# show_progress
# update_progress
# hide_progress
# reset_progress
# create_progress_panel
# start_operation
# complete_operation
# cancel_operation
# get_progress_manager
# integrate_progress_system

##Classes -
# EnhancedProgressManager
# ProgressPanel

class ProgressPanel(QWidget): #vers 1
    """Enhanced progress panel from IMG Editor Tool with cancellation support"""
    
    cancelled = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._cancelled = False
        self._setup_ui()
    
    def _setup_ui(self): #vers 1
        """Setup progress panel UI"""
        self.setVisible(False)
        self.setMaximumHeight(80)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        # Title and status
        self.title_label = QLabel("Operation in Progress")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 10pt;")
        layout.addWidget(self.title_label)
        
        self.status_label = QLabel("Initializing...")
        layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)
        
        # Cancel button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self._on_cancel)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
    
    def start_operation(self, title: str = "Operation in Progress"): #vers 1
        """Start showing progress for an operation"""
        self._cancelled = False
        self.title_label.setText(title)
        self.status_label.setText("Initializing...")
        self.progress_bar.setValue(0)
        self.cancel_button.setEnabled(True)
        self.cancel_button.setText("Cancel")
        self.setVisible(True)
    
    def update_progress(self, percentage: int, message: str = None): #vers 1
        """Update progress percentage and message"""
        self.progress_bar.setValue(percentage)
        if message:
            self.status_label.setText(message)
    
    def set_status(self, message: str): #vers 1
        """Set status message without changing progress"""
        self.status_label.setText(message)
    
    def complete_operation(self, success: bool = True, message: str = None): #vers 1
        """Complete operation and auto-hide"""
        if success:
            self.progress_bar.setValue(100)
            if message:
                self.status_label.setText(message)
            # Auto-hide after 2 seconds
            QTimer.singleShot(2000, self.hide)
        else:
            if message:
                self.status_label.setText(message)
            # Hide immediately on failure
            QTimer.singleShot(500, self.hide)
    
    def is_cancelled(self) -> bool: #vers 1
        """Check if operation was cancelled"""
        return self._cancelled
    
    def _on_cancel(self): #vers 1
        """Handle cancel button click"""
        self._cancelled = True
        self.cancel_button.setEnabled(False)
        self.cancel_button.setText("Cancelling...")
        self.status_label.setText("Cancelling operation...")
        self.cancelled.emit()
    
    def hide(self): #vers 1
        """Hide progress panel"""
        self.setVisible(False)
        self._cancelled = False
    
    def reset(self): #vers 1
        """Reset to initial state"""
        self._cancelled = False
        self.title_label.setText("Operation in Progress")
        self.status_label.setText("Initializing...")
        self.progress_bar.setValue(0)
        self.cancel_button.setEnabled(True)
        self.cancel_button.setText("Cancel")
        self.setVisible(False)


class EnhancedProgressManager(QObject): #vers 1
    """Enhanced progress manager combining existing progressbar_functions with IMG Editor Tool capabilities"""
    
    operation_cancelled = pyqtSignal()
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.is_active = False
        self.current_operation = None
        self.progress_panel = None
        self.auto_reset_timer = QTimer()
        self.auto_reset_timer.timeout.connect(self._auto_reset)
        
        # Try to get existing progress manager
        try:
            from methods.progressbar_functions import get_progress_manager
            self.base_manager = get_progress_manager(main_window)
        except ImportError:
            self.base_manager = None
        
        # Create enhanced progress panel
        self._setup_progress_panel()
    
    def _setup_progress_panel(self): #vers 1
        """Setup enhanced progress panel if GUI layout available"""
        try:
            if hasattr(self.main_window, 'gui_layout'):
                self.progress_panel = ProgressPanel(self.main_window)
                self.progress_panel.cancelled.connect(self._on_operation_cancelled)
                
                # Try to add to GUI layout
                if hasattr(self.main_window.gui_layout, 'layout'):
                    self.main_window.gui_layout.layout().addWidget(self.progress_panel)
        except Exception as e:
            # Fallback - no enhanced panel
            pass
    
    def show_progress(self, value: int = 0, text: str = "Working...", auto_reset_ms: int = 30000, 
                     operation_title: str = None, cancellable: bool = False): #vers 1
        """Enhanced show progress with cancellation support"""
        try:
            self.is_active = True
            self.current_operation = text
            
            # Use enhanced panel if available and operation needs cancellation
            if self.progress_panel and (cancellable or operation_title):
                title = operation_title or "Operation in Progress"
                self.progress_panel.start_operation(title)
                self.progress_panel.update_progress(value, text)
            
            # Use base manager for standard progress
            elif self.base_manager:
                self.base_manager.show_progress(value, text, auto_reset_ms)
            
            # Fallback to main window methods
            elif hasattr(self.main_window, 'show_progress'):
                self.main_window.show_progress(text, 0, 100)
                if hasattr(self.main_window, 'update_progress'):
                    self.main_window.update_progress(value)
            
            # Final fallback to GUI layout
            elif hasattr(self.main_window, 'gui_layout') and hasattr(self.main_window.gui_layout, 'show_progress'):
                self.main_window.gui_layout.show_progress(value, text)
            
            # Setup auto-reset timer
            if auto_reset_ms > 0:
                self.auto_reset_timer.start(auto_reset_ms)
            
        except Exception as e:
            print(f"Enhanced progress show error: {e}")
    
    def update_progress(self, value: int, text: str = None): #vers 1
        """Enhanced update progress"""
        try:
            if not self.is_active:
                return
            
            # Update enhanced panel
            if self.progress_panel and self.progress_panel.isVisible():
                self.progress_panel.update_progress(value, text)
            
            # Update base manager
            elif self.base_manager:
                self.base_manager.update_progress(value, text)
            
            # Fallback to main window
            elif hasattr(self.main_window, 'update_progress'):
                self.main_window.update_progress(value)
                if text and hasattr(self.main_window, 'show_status'):
                    self.main_window.show_status(text)
            
            # Final fallback to GUI layout
            elif hasattr(self.main_window, 'gui_layout') and hasattr(self.main_window.gui_layout, 'show_progress'):
                self.main_window.gui_layout.show_progress(value, text or self.current_operation or "Working...")
            
        except Exception as e:
            print(f"Enhanced progress update error: {e}")
    
    def hide_progress(self, final_text: str = "Ready"): #vers 1
        """Enhanced hide progress"""
        try:
            self.is_active = False
            self.current_operation = None
            
            # Stop auto-reset timer
            if self.auto_reset_timer.isActive():
                self.auto_reset_timer.stop()
            
            # Hide enhanced panel
            if self.progress_panel and self.progress_panel.isVisible():
                self.progress_panel.hide()
            
            # Hide base manager progress
            if self.base_manager:
                self.base_manager.hide_progress(final_text)
            
            # Fallback to main window
            elif hasattr(self.main_window, 'hide_progress'):
                self.main_window.hide_progress()
                if hasattr(self.main_window, 'show_permanent_status'):
                    self.main_window.show_permanent_status(final_text)
            
            # Final fallback to GUI layout
            elif hasattr(self.main_window, 'gui_layout') and hasattr(self.main_window.gui_layout, 'show_progress'):
                self.main_window.gui_layout.show_progress(-1, final_text)
            
        except Exception as e:
            print(f"Enhanced progress hide error: {e}")
    
    def start_operation(self, title: str, cancellable: bool = False): #vers 1
        """Start a new operation with enhanced panel"""
        if self.progress_panel:
            self.progress_panel.start_operation(title)
        self.show_progress(0, "Initializing...", operation_title=title, cancellable=cancellable)
    
    def complete_operation(self, success: bool = True, message: str = None): #vers 1
        """Complete current operation"""
        if self.progress_panel and self.progress_panel.isVisible():
            self.progress_panel.complete_operation(success, message)
        else:
            final_message = message or ("Operation completed" if success else "Operation failed")
            self.hide_progress(final_message)
    
    def is_operation_cancelled(self) -> bool: #vers 1
        """Check if current operation was cancelled"""
        if self.progress_panel:
            return self.progress_panel.is_cancelled()
        return False
    
    def _on_operation_cancelled(self): #vers 1
        """Handle operation cancellation"""
        self.operation_cancelled.emit()
    
    def _auto_reset(self): #vers 1
        """Auto-reset progress if active too long"""
        if self.is_active:
            if hasattr(self.main_window, 'log_message'):
                self.main_window.log_message("⚠️ Progress auto-reset due to timeout")
            self.hide_progress("Ready")


# Global enhanced progress manager
_enhanced_progress_manager: Optional[EnhancedProgressManager] = None

def get_progress_manager(main_window) -> EnhancedProgressManager: #vers 1
    """Get or create enhanced progress manager"""
    global _enhanced_progress_manager
    if _enhanced_progress_manager is None:
        _enhanced_progress_manager = EnhancedProgressManager(main_window)
    return _enhanced_progress_manager

def show_progress(main_window, value: int = 0, text: str = "Working...", 
                 auto_reset_ms: int = 30000, operation_title: str = None, 
                 cancellable: bool = False): #vers 1
    """Enhanced show progress function
    
    Args:
        main_window: Main window instance
        value: Progress value (0-100)
        text: Status message
        auto_reset_ms: Auto-reset timeout (0 = disabled)
        operation_title: Title for enhanced progress panel
        cancellable: Whether operation can be cancelled
    """
    manager = get_progress_manager(main_window)
    manager.show_progress(value, text, auto_reset_ms, operation_title, cancellable)

def update_progress(main_window, value: int, text: str = None): #vers 1
    """Enhanced update progress function"""
    manager = get_progress_manager(main_window)
    manager.update_progress(value, text)

def hide_progress(main_window, final_text: str = "Ready"): #vers 1
    """Enhanced hide progress function"""
    manager = get_progress_manager(main_window)
    manager.hide_progress(final_text)

def reset_progress(main_window): #vers 1
    """Reset progress to ready state"""
    manager = get_progress_manager(main_window)
    manager.hide_progress("Ready")

def start_operation(main_window, title: str, cancellable: bool = False): #vers 1
    """Start operation with enhanced progress panel
    
    Args:
        main_window: Main window instance
        title: Operation title
        cancellable: Whether operation can be cancelled
    """
    manager = get_progress_manager(main_window)
    manager.start_operation(title, cancellable)

def complete_operation(main_window, success: bool = True, message: str = None): #vers 1
    """Complete current operation
    
    Args:
        main_window: Main window instance
        success: Whether operation succeeded
        message: Completion message
    """
    manager = get_progress_manager(main_window)
    manager.complete_operation(success, message)

def is_operation_cancelled(main_window) -> bool: #vers 1
    """Check if current operation was cancelled"""
    manager = get_progress_manager(main_window)
    return manager.is_operation_cancelled()

def create_progress_panel(parent=None) -> ProgressPanel: #vers 1
    """Create standalone progress panel"""
    return ProgressPanel(parent)

def integrate_progress_system(main_window) -> bool: #vers 1
    """Integrate enhanced progress system into main window"""
    try:
        # Create enhanced progress manager
        manager = get_progress_manager(main_window)
        
        # Add enhanced methods to main window
        main_window.show_progress_enhanced = lambda value=0, text="Working...", auto_reset=30000, title=None, cancellable=False: show_progress(main_window, value, text, auto_reset, title, cancellable)
        main_window.update_progress_enhanced = lambda value, text=None: update_progress(main_window, value, text)
        main_window.hide_progress_enhanced = lambda final_text="Ready": hide_progress(main_window, final_text)
        main_window.start_operation = lambda title, cancellable=False: start_operation(main_window, title, cancellable)
        main_window.complete_operation = lambda success=True, message=None: complete_operation(main_window, success, message)
        main_window.is_operation_cancelled = lambda: is_operation_cancelled(main_window)
        
        # Store manager reference
        main_window._enhanced_progress_manager = manager
        
        # Connect cancellation signal
        if hasattr(main_window, 'cancel_current_operation'):
            manager.operation_cancelled.connect(main_window.cancel_current_operation)
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("✅ Enhanced progress system integrated")
            main_window.log_message("   • Enhanced progress panel with cancellation")
            main_window.log_message("   • Backward compatibility with existing system")
            main_window.log_message("   • IMG Editor Tool progress integration")
        
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Enhanced progress integration failed: {str(e)}")
        return False

# Export functions
__all__ = [
    'EnhancedProgressManager',
    'ProgressPanel',
    'show_progress',
    'update_progress',
    'hide_progress',
    'reset_progress',
    'start_operation',
    'complete_operation',
    'is_operation_cancelled',
    'create_progress_panel',
    'get_progress_manager',
    'integrate_progress_system'
]