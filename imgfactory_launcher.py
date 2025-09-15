#!/usr/bin/env python3
"""
#this belongs in root /launch_imgfactory.py - Version: 4
# X-Seti - September12 2025 - IMG Factory 1.5 - Main Application Launcher
"""

import sys
import os
import subprocess
from pathlib import Path
from typing import List, Tuple, Optional
import importlib.util

##Methods list -
# check_dependencies
# check_project_structure
# check_python_version
# install_missing_dependencies
# launch_application
# main
# print_header
# setup_python_path
# show_help

def print_header(): #vers 1
    """Print application header"""
    print("=" * 60)
    print("IMG Factory 1.5 - Python Edition")
    print("Advanced IMG Archive Management Tool")
    print("X-Seti - 2025")
    print("=" * 60)

def check_python_version() -> bool: #vers 1
    """Check Python version compatibility"""
    print("🐍 Checking Python version...")
    
    version = sys.version_info
    required = (3, 8)
    
    print(f"   Current: Python {version.major}.{version.minor}.{version.micro}")
    print(f"   Required: Python {required[0]}.{required[1]}+")
    
    if version >= required:
        print("   ✅ Python version OK")
        return True
    else:
        print(f"   ❌ Python {required[0]}.{required[1]}+ required")
        print(f"   Please upgrade Python to {required[0]}.{required[1]} or newer")
        return False

def check_dependencies() -> Tuple[bool, List[str]]: #vers 1
    """Check required Python dependencies"""
    print("📦 Checking dependencies...")
    
    dependencies = [
        ("PyQt6", "PyQt6.QtWidgets"),
        ("PyQt6.QtCore", "PyQt6.QtCore"), 
        ("PyQt6.QtGui", "PyQt6.QtGui")
    ]
    
    missing = []
    
    for name, module in dependencies:
        try:
            spec = importlib.util.find_spec(module)
            if spec is not None:
                print(f"   ✅ {name}")
            else:
                print(f"   ❌ {name} (not found)")
                missing.append(name)
        except ImportError:
            print(f"   ❌ {name} (import error)")
            missing.append(name)
    
    if not missing:
        print("   ✅ All dependencies satisfied")
        return True, []
    else:
        print(f"   ❌ Missing: {', '.join(missing)}")
        return False, missing

def check_project_structure() -> Tuple[bool, List[str]]: #vers 1
    """Check project file structure"""
    print("📁 Checking project structure...")
    
    current_dir = Path(__file__).parent
    application_dir = current_dir / "application"
    imgfactory_dir = application_dir / "tools" / "IMG_Factory"
    
    required_files = [
        "application/tools/IMG_Factory/imgfactory.py",
        "application/core/",
        "application/gui/"
    ]
    
    optional_files = [
        "application/tools/IMG_Factory/imgfactory.settings.json",
        "application/themes/",
        "application/debug/debug_system.py"
    ]
    
    missing_required = []
    found_optional = []
    
    # Check main imgfactory.py
    main_file = imgfactory_dir / "imgfactory.py"
    if main_file.exists():
        print(f"   ✅ application.tools/IMG_Factory/imgfactory.py")
    else:
        print(f"   ❌ application.tools/IMG_Factory/imgfactory.py (CRITICAL - main app missing)")
        missing_required.append("imgfactory.py")
    
    # Check required directories
    required_dirs = [
        (application_dir / "core", "core"),
        (application_dir / "gui", "gui")
    ]
    
    for dir_path, dir_name in required_dirs:
        if dir_path.exists() and dir_path.is_dir():
            file_count = len(list(dir_path.glob("*.py")))
            print(f"   ✅ application/{dir_name}/ ({file_count} Python files)")
        else:
            print(f"   ❌ application/{dir_name}/ (missing directory)")
            missing_required.append(f"application/{dir_name}/")
    
    # Check optional files and directories
    optional_checks = [
        (imgfactory_dir / "imgfactory.settings.json", "Settings file"),
        (application_dir / "themes", "Themes directory"),
        (application_dir / "debug" / "debug_system.py", "Debug system")
    ]
    
    for path, description in optional_checks:
        if path.exists():
            print(f"   ✅ {description}")
            found_optional.append(str(path))
        else:
            print(f"   ⚠️  {description} (optional)")
    
    if not missing_required:
        print("   ✅ Project structure OK")
        return True, found_optional
    else:
        print(f"   ❌ Missing required: {missing_required}")
        return False, missing_required

def setup_python_path(): #vers 1
    """Setup Python import paths for IMG Factory"""
    print("🛠️  Setting up Python paths...")
    
    current_dir = Path(__file__).parent
    application_dir = current_dir / "application"
    
    paths_to_add = [
        current_dir,  # Root directory
        application_dir,  # application directory
        application_dir / "tools" / "IMG_Factory",  # Main app directory
        application_dir / "core",  # Core functions
        application_dir / "gui",  # GUI components
        application_dir / "debug",  # Debug utilities
        application_dir / "themes"  # Theme files
    ]
    
    for path in paths_to_add:
        if path.exists() and str(path) not in sys.path:
            sys.path.insert(0, str(path))
            print(f"   ✅ Added {path.relative_to(current_dir)}")
        elif str(path) in sys.path:
            print(f"   ✅ Already in path: {path.relative_to(current_dir)}")
        else:
            print(f"   ⚠️  Skipped missing: {path.relative_to(current_dir)}")

