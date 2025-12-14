"""
Configuration Dialog for Python Linter
Allows editing of linter configuration settings
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
    QSpinBox, QComboBox, QPushButton, QGroupBox, QListWidget,
    QLineEdit, QMessageBox, QTabWidget, QWidget, QCheckBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class ConfigDialog(QDialog):
    """Dialog for editing configuration"""
    
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.config = config_manager.get_config().copy()
        
        self.init_ui()
        self.load_config_values()
    
    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle("Linter Configuration")
        self.setGeometry(200, 200, 600, 500)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Title
        title = QLabel("⚙️ Linter Configuration")
        title_font = QFont("Segoe UI", 14, QFont.Weight.Bold)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #7aa2f7;")  # Tokyo Night accent color
        layout.addWidget(title)
        
        # Tab widget for different config sections
        tabs = QTabWidget()
        
        # Metrics tab
        metrics_tab = self.create_metrics_tab()
        tabs.addTab(metrics_tab, "📊 Metrics")
        
        # Naming tab
        naming_tab = self.create_naming_tab()
        tabs.addTab(naming_tab, "📝 Naming")
        
        # Semantic tab
        semantic_tab = self.create_semantic_tab()
        tabs.addTab(semantic_tab, "🔍 Semantic")
        
        # Exclusions tab
        exclusions_tab = self.create_exclusions_tab()
        tabs.addTab(exclusions_tab, "🚫 Exclusions")
        
        layout.addWidget(tabs)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.reset_btn = QPushButton("Reset to Defaults")
        self.reset_btn.clicked.connect(self.reset_to_defaults)
        button_layout.addWidget(self.reset_btn)
        
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_config)
        button_layout.addWidget(self.save_btn)
        
        layout.addLayout(button_layout)
        
        self.apply_style()
    
    def create_metrics_tab(self):
        """Create metrics configuration tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # Metrics group
        metrics_group = QGroupBox("Code Metrics Limits")
        metrics_layout = QFormLayout()
        
        # Max function lines
        self.max_lines_spin = QSpinBox()
        self.max_lines_spin.setRange(1, 1000)
        self.max_lines_spin.setSuffix(" lines")
        metrics_layout.addRow("Max Function Lines:", self.max_lines_spin)
        
        # Max nesting depth
        self.max_depth_spin = QSpinBox()
        self.max_depth_spin.setRange(1, 20)
        self.max_depth_spin.setSuffix(" levels")
        metrics_layout.addRow("Max Nesting Depth:", self.max_depth_spin)
        
        # Max arguments
        self.max_args_spin = QSpinBox()
        self.max_args_spin.setRange(1, 20)
        self.max_args_spin.setSuffix(" args")
        metrics_layout.addRow("Max Function Arguments:", self.max_args_spin)
        
        # Max cyclomatic complexity
        self.max_complexity_spin = QSpinBox()
        self.max_complexity_spin.setRange(1, 50)
        metrics_layout.addRow("Max Cyclomatic Complexity:", self.max_complexity_spin)
        
        metrics_group.setLayout(metrics_layout)
        layout.addWidget(metrics_group)

        # Parser/Lexer Errors toggle
        errors_group = QGroupBox("Parser/Lexer Error Reporting")
        errors_layout = QVBoxLayout()
        self.parser_errors_checkbox = QCheckBox("Capture parser/lexer syntax errors")
        errors_layout.addWidget(self.parser_errors_checkbox)
        help_errors = QLabel("When enabled, syntax errors from the ANTLR lexer/parser will be collected and shown under Errors.")
        help_errors.setWordWrap(True)
        help_errors.setStyleSheet("color: #7f8c8d; padding: 6px;")
        errors_layout.addWidget(help_errors)
        errors_group.setLayout(errors_layout)
        layout.addWidget(errors_group)
        
        # Help text
        help_text = QLabel(
            "These metrics help identify overly complex code:\n"
            "• Function Lines: Total lines in a function\n"
            "• Nesting Depth: How deep code blocks are nested\n"
            "• Arguments: Number of parameters a function accepts\n"
            "• Cyclomatic Complexity: Measure of code complexity"
        )
        help_text.setWordWrap(True)
        help_text.setStyleSheet("color: #7f8c8d; padding: 10px;")
        layout.addWidget(help_text)
        
        layout.addStretch()
        
        return tab
    
    def create_naming_tab(self):
        """Create naming convention configuration tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # Naming group
        naming_group = QGroupBox("Naming Conventions")
        naming_layout = QFormLayout()
        
        # Function naming
        self.func_naming_combo = QComboBox()
        self.func_naming_combo.addItems(["none", "snake_case", "camelCase", "PascalCase"])
        naming_layout.addRow("Function Names:", self.func_naming_combo)
        
        # Class naming
        self.class_naming_combo = QComboBox()
        self.class_naming_combo.addItems(["none", "PascalCase", "snake_case", "camelCase"])
        naming_layout.addRow("Class Names:", self.class_naming_combo)
        
        # Variable naming
        self.var_naming_combo = QComboBox()
        self.var_naming_combo.addItems(["none", "snake_case", "camelCase", "PascalCase"])
        naming_layout.addRow("Variable Names:", self.var_naming_combo)
        
        naming_group.setLayout(naming_layout)
        layout.addWidget(naming_group)
        
        # Examples
        examples = QLabel(
            "Naming Convention Examples:\n\n"
            "• none: Any naming style allowed (no checks)\n"
            "• snake_case: my_function_name\n"
            "• camelCase: myFunctionName\n"
            "• PascalCase: MyFunctionName"
        )
        examples.setWordWrap(True)
        examples.setStyleSheet("color: #7f8c8d; padding: 10px;")
        layout.addWidget(examples)
        
        layout.addStretch()
        
        return tab
    
    def create_semantic_tab(self):
        """Create semantic checker configuration tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # Semantic checker group
        semantic_group = QGroupBox("Semantic Checker Settings")
        semantic_layout = QVBoxLayout()
        
        # Ignore PascalCase
        self.ignore_pascalcase_check = QCheckBox("Ignore Undefined PascalCase Names")
        self.ignore_pascalcase_check.setToolTip(
            "When enabled, PascalCase identifiers (e.g., MyClass, MyFunction) "
            "won't be reported as undefined, assuming they're from external libraries"
        )
        semantic_layout.addWidget(self.ignore_pascalcase_check)
        
        # Ignore UPPERCASE
        self.ignore_uppercase_check = QCheckBox("Ignore Undefined UPPERCASE Names")
        self.ignore_uppercase_check.setToolTip(
            "When enabled, UPPERCASE identifiers (e.g., MY_CONSTANT, API_KEY) "
            "won't be reported as undefined"
        )
        semantic_layout.addWidget(self.ignore_uppercase_check)
        
        # Strict import tracking
        self.strict_import_check = QCheckBox("Strict Import Tracking")
        self.strict_import_check.setChecked(True)
        self.strict_import_check.setToolTip(
            "When enabled, only explicitly imported names are considered defined. "
            "Disable for more lenient checking"
        )
        semantic_layout.addWidget(self.strict_import_check)
        
        semantic_group.setLayout(semantic_layout)
        layout.addWidget(semantic_group)
        
        # Help text
        help_text = QLabel(
            "Semantic Checker Options:\n\n"
            "• Ignore PascalCase: Useful if you use external libraries with classes\n"
            "• Ignore UPPERCASE: Useful for constants from external sources\n"
            "• Strict Import Tracking: Requires explicit imports for identifiers\n\n"
            "Note: Enable/Disable semantic analysis in the Linter Options"
        )
        help_text.setWordWrap(True)
        help_text.setStyleSheet("color: #7f8c8d; padding: 10px;")
        layout.addWidget(help_text)
        
        layout.addStretch()
        
        return tab
    
    def create_exclusions_tab(self):
        """Create exclusions configuration tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # Exclusions group
        exclusions_group = QGroupBox("Excluded Patterns")
        exclusions_layout = QVBoxLayout()
        
        # List of exclusions
        self.exclusions_list = QListWidget()
        exclusions_layout.addWidget(self.exclusions_list)
        
        # Buttons for managing exclusions
        button_layout = QHBoxLayout()
        
        self.add_exclusion_btn = QPushButton("➕ Add Pattern")
        self.add_exclusion_btn.clicked.connect(self.add_exclusion)
        button_layout.addWidget(self.add_exclusion_btn)
        
        self.remove_exclusion_btn = QPushButton("➖ Remove Pattern")
        self.remove_exclusion_btn.clicked.connect(self.remove_exclusion)
        button_layout.addWidget(self.remove_exclusion_btn)
        
        exclusions_layout.addLayout(button_layout)
        
        exclusions_group.setLayout(exclusions_layout)
        layout.addWidget(exclusions_group)
        
        # Help text
        help_text = QLabel(
            "Files and folders matching these patterns will be excluded from linting.\n"
            "Examples: __pycache__, generated, .venv, test_"
        )
        help_text.setWordWrap(True)
        help_text.setStyleSheet("color: #7f8c8d; padding: 10px;")
        layout.addWidget(help_text)
        
        return tab
    
    def load_config_values(self):
        """Load current configuration values into UI"""
        # Metrics
        self.max_lines_spin.setValue(self.config.get('max_function_lines', 20))
        self.max_depth_spin.setValue(self.config.get('max_nesting_depth', 5))
        self.max_args_spin.setValue(self.config.get('max_arguments', 3))
        self.max_complexity_spin.setValue(self.config.get('max_cyclomatic_complexity', 5))
        # Parser/Lexer Errors toggle
        self.parser_errors_checkbox.setChecked(self.config.get('parser_errors_enabled', True))
        
        # Naming conventions
        naming = self.config.get('naming_convention', {})
        
        func_naming = naming.get('function', 'snake_case')
        self.func_naming_combo.setCurrentText(func_naming)
        
        class_naming = naming.get('class', 'PascalCase')
        self.class_naming_combo.setCurrentText(class_naming)
        
        var_naming = naming.get('variable', 'snake_case')
        self.var_naming_combo.setCurrentText(var_naming)
        
        # Semantic checker settings
        semantic = self.config.get('semantic_checker', {})
        self.ignore_pascalcase_check.setChecked(semantic.get('ignore_pascalcase', False))
        self.ignore_uppercase_check.setChecked(semantic.get('ignore_uppercase', False))
        self.strict_import_check.setChecked(semantic.get('strict_import_tracking', True))
        
        # Exclusions
        self.exclusions_list.clear()
        for pattern in self.config.get('exclude', []):
            self.exclusions_list.addItem(pattern)
    
    def add_exclusion(self):
        """Add a new exclusion pattern"""
        from PyQt6.QtWidgets import QInputDialog
        
        pattern, ok = QInputDialog.getText(
            self,
            "Add Exclusion Pattern",
            "Enter pattern to exclude (e.g., __pycache__, test_*):"
        )
        
        if ok and pattern:
            # Check if pattern already exists
            items = [self.exclusions_list.item(i).text() 
                    for i in range(self.exclusions_list.count())]
            
            if pattern not in items:
                self.exclusions_list.addItem(pattern)
            else:
                QMessageBox.information(
                    self,
                    "Pattern Exists",
                    "This pattern is already in the exclusion list."
                )
    
    def remove_exclusion(self):
        """Remove selected exclusion pattern"""
        current_item = self.exclusions_list.currentItem()
        if current_item:
            row = self.exclusions_list.row(current_item)
            self.exclusions_list.takeItem(row)
        else:
            QMessageBox.information(
                self,
                "No Selection",
                "Please select a pattern to remove."
            )
    
    def save_config(self):
        """Save configuration"""
        # Update config dictionary
        self.config['max_function_lines'] = self.max_lines_spin.value()
        self.config['max_nesting_depth'] = self.max_depth_spin.value()
        self.config['max_arguments'] = self.max_args_spin.value()
        self.config['max_cyclomatic_complexity'] = self.max_complexity_spin.value()
        # Parser/Lexer Errors toggle
        self.config['parser_errors_enabled'] = self.parser_errors_checkbox.isChecked()
        
        # Update naming conventions
        self.config['naming_convention'] = {
            'function': self.func_naming_combo.currentText(),
            'class': self.class_naming_combo.currentText(),
            'variable': self.var_naming_combo.currentText()
        }
        
        # Update semantic checker settings
        self.config['semantic_checker'] = {
            'ignore_pascalcase': self.ignore_pascalcase_check.isChecked(),
            'ignore_uppercase': self.ignore_uppercase_check.isChecked(),
            'strict_import_tracking': self.strict_import_check.isChecked()
        }
        
        # Update exclusions
        exclusions = []
        for i in range(self.exclusions_list.count()):
            exclusions.append(self.exclusions_list.item(i).text())
        self.config['exclude'] = exclusions
        
        # Save to file
        if self.config_manager.update_config(self.config):
            QMessageBox.information(
                self,
                "Configuration Saved",
                "Configuration has been saved successfully."
            )
            self.accept()
        else:
            QMessageBox.critical(
                self,
                "Save Error",
                "Failed to save configuration."
            )
    
    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        reply = QMessageBox.question(
            self,
            "Reset to Defaults",
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.config = self.config_manager.DEFAULT_CONFIG.copy()
            self.load_config_values()
    
    def apply_style(self):
        """Apply Tokyo Night styling to dialog"""
        # Load Tokyo Night stylesheet
        import os
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
            print(f"Warning: Tokyo Night stylesheet not found")
            # Fallback to basic dark theme
            self.setStyleSheet("""
                QDialog { background-color: #161821; color: #c0caf5; }
                QPushButton { background-color: #2a2f45; color: #c0caf5; border-radius: 6px; padding: 6px 10px; }
            """)
        
        # Set variants for specific buttons
        self.save_btn.setProperty("variant", "success")
        self.reset_btn.setProperty("variant", "danger")
        self.add_exclusion_btn.setProperty("variant", "accent")
        self.remove_exclusion_btn.setProperty("variant", "danger")
