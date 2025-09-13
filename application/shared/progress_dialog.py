#this belongs in Shared/progress_dialog.py - Version: 1
# X-Seti - September12 2025 - IMG Factory 1.5 - Progress Dialog System

"""
Progress Dialog System - Ported from To_port/IMG_Editor/progress_dialog.py
Compatible with IMG Factory's GUI layout system and theming
Provides modal dialogs and embedded panels for long-running operations
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QProgressBar, QPushButton, QFrame, QApplication)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont

##Methods list -
# create_progress_dialog
# create_progress_panel
# integrate_progress_dialog_system
# _get_img_factory_theme
# _apply_img_factory_styling

##Classes -
# IMGProgressDialog
# IMGProgressPanel

def _get_img_factory_theme(): #vers 1
    """Get IMG Factory theme colors - compatible with existing theme system"""
    # Default dark theme colors that work with IMG Factory
    return {
        'background': '#2b2b2b',
        'border': '#404040',
        'text': 'white',
        'progress_bg': '#1e1e1e',
        'progress_chunk': '#0078d4',
        'button_bg': '#404040',
        'button_border': '#606060',
        'button_hover': '#505050',
        'button_pressed': '#303030',
        'spacing': 8,
        'border_radius': 4,
        'font_size': 12
    }


class IMGProgressDialog(QDialog): #vers 1
    """Modal progress dialog for IMG Factory operations - based on IMG Editor Tool"""
    
    # Signals
    cancelled = pyqtSignal()  # Emitted when user cancels the operation

    def __init__(self, title="Operation in Progress", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(400, 150)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowTitleHint)
        
        # Setup UI
        self._setup_ui()
        self._apply_styling()
        
        # State
        self._cancelled = False
        
    def _setup_ui(self): #vers 1
        """Setup the user interface"""
        theme = _get_img_factory_theme()
        
        layout = QVBoxLayout(self)
        layout.setSpacing(theme['spacing'])
        layout.setContentsMargins(theme['spacing'] * 2, theme['spacing'] * 2, 
                                 theme['spacing'] * 2, theme['spacing'] * 2)
        
        # Status label
        self.status_label = QLabel("Initializing...")
        self.status_label.setWordWrap(True)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # Cancel button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self._on_cancel_clicked)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
    def _apply_styling(self): #vers 1
        """Apply IMG Factory compatible styling"""
        theme = _get_img_factory_theme()
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {theme['background']};
                color: {theme['text']};
                border: 1px solid {theme['border']};
                border-radius: {theme['border_radius']}px;
            }}
            
            QLabel {{
                color: {theme['text']};
                font-size: {theme['font_size']}px;
                padding: {theme['spacing']}px;
            }}
            
            QProgressBar {{
                border: 1px solid {theme['border']};
                border-radius: {theme['border_radius']}px;
                background-color: {theme['progress_bg']};
                text-align: center;
                color: {theme['text']};
                font-size: {theme['font_size']}px;
            }}
            
            QProgressBar::chunk {{
                background-color: {theme['progress_chunk']};
                border-radius: {theme['border_radius']}px;
            }}
            
            QPushButton {{
                background-color: {theme['button_bg']};
                border: 1px solid {theme['button_border']};
                border-radius: {theme['border_radius']}px;
                color: {theme['text']};
                padding: {theme['spacing']}px {theme['spacing'] * 2}px;
                font-size: {theme['font_size']}px;
                min-width: 80px;
            }}
            
            QPushButton:hover {{
                background-color: {theme['button_hover']};
                border-color: #707070;
            }}
            
            QPushButton:pressed {{
                background-color: {theme['button_pressed']};
                border-color: #505050;
            }}
        """)
    
    def _on_cancel_clicked(self): #vers 1
        """Handle cancel button click"""
        self._cancelled = True
        self.cancel_button.setEnabled(False)
        self.cancel_button.setText("Cancelling...")
        self.cancelled.emit()
    
    def update_progress(self, percentage, message=None): #vers 1
        """Update the progress bar and status message
        
        Args:
            percentage: Progress percentage (0-100)
            message: Optional status message to display
        """
        self.progress_bar.setValue(percentage)
        if message:
            self.status_label.setText(message)
        
        # Process events to update UI
        QApplication.processEvents()
    
    def set_status(self, message): #vers 1
        """Set the status message without changing progress"""
        self.status_label.setText(message)
        QApplication.processEvents()
    
    def is_cancelled(self): #vers 1
        """Check if the operation was cancelled"""
        return self._cancelled
    
    def closeEvent(self, event): #vers 1
        """Handle dialog close event"""
        if self._cancelled:
            event.accept()
        else:
            # Prevent closing by clicking X - user must cancel
            event.ignore()


