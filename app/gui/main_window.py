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
    QGroupBox, QCheckBox, QListWidget, QListWidgetItem, QSplitter,
    QTreeWidget, QTreeWidgetItem, QFrame, QGridLayout
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
    finished = pyqtSignal(str, list)  # results text, results data
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
            self.finished.emit(formatted, results)
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
        
        # Splitter for file list and output
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - File selection
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        
        # Title (moved to left panel)
        title_label = QLabel("🐍 Python Clean Code Linter")
        title_font = QFont("Segoe UI", 18, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        title_label.setStyleSheet("color: #7aa2f7; padding: 8px;")  # Tokyo Night accent color
        left_layout.addWidget(title_label)
        left_panel.setLayout(left_layout)
        
        # File selection group
        file_group = QGroupBox("📁 File Selection")
        file_group_layout = QVBoxLayout()
        
        # Buttons for file selection
        button_layout = QHBoxLayout()
        
        self.add_file_btn = QPushButton("Add File")
        self.add_file_btn.setProperty("variant", "accent")
        self.add_file_btn.clicked.connect(self.add_file)
        button_layout.addWidget(self.add_file_btn)
        
        self.add_folder_btn = QPushButton("Add Folder")
        self.add_folder_btn.setProperty("variant", "accent")
        self.add_folder_btn.clicked.connect(self.add_folder)
        button_layout.addWidget(self.add_folder_btn)
        
        self.clear_btn = QPushButton("Clear All")
        self.clear_btn.setProperty("variant", "danger")
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
        self.config_btn.setProperty("variant", "accent")
        self.config_btn.clicked.connect(self.open_config_dialog)
        action_layout.addWidget(self.config_btn)
        
        self.run_btn = QPushButton("▶️ Run Linter")
        self.run_btn.setProperty("variant", "success")
        self.run_btn.clicked.connect(self.run_linter)
        action_layout.addWidget(self.run_btn)
        
        left_layout.addLayout(action_layout)
        
        splitter.addWidget(left_panel)
        
        # Right panel - Results
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_panel.setLayout(right_layout)
        
        output_label = QLabel("📊 Analysis Results")
        output_font = QFont("Segoe UI", 12, QFont.Weight.Bold)
        output_label.setFont(output_font)
        output_label.setStyleSheet("color: #7aa2f7;")  # Tokyo Night accent color
        right_layout.addWidget(output_label)
        
        # Statistics panel
        stats_frame = QFrame()
        stats_frame.setFrameShape(QFrame.Shape.StyledPanel)
        stats_layout = QGridLayout()
        stats_frame.setLayout(stats_layout)
        
        # Create statistic labels
        self.stat_files = self.create_stat_widget("📁", "Files", "0")
        self.stat_violations = self.create_stat_widget("⚠️", "Violations", "0")
        self.stat_semantic = self.create_stat_widget("🔍", "Semantic", "0")
        self.stat_errors = self.create_stat_widget("❌", "Errors", "0")
        
        stats_layout.addWidget(self.stat_files, 0, 0)
        stats_layout.addWidget(self.stat_violations, 0, 1)
        stats_layout.addWidget(self.stat_semantic, 0, 2)
        stats_layout.addWidget(self.stat_errors, 0, 3)
        
        right_layout.addWidget(stats_frame)
        
        # Results tree
        self.results_tree = QTreeWidget()
        self.results_tree.setHeaderLabels(["Issue Type", "Location", "Description"])
        self.results_tree.setColumnWidth(0, 150)
        self.results_tree.setColumnWidth(1, 100)
        self.results_tree.setAlternatingRowColors(True)
        right_layout.addWidget(self.results_tree)
        
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
        """Apply Tokyo Night styling to the application"""
        # Load Tokyo Night stylesheet
        stylesheet_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'stylesheet',
            'tokyo_night.qss'
        )
        
        try:
            with open(stylesheet_path, 'r', encoding='utf-8') as f:
                stylesheet = f.read()
            self.setStyleSheet(stylesheet)
        except FileNotFoundError:
            print(f"Warning: Tokyo Night stylesheet not found at {stylesheet_path}")
            # Fallback to basic dark theme if stylesheet not found
            self.setStyleSheet("""
                QMainWindow { background-color: #161821; color: #c0caf5; }
                QPushButton { background-color: #2a2f45; color: #c0caf5; border-radius: 6px; padding: 6px 10px; }
            """)
    
    def create_stat_widget(self, icon, label, value):
        """Create a statistic display widget"""
        widget = QGroupBox()
        layout = QVBoxLayout()
        
        # Icon and value
        value_label = QLabel(f"{icon} {value}")
        value_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setStyleSheet("color: #7aa2f7;")
        value_label.setObjectName(f"stat_value_{label}")
        layout.addWidget(value_label)
        
        # Label
        name_label = QLabel(label)
        name_label.setFont(QFont("Segoe UI", 10))
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setStyleSheet("color: #9fb2ff;")
        layout.addWidget(name_label)
        
        widget.setLayout(layout)
        return widget
    
    def update_statistics(self, results_data):
        """Update statistics panel with results data"""
        total_files = len(results_data)
        total_violations = sum(len(r['listener_violations']) for r in results_data)
        total_semantic = sum(len([line for line in r['semantic_output'] 
                                   if '❌' in line or 'ERROR' in line]) 
                             for r in results_data)
        total_errors = sum(len(r['errors']) for r in results_data)
        
        # Update stat widgets
        self.update_stat_value(self.stat_files, "📁", total_files)
        self.update_stat_value(self.stat_violations, "⚠️", total_violations)
        self.update_stat_value(self.stat_semantic, "🔍", total_semantic)
        self.update_stat_value(self.stat_errors, "❌", total_errors)
    
    def update_stat_value(self, widget, icon, value):
        """Update a single stat widget value"""
        # Find the value label
        for child in widget.findChildren(QLabel):
            if child.objectName().startswith("stat_value"):
                child.setText(f"{icon} {value}")
                # Color code based on value
                if value == 0:
                    child.setStyleSheet("color: #9ece6a;")  # Green for zero
                elif value < 5:
                    child.setStyleSheet("color: #e0af68;")  # Yellow for few
                else:
                    child.setStyleSheet("color: #f7768e;")  # Red for many
                break
    
    def populate_results_tree(self, results_data):
        """Populate the results tree with linting data"""
        self.results_tree.clear()
        
        if not results_data:
            return
        
        for result in results_data:
            file_path = Path(result['file'])
            
            # Skip files with no issues
            if not (result['listener_violations'] or result['semantic_output'] or result['errors']):
                continue
            
            # Create file item
            file_item = QTreeWidgetItem(self.results_tree)
            file_item.setText(0, f"📄 {file_path.name}")
            file_item.setText(2, str(file_path))
            file_item.setExpanded(True)
            
            # Add listener violations
            if result['listener_violations']:
                violations_item = QTreeWidgetItem(file_item)
                violations_item.setText(0, "⚠️ Clean Code Violations")
                violations_item.setText(1, f"{len(result['listener_violations'])} issues")
                violations_item.setExpanded(True)
                
                for violation in result['listener_violations']:
                    # Parse violation to extract line number and message
                    violation_item = QTreeWidgetItem(violations_item)
                    
                    if '[Baris' in violation or 'Line' in violation:
                        # Extract line number
                        import re
                        line_match = re.search(r'\[Baris (\d+)\]|Line (\d+)', violation)
                        if line_match:
                            line_num = line_match.group(1) or line_match.group(2)
                            violation_item.setText(1, f"Line {line_num}")
                        
                        # Clean up message
                        msg = violation.replace('⚠️', '').strip()
                        msg = re.sub(r'\[Baris \d+\]', '', msg).strip()
                        
                        # Categorize
                        if 'Naming' in msg or 'snake_case' in msg or 'PascalCase' in msg:
                            violation_item.setText(0, "🏷️ Naming")
                        elif 'Kompleksitas' in msg or 'complexity' in msg.lower():
                            violation_item.setText(0, "🧩 Complexity")
                        elif 'Panjang' in msg or 'length' in msg.lower():
                            violation_item.setText(0, "📏 Length")
                        elif 'Argumen' in msg or 'parameter' in msg.lower():
                            violation_item.setText(0, "📝 Parameters")
                        elif 'Nesting' in msg or 'dalam' in msg.lower():
                            violation_item.setText(0, "📐 Nesting")
                        else:
                            violation_item.setText(0, "⚠️ Other")
                        
                        violation_item.setText(2, msg)
                    else:
                        violation_item.setText(0, "⚠️ Violation")
                        violation_item.setText(2, violation)
            
            # Add semantic issues
            if result['semantic_output']:
                semantic_issues = [line for line in result['semantic_output'] 
                                   if line.strip() and ('❌' in line or 'ERROR' in line)]
                
                if semantic_issues:
                    semantic_item = QTreeWidgetItem(file_item)
                    semantic_item.setText(0, "🔍 Semantic Analysis")
                    semantic_item.setText(1, f"{len(semantic_issues)} issues")
                    semantic_item.setExpanded(True)
                    
                    for issue in semantic_issues:
                        issue_item = QTreeWidgetItem(semantic_item)
                        issue_item.setText(0, "❌ Error")
                        
                        # Try to extract line info
                        clean_issue = issue.replace('❌', '').replace('[ERROR]', '').strip()
                        issue_item.setText(2, clean_issue)
            
            # Add parse errors
            if result['errors']:
                errors_item = QTreeWidgetItem(file_item)
                errors_item.setText(0, "🚫 Parse Errors")
                errors_item.setText(1, f"{len(result['errors'])} errors")
                errors_item.setExpanded(True)
                
                for error in result['errors']:
                    error_item = QTreeWidgetItem(errors_item)
                    error_item.setText(0, "❌ Error")
                    error_item.setText(2, error)
        
        # If no issues at all, show success message
        if self.results_tree.topLevelItemCount() == 0:
            success_item = QTreeWidgetItem(self.results_tree)
            success_item.setText(0, "✅ All Clear!")
            success_item.setText(2, "No issues found in any files")
            success_item.setForeground(0, QColor("#9ece6a"))
            success_item.setForeground(2, QColor("#9ece6a"))
    
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
        
        # Clear results
        self.results_tree.clear()
        
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
    
    def linter_finished(self, results_text, results_data):
        """Handle linter completion"""
        # Update statistics
        self.update_statistics(results_data)
        
        # Populate results tree
        self.populate_results_tree(results_data)
        
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
        self.results_tree.clear()
        error_item = QTreeWidgetItem(self.results_tree)
        error_item.setText(0, "❌ Error")
        error_item.setText(2, error_msg)
        
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
