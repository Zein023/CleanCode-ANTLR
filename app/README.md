# Python Clean Code Linter - GUI Application

A modern PyQt6-based GUI application for linting Python code using ANTLR4-generated parsers with both Listener and Visitor pattern implementations.

## Features

✨ **Modern User Interface**
- Beautiful Tokyo Night themed dark interface
- Clean, intuitive PyQt6 design with Fusion style
- Real-time progress tracking
- Multi-threaded linting (non-blocking UI)

📁 **Flexible File Selection**
- Add individual Python files
- Add entire folders (recursive search)
- Smart exclusion patterns (configurable)

🔍 **Dual Linting Approach**
- **Listener-based linter**: Checks clean code metrics
  - Function length
  - Nesting depth
  - Function arguments count
  - Cyclomatic complexity
  - Naming conventions
  - Built-in shadowing detection
  
- **Semantic Visitor linter**: Performs semantic analysis
  - Scope analysis
  - Variable usage tracking
  - Undefined variable detection

⚙️ **Configurable Settings**
- Customizable code metrics thresholds
- Naming convention rules (snake_case, camelCase, PascalCase)
- Exclusion patterns for files/folders
- Persistent configuration (JSON)

## Installation

### Prerequisites
- Python 3.7+
- PyQt6
- ANTLR4 Python runtime

### Install Dependencies

```bash
pip install PyQt6 antlr4-python3-runtime
```

## Usage

### Running the Application

From the `app` directory:

```bash
python main.py
```

### Using the GUI

1. **Add Files/Folders**
   - Click "Add File" to select individual Python files
   - Click "Add Folder" to recursively scan for all .py files
   - Files matching exclusion patterns are automatically filtered

2. **Configure Linter**
   - Click "⚙️ Configuration" to open settings
   - Adjust metrics thresholds
   - Set naming conventions
   - Add/remove exclusion patterns

3. **Run Linting**
   - Select which linters to use (Listener/Semantic)
   - Click "▶️ Run Linter"
   - View results in the output panel

4. **View Results**
   - Clean code violations are highlighted
   - Semantic errors are reported
   - Each file's issues are grouped together

## Configuration

Configuration is stored in `config.json` and includes:

```json
{
    "max_function_lines": 20,
    "max_nesting_depth": 5,
    "max_arguments": 3,
    "max_cyclomatic_complexity": 5,
    "naming_convention": {
        "function": "snake_case",
        "class": "PascalCase",
        "variable": "snake_case"
    },
    "exclude": [
        "__pycache__",
        "generated"
    ]
}
```

### Default Exclusions

By default, the following patterns are excluded:
- `__pycache__` - Python cache directories
- `generated` - ANTLR4 generated parser files

You can add more patterns through the GUI configuration dialog.

## Project Structure

```
app/
├── main.py                 # Application entry point
├── config.json            # Configuration file (auto-generated)
├── gui/
│   ├── __init__.py        # GUI package init
│   ├── main_window.py     # Main application window
│   ├── config_dialog.py   # Configuration dialog
│   ├── config_manager.py  # Config file manager
│   └── linter_runner.py   # Linter execution logic
├── generated/             # ANTLR4 generated files
│   ├── PythonLexer.py
│   ├── PythonParser.py
│   ├── PythonParserListener.py
│   └── PythonParserVisitor.py
└── linter/                # Linter implementations
    ├── MyListener.py      # Listener-based linter
    └── MySemanticVisitor.py  # Visitor-based linter
```

## Linter Details

### Listener-based Linter (AdvancedCleanCodeListener)

Checks for:
- ⚠️ Function length violations
- ⚠️ Excessive nesting depth
- ⚠️ Too many function parameters
- ⚠️ High cyclomatic complexity
- ⚠️ Naming convention violations
- ⚠️ Built-in function shadowing

### Semantic Visitor Linter (MySemanticVisitor)

Performs:
- 🔍 Scope analysis
- 🔍 Variable definition tracking
- 🔍 Undefined variable detection
- 🔍 Function scope management

## Troubleshooting

### "No module named PyQt6"
Install PyQt6:
```bash
pip install PyQt6
```

### "No module named antlr4"
Install ANTLR4 runtime:
```bash
pip install antlr4-python3-runtime
```

### Import errors for generated files
Ensure the `generated/` folder contains:
- PythonLexer.py
- PythonParser.py
- PythonParserListener.py
- PythonParserVisitor.py

### Config.json not found
The application will automatically create a default `config.json` on first run.

## Contributing

Feel free to extend the linters with additional rules or improve the UI!

## License

This project is part of the CleanCode-ANTLR repository.
