"""
Main Window for Python Linter GUI
Modern PyQt6 interface for code linting
"""
import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTextEdit, QLabel, QFileDialog, QProgressBar, QMessageBox,
    QGroupBox, QCheckBox, QListWidget, QListWidgetItem, QSplitter
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QIcon, QPalette, QColor

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from gui.config_manager import ConfigManager
from gui.linter_runner import LinterRunner
from gui.config_dialog import ConfigDialog

class LinterThread(QThread):
    """Thread for running linter without blocking UI"""
    
    progress = pyqtSignal(int, int, str)  # current, total, filename
    finished = pyqtSignal(str)  # results
    error = pyqtSignal(str)  # error message
    
    def __init__(self, linter_runner, file_paths, use_listener, use_semantic):
        super().__init__()
        self.linter_runner = linter_runner
        self.file_paths = file_paths
        self.use_listener = use_listener
        self.use_semantic = use_semantic
    
    def run(self):
        """Run linter in separate thread"""
        try:
            results = self.linter_runner.lint_files(
                self.file_paths,
                self.use_listener,
                self.use_semantic,
                progress_callback=self.progress.emit
            )
            formatted = self.linter_runner.format_results(results)
            self.finished.emit(formatted)
        except Exception as e:
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.linter_runner = LinterRunner(self.config_manager.get_config())
        self.selected_paths = []
        self.linter_thread = None
        
        self.init_ui()
        self.apply_modern_style()
    
    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle("Python Clean Code Linter")
        self.setGeometry(100, 100, 1200, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Title
        title_label = QLabel("🐍 Python Clean Code Linter")
        title_font = QFont("Segoe UI", 20, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Splitter for file list and output
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - File selection
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)
        
        # File selection group
        file_group = QGroupBox("📁 File Selection")
        file_group_layout = QVBoxLayout()
        
        # Buttons for file selection
        button_layout = QHBoxLayout()
        
        self.add_file_btn = QPushButton("Add File")
        self.add_file_btn.clicked.connect(self.add_file)
        button_layout.addWidget(self.add_file_btn)
        
        self.add_folder_btn = QPushButton("Add Folder")
        self.add_folder_btn.clicked.connect(self.add_folder)
        button_layout.addWidget(self.add_folder_btn)
        
        self.clear_btn = QPushButton("Clear All")
        self.clear_btn.clicked.connect(self.clear_files)
        button_layout.addWidget(self.clear_btn)
        
        file_group_layout.addLayout(button_layout)
        
        # List of selected files
        self.file_list = QListWidget()
        file_group_layout.addWidget(self.file_list)
        
        file_group.setLayout(file_group_layout)
        left_layout.addWidget(file_group)
        
        # Linter options
        options_group = QGroupBox("⚙️ Linter Options")
        options_layout = QVBoxLayout()
        
        self.listener_check = QCheckBox("Use Listener-based Linter")
        self.listener_check.setChecked(True)
        options_layout.addWidget(self.listener_check)
        
        self.semantic_check = QCheckBox("Use Semantic Visitor Linter")
        self.semantic_check.setChecked(True)
        options_layout.addWidget(self.semantic_check)
        
        options_group.setLayout(options_layout)
        left_layout.addWidget(options_group)
        
        # Action buttons
        action_layout = QHBoxLayout()
        
        self.config_btn = QPushButton("⚙️ Configuration")
        self.config_btn.clicked.connect(self.open_config_dialog)
        action_layout.addWidget(self.config_btn)
        
        self.run_btn = QPushButton("▶️ Run Linter")
        self.run_btn.clicked.connect(self.run_linter)
        action_layout.addWidget(self.run_btn)
        
        left_layout.addLayout(action_layout)
        
        splitter.addWidget(left_panel)
        
        # Right panel - Output
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_panel.setLayout(right_layout)
        
        output_label = QLabel("📋 Linter Output")
        output_font = QFont("Segoe UI", 12, QFont.Weight.Bold)
        output_label.setFont(output_font)
        right_layout.addWidget(output_label)
        
        # Output text area
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setFont(QFont("Consolas", 10))
        right_layout.addWidget(self.output_text)
        
        splitter.addWidget(right_panel)
        
        # Set splitter sizes (40% left, 60% right)
        splitter.setSizes([400, 800])
        
        main_layout.addWidget(splitter)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Status bar
        self.statusBar().showMessage("Ready")
    
    def apply_modern_style(self):
        """Apply modern styling to the application"""
        style = """
        QMainWindow {
            background-color: #f5f5f5;
        }
        
        QGroupBox {
            font-weight: bold;
            border: 2px solid #3498db;
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 10px;
            background-color: white;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }
        
        QPushButton {
            background-color: #3498db;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
            min-height: 30px;
        }
        
        QPushButton:hover {
            background-color: #2980b9;
        }
        
        QPushButton:pressed {
            background-color: #21618c;
        }
        
        QPushButton#run_btn {
            background-color: #27ae60;
        }
        
        QPushButton#run_btn:hover {
            background-color: #229954;
        }
        
        QTextEdit {
            border: 1px solid #bdc3c7;
            border-radius: 4px;
            padding: 8px;
            background-color: white;
        }
        
        QListWidget {
            border: 1px solid #bdc3c7;
            border-radius: 4px;
            background-color: white;
        }
        
        QCheckBox {
            spacing: 8px;
            font-size: 11pt;
        }
        
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
        }
        
        QProgressBar {
            border: 1px solid #bdc3c7;
            border-radius: 4px;
            text-align: center;
            background-color: white;
        }
        
        QProgressBar::chunk {
            background-color: #3498db;
            border-radius: 3px;
        }
        
        QStatusBar {
            background-color: #ecf0f1;
            color: #2c3e50;
        }
        """
        
        self.setStyleSheet(style)
        self.run_btn.setObjectName("run_btn")
    
    def add_file(self):
        """Add a single Python file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Python File",
            "",
            "Python Files (*.py)"
        )
        
        if file_path:
            path = Path(file_path)
            exclude_patterns = self.config_manager.get_exclude_patterns()
            
            # Check if should be excluded
            if not self.linter_runner._should_exclude(path, exclude_patterns):
                if path not in self.selected_paths:
                    self.selected_paths.append(path)
                    self.file_list.addItem(str(path))
                    self.statusBar().showMessage(f"Added: {path.name}")
            else:
                QMessageBox.warning(
                    self,
                    "File Excluded",
                    f"File matches exclude pattern and was not added."
                )
    
    def add_folder(self):
        """Add all Python files from a folder recursively"""
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Select Folder"
        )
        
        if folder_path:
            exclude_patterns = self.config_manager.get_exclude_patterns()
            python_files = self.linter_runner.find_python_files(
                folder_path,
                exclude_patterns
            )
            
            added_count = 0
            for file_path in python_files:
                if file_path not in self.selected_paths:
                    self.selected_paths.append(file_path)
                    self.file_list.addItem(str(file_path))
                    added_count += 1
            
            self.statusBar().showMessage(
                f"Added {added_count} Python file(s) from {Path(folder_path).name}"
            )
            
            if added_count == 0:
                QMessageBox.information(
                    self,
                    "No Files Added",
                    "No Python files found or all files are excluded."
                )
    
    def clear_files(self):
        """Clear all selected files"""
        self.selected_paths.clear()
        self.file_list.clear()
        self.statusBar().showMessage("Cleared all files")
    
    def open_config_dialog(self):
        """Open configuration dialog"""
        dialog = ConfigDialog(self.config_manager, self)
        if dialog.exec():
            # Reload configuration
            self.linter_runner = LinterRunner(self.config_manager.get_config())
            self.statusBar().showMessage("Configuration updated")
    
    def run_linter(self):
        """Run the linter on selected files"""
        if not self.selected_paths:
            QMessageBox.warning(
                self,
                "No Files Selected",
                "Please add files or folders to lint."
            )
            return
        
        if not self.listener_check.isChecked() and not self.semantic_check.isChecked():
            QMessageBox.warning(
                self,
                "No Linter Selected",
                "Please select at least one linter option."
            )
            return
        
        # Disable buttons during linting
        self.run_btn.setEnabled(False)
        self.add_file_btn.setEnabled(False)
        self.add_folder_btn.setEnabled(False)
        self.config_btn.setEnabled(False)
        
        # Show progress bar
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Clear output
        self.output_text.clear()
        self.output_text.append("🔍 Running linter...\n")
        
        # Start linter thread
        self.linter_thread = LinterThread(
            self.linter_runner,
            self.selected_paths,
            self.listener_check.isChecked(),
            self.semantic_check.isChecked()
        )
        
        self.linter_thread.progress.connect(self.update_progress)
        self.linter_thread.finished.connect(self.linter_finished)
        self.linter_thread.error.connect(self.linter_error)
        
        self.linter_thread.start()
        self.statusBar().showMessage("Linting in progress...")
    
    def update_progress(self, current, total, filename):
        """Update progress bar"""
        progress = int((current / total) * 100)
        self.progress_bar.setValue(progress)
        self.statusBar().showMessage(f"Processing {current}/{total}: {Path(filename).name}")
    
    def linter_finished(self, results):
        """Handle linter completion"""
        self.output_text.clear()
        self.output_text.append(results)
        
        # Re-enable buttons
        self.run_btn.setEnabled(True)
        self.add_file_btn.setEnabled(True)
        self.add_folder_btn.setEnabled(True)
        self.config_btn.setEnabled(True)
        
        # Hide progress bar
        self.progress_bar.setVisible(False)
        
        self.statusBar().showMessage("Linting completed")
        
        # Show completion message
        QMessageBox.information(
            self,
            "Linting Complete",
            f"Analyzed {len(self.selected_paths)} file(s).\nCheck output for details."
        )
    
    def linter_error(self, error_msg):
        """Handle linter error"""
        self.output_text.clear()
        self.output_text.append(f"❌ Error occurred:\n{error_msg}")
        
        # Re-enable buttons
        self.run_btn.setEnabled(True)
        self.add_file_btn.setEnabled(True)
        self.add_folder_btn.setEnabled(True)
        self.config_btn.setEnabled(True)
        
        # Hide progress bar
        self.progress_bar.setVisible(False)
        
        self.statusBar().showMessage("Error occurred")
        
        QMessageBox.critical(
            self,
            "Error",
            f"An error occurred during linting:\n{error_msg}"
        )
