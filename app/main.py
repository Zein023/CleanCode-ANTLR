"""
Python Clean Code Linter - Main Entry Point
A modern PyQt6 GUI application for linting Python code
"""
import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Set Fusion style for better Tokyo Night theme compatibility
    app.setStyle('Fusion')
    
    # Set application metadata
    app.setApplicationName("PyLinter")
    app.setApplicationVersion("1.0.0")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run application
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