class IMGProgressPanel(QFrame): #vers 1
    """Non-modal progress panel for embedding in IMG Factory main UI"""
    
    # Signals
    cancelled = pyqtSignal()  # Emitted when user cancels the operation

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setVisible(False)  # Hidden by default
        self._setup_ui()
        self._apply_styling()
        
        # State
        self._cancelled = False
        
    def _setup_ui(self): #vers 1
        """Setup the user interface"""
        theme = _get_img_factory_theme()
        
        layout = QVBoxLayout(self)
        layout.setSpacing(theme['spacing'] // 2)
        layout.setContentsMargins(theme['spacing'], theme['spacing'], 
                                 theme['spacing'], theme['spacing'])
        
        # Header with title and cancel button
        header_layout = QHBoxLayout()
        
        self.title_label = QLabel("Operation in Progress")
        self.title_label.setFont(QFont('Arial', theme['font_size'] + 2, QFont.Weight.Bold))
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setFixedSize(60, 25)
        self.cancel_button.clicked.connect(self._on_cancel_clicked)
        header_layout.addWidget(self.cancel_button)
        
        layout.addLayout(header_layout)
        
        # Status label
        self.status_label = QLabel("Initializing...")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(20)
        layout.addWidget(self.progress_bar)
        
    def _apply_styling(self): #vers 1
        """Apply IMG Factory compatible styling"""
        theme = _get_img_factory_theme()
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {theme['background']};
                border: 1px solid {theme['border']};
                border-radius: {theme['border_radius']}px;
                padding: {theme['spacing']}px;
            }}
            
            QLabel {{
                color: {theme['text']};
                font-size: {theme['font_size']}px;
                background: transparent;
            }}
            
            QProgressBar {{
                border: 1px solid {theme['border']};
                border-radius: {theme['border_radius']}px;
                background-color: {theme['progress_bg']};
                text-align: center;
                color: {theme['text']};
                font-size: {theme['font_size']}px;
            }}
            
            QProgressBar::chunk {{
                background-color: {theme['progress_chunk']};
                border-radius: {theme['border_radius']}px;
            }}
            
            QPushButton {{
                background-color: {theme['button_bg']};
                border: 1px solid {theme['button_border']};
                border-radius: {theme['border_radius']}px;
                color: {theme['text']};
                font-size: {theme['font_size'] - 2}px;
            }}
            
            QPushButton:hover {{
                background-color: {theme['button_hover']};
            }}
            
            QPushButton:pressed {{
                background-color: {theme['button_pressed']};
            }}
        """)
    
    def _on_cancel_clicked(self): #vers 1
        """Handle cancel button click"""
        self._cancelled = True
        self.cancel_button.setEnabled(False)
        self.cancel_button.setText("...")
        self.cancelled.emit()
    
    def start_operation(self, title="Operation in Progress"): #vers 1
        """Start a new operation and show the panel"""
        self._cancelled = False
        self.title_label.setText(title)
        self.status_label.setText("Initializing...")
        self.progress_bar.setValue(0)
        self.cancel_button.setEnabled(True)
        self.cancel_button.setText("Cancel")
        self.setVisible(True)
    
    def update_progress(self, percentage, message=None): #vers 1
        """Update the progress bar and status message
        
        Args:
            percentage: Progress percentage (0-100)
            message: Optional status message to display
        """
        self.progress_bar.setValue(percentage)
        if message:
            self.status_label.setText(message)
    
    def set_status(self, message): #vers 1
        """Set the status message without changing progress"""
        self.status_label.setText(message)
    
    def complete_operation(self, success=True, message=None): #vers 1
        """Complete the operation and hide the panel"""
        if success:
            self.progress_bar.setValue(100)
            if message:
                self.status_label.setText(message)
            
            # Auto-hide after a short delay
            QTimer.singleShot(2000, self.hide)
        else:
            if message:
                self.status_label.setText(message)
            # Hide immediately on failure
            QTimer.singleShot(500, self.hide)
    
    def is_cancelled(self): #vers 1
        """Check if the operation was cancelled"""
        return self._cancelled
    
    def hide(self): #vers 1
        """Hide the progress panel"""
        self.setVisible(False)
        self._cancelled = False
    
    def reset(self): #vers 1
        """Reset the progress panel to initial state"""
        self._cancelled = False
        self.title_label.setText("Operation in Progress")
        self.status_label.setText("Initializing...")
        self.progress_bar.setValue(0)
        self.cancel_button.setEnabled(True)
        self.cancel_button.setText("Cancel")
        self.setVisible(False)


def create_progress_dialog(title="Operation in Progress", parent=None): #vers 1
    """Create a modal progress dialog for IMG Factory"""
    return IMGProgressDialog(title, parent)


def create_progress_panel(parent=None): #vers 1
    """Create an embedded progress panel for IMG Factory"""
    return IMGProgressPanel(parent)


def integrate_progress_dialog_system(main_window): #vers 1
    """Integrate progress dialog system into IMG Factory main window"""
    try:
        # Create progress panel for embedding in GUI
        if hasattr(main_window, 'gui_layout'):
            progress_panel = create_progress_panel(main_window)
            main_window.progress_panel = progress_panel
            
            # Try to add to GUI layout if it has a container
            if hasattr(main_window.gui_layout, 'main_splitter'):
                # Add to the main layout - this will be integrated with GUI layout
                main_window.embedded_progress_panel = progress_panel
        
        # Add convenience methods to main window
        main_window.create_progress_dialog = lambda title="Processing": create_progress_dialog(title, main_window)
        main_window.create_progress_panel = lambda: create_progress_panel(main_window)
        
        # Add show/hide progress methods compatible with existing system
        def show_progress_dialog(title="Processing"):
            dialog = main_window.create_progress_dialog(title)
            dialog.show()
            return dialog
        
        def show_progress_panel(title="Processing"):
            if hasattr(main_window, 'progress_panel'):
                main_window.progress_panel.start_operation(title)
                return main_window.progress_panel
            return None
        
        main_window.show_progress_dialog = show_progress_dialog
        main_window.show_progress_panel = show_progress_panel
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("✅ Progress dialog system integrated")
            main_window.log_message("   • Modal progress dialogs")
            main_window.log_message("   • Embedded progress panels")
            main_window.log_message("   • IMG Factory theme compatible")
        
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Progress dialog integration failed: {str(e)}")
        return False


# Export functions
__all__ = [
    'IMGProgressDialog',
    'IMGProgressPanel',
    'create_progress_dialog',
    'create_progress_panel',
    'integrate_progress_dialog_system'
]