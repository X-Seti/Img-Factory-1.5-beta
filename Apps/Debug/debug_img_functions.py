#this belongs in Apps/Debug/img_debug_functions.py - Version: 1
# X-Seti - September12 2025 - IMG Factory 1.5 - IMG Debug Functions

"""
IMG Debug Functions - Clean debug system for IMG Factory
Provides img_debugger and COL debug functionality
Simple, reliable debug output system
"""

import os
import sys
import time
from datetime import datetime
from typing import Optional

##Methods list -
# debug
# error
# info
# success  
# warning
# set_col_debug_enabled
# is_col_debug_enabled

##Classes -
# ImgDebugger

class ImgDebugger: #vers 1
    """Clean IMG Debugger with formatted output"""
    
    def __init__(self, enabled=True):
        self.enabled = enabled
        self._col_debug_enabled = False
        self.session_start = datetime.now()
        
        # Create logs directory if needed
        self.logs_dir = "logs"
        if not os.path.exists(self.logs_dir):
            try:
                os.makedirs(self.logs_dir)
            except:
                pass  # Continue without logging if can't create dir
        
        # Optional log file
        self.log_file = None
        try:
            log_filename = f"debug_{self.session_start.strftime('%Y%m%d_%H%M%S')}.log"
            self.log_file = os.path.join(self.logs_dir, log_filename)
        except:
            pass  # Continue without file logging if fails
    
    def _log_to_file(self, level: str, message: str): #vers 1
        """Log message to file if possible"""
        if not self.log_file:
            return
        
        try:
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            log_entry = f"[{timestamp}] [{level}] {message}\n"
            
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except:
            pass  # Continue silently if file logging fails
    
    def _format_message(self, level: str, message: str) -> str: #vers 1
        """Format message with timestamp and level"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        return f"[{timestamp}] [{level}] {message}"
    
    def debug(self, message: str): #vers 1
        """Log debug message"""
        if self.enabled:
            formatted = self._format_message("DEBUG", message)
            print(formatted)
            self._log_to_file("DEBUG", message)
    
    def info(self, message: str): #vers 1
        """Log info message"""
        if self.enabled:
            formatted = self._format_message("INFO", message)
            print(formatted)
            self._log_to_file("INFO", message)
    
    def warning(self, message: str): #vers 1
        """Log warning message"""
        if self.enabled:
            formatted = self._format_message("WARNING", message)
            print(formatted)
            self._log_to_file("WARNING", message)
    
    def error(self, message: str): #vers 1
        """Log error message"""
        if self.enabled:
            formatted = self._format_message("ERROR", message)
            print(formatted)
            self._log_to_file("ERROR", message)
    
    def success(self, message: str): #vers 1
        """Log success message"""
        if self.enabled:
            formatted = self._format_message("SUCCESS", f"✅ {message}")
            print(formatted)
            self._log_to_file("SUCCESS", message)
    
    def set_enabled(self, enabled: bool): #vers 1
        """Enable or disable debug output"""
        self.enabled = enabled
        if enabled:
            self.info("Debug output enabled")
        else:
            print("[INFO] Debug output disabled")


# Global debugger instance
img_debugger = ImgDebugger()

# COL debug control
_col_debug_enabled = False

def set_col_debug_enabled(enabled: bool): #vers 1
    """Enable/disable COL debug output"""
    global _col_debug_enabled
    _col_debug_enabled = enabled
    img_debugger._col_debug_enabled = enabled
    
    if enabled:
        img_debugger.info("COL debug output enabled")
    else:
        img_debugger.info("COL debug output disabled")

def is_col_debug_enabled() -> bool: #vers 1
    """Check if COL debug is enabled"""
    return _col_debug_enabled

# Direct debug functions for compatibility
def debug(message: str): #vers 1
    """Direct debug function"""
    img_debugger.debug(message)

def info(message: str): #vers 1
    """Direct info function"""
    img_debugger.info(message)

def warning(message: str): #vers 1
    """Direct warning function"""
    img_debugger.warning(message)

def error(message: str): #vers 1
    """Direct error function"""
    img_debugger.error(message)

def success(message: str): #vers 1
    """Direct success function"""
    img_debugger.success(message)

# Debug control functions
def enable_debug(): #vers 1
    """Enable debug output"""
    img_debugger.set_enabled(True)

def disable_debug(): #vers 1
    """Disable debug output"""
    img_debugger.set_enabled(False)

def is_debug_enabled() -> bool: #vers 1
    """Check if debug is enabled"""
    return img_debugger.enabled

# Export all functions and classes
__all__ = [
    'img_debugger',
    'ImgDebugger',
    'set_col_debug_enabled',
    'is_col_debug_enabled',
    'debug',
    'info',
    'warning', 
    'error',
    'success',
    'enable_debug',
    'disable_debug',
    'is_debug_enabled'
]