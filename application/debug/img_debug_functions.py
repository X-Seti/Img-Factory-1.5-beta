#this belongs in root debug/img_debug_functions.py - Version: 1
# X-Seti - September12 2025 - IMG Factory 1.5 - IMG Debug Functions

"""
IMG Debug Functions - Compatibility layer for existing debug imports
Provides debug.img_debug_functions for old code that expects this import
Simple fallback system to prevent import errors
"""

import os
import sys

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
    """Simple IMG Debugger compatibility class"""
    
    def __init__(self):
        self.enabled = True
        self._col_debug_enabled = False
    
    def debug(self, message: str): #vers 1
        """Log debug message"""
        if self.enabled:
            print(f"[DEBUG] {message}")
    
    def info(self, message: str): #vers 1
        """Log info message"""
        if self.enabled:
            print(f"[INFO] {message}")
    
    def warning(self, message: str): #vers 1
        """Log warning message"""
        if self.enabled:
            print(f"[WARNING] {message}")
    
    def error(self, message: str): #vers 1
        """Log error message"""
        if self.enabled:
            print(f"[ERROR] {message}")
    
    def success(self, message: str): #vers 1
        """Log success message"""
        if self.enabled:
            print(f"[SUCCESS] {message}")


# Global debugger instance for compatibility
img_debugger = ImgDebugger()

# COL debug control functions
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

# Additional compatibility functions that some files might expect
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

# Export all the functions and classes
__all__ = [
    'img_debugger',
    'ImgDebugger',
    'set_col_debug_enabled',
    'is_col_debug_enabled',
    'debug',
    'info', 
    'warning',
    'error',
    'success'
]