def install_missing_dependencies(missing: List[str]) -> bool: #vers 1
    """Attempt to install missing dependencies"""
    print("🔧 Attempting to install missing dependencies...")
    
    # Map package names to pip install names
    pip_packages = {
        "PyQt6": "PyQt6",
        "PyQt6.QtCore": "PyQt6", 
        "PyQt6.QtGui": "PyQt6"
    }
    
    unique_packages = set()
    for pkg in missing:
        if pkg in pip_packages:
            unique_packages.add(pip_packages[pkg])
    
    if not unique_packages:
        print("   ❌ No packages to install")
        return False
    
    for package in unique_packages:
        print(f"   📦 Installing {package}...")
        try:
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", package
            ], capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                print(f"   ✅ {package} installed successfully")
            else:
                print(f"   ❌ {package} installation failed")
                print(f"      Error: {result.stderr.strip()}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"   ❌ {package} installation timed out")
            return False
        except Exception as e:
            print(f"   ❌ {package} installation error: {e}")
            return False
    
    print("   ✅ All packages installed successfully")
    return True

def launch_application() -> int: #vers 1
    """Launch the main IMG Factory application"""
    print("🚀 Launching IMG Factory...")
    
    try:
        # Navigate to the correct directory and import
        current_dir = Path(__file__).parent
        imgfactory_path = current_dir / "application" / "tools" / "IMG_Factory"
        
        # Change to IMG Factory directory
        os.chdir(imgfactory_path)
        
        # Import the main module
        sys.path.insert(0, str(imgfactory_path))
        import imgfactory
        print("   ✅ Main module imported successfully")
        
        # Create PyQt6 application
        from PyQt6.QtWidgets import QApplication
        
        app = QApplication(sys.argv)
        app.setApplicationName("IMG Factory")
        app.setApplicationVersion("1.5")
        app.setOrganizationName("X-Seti")
        
        # Create and show main window
        if hasattr(imgfactory, 'IMGFactory'):
            print("   ✅ Creating IMG Factory main window")
            window = imgfactory.IMGFactory()
            window.show()
        elif hasattr(imgfactory, 'main'):
            print("   ✅ Using main() function")
            return imgfactory.main()
        else:
            print("   ❌ No valid entry point found in imgfactory.py")
            return 1
        
        print("   ✅ IMG Factory started successfully")
        return app.exec()
        
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        print("   💡 This usually means missing dependencies or file structure issues")
        return 1
    except Exception as e:
        print(f"   ❌ Launch error: {e}")
        import traceback
        print("   📝 Full traceback:")
        traceback.print_exc()
        return 1

def show_help(): #vers 1
    """Show help information"""
    print("\n📚 Troubleshooting Help:")
    print("─" * 40)
    print("If IMG Factory won't start:")
    print("1. Ensure Python 3.8+ is installed")
    print("2. Install PyQt6: pip install PyQt6")
    print("3. Check all files are in application.tools/IMG_Factory/")
    print("4. Try running: python -m pip install --upgrade PyQt6")
    print("5. Run with verbose output: python -v launch_imgfactory.py")
    print("\n📧 For support: Check project documentation")
    print("🐛 Report bugs: Include the full error output above")

def main() -> int: #vers 1
    """Main launcher function"""
    print_header()
    
    # Step 1: Check Python version
    if not check_python_version():
        show_help()
        return 1
    
    print()
    
    # Step 2: Check dependencies
    deps_ok, missing_deps = check_dependencies()
    if not deps_ok:
        print(f"\n🔧 Attempting to install missing dependencies...")
        if install_missing_dependencies(missing_deps):
            print("   ✅ Dependencies installed, please restart the launcher")
            return 0
        else:
            print("   ❌ Failed to install dependencies")
            print("\n💡 Manual installation:")
            print("   pip install PyQt6")
            show_help()
            return 1
    
    print()
    
    # Step 3: Check project structure  
    structure_ok, found_files = check_project_structure()
    if not structure_ok:
        print("   ❌ Project structure issues detected")
        show_help()
        return 1
    
    print()
    
    # Step 4: Setup Python paths
    setup_python_path()
    
    print()
    
    # Step 5: Launch application
    exit_code = launch_application()
    
    # Step 6: Handle exit
    if exit_code == 0:
        print("\n✅ IMG Factory closed normally")
    else:
        print(f"\n❌ IMG Factory exited with error code: {exit_code}")
        show_help()
    
    return exit_code

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n🛑 Cancelled by user")
        sys.exit(130)  # Standard exit code for Ctrl+C
    except Exception as e:
        print(f"\n💥 Unexpected launcher error: {e}")
        import traceback
        traceback.print_exc()
        print("\n" + "="*60)
        show_help()
        sys.exit(1)
