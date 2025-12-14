import sys
import os

# Add generated folder to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'generated'))

from PythonParserVisitor import PythonParserVisitor
from PythonParser import PythonParser

class Scope:
    """Represents a scope (global or function-local)."""
    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent
        self.symbols = set()

    def define(self, name):
        """Define a symbol in this scope."""
        self.symbols.add(name)

    def resolve(self, name):
        """Check if symbol exists in this scope or parent scopes."""
        if name in self.symbols:
            return True
        if self.parent:
            return self.parent.resolve(name)
        return False


class MySemanticVisitor(PythonParserVisitor):
    """
    Semantic analyzer for Python code.
    Detects undefined variable usage through a simple AST walk.
    
    Key approach:
    - Process assignments BEFORE visiting children (define vars first)
    - Track function scopes
    - Report undefined variable access
    """
    
    def __init__(self, config=None):
        self.current_scope = Scope("Global")
        self.global_scope = self.current_scope
        
        # Load semantic checker configuration
        if config and 'semantic_checker' in config:
            semantic_config = config['semantic_checker']
            self.ignore_pascalcase = semantic_config.get('ignore_pascalcase', False)
            self.ignore_uppercase = semantic_config.get('ignore_uppercase', False)
            self.strict_import_tracking = semantic_config.get('strict_import_tracking', True)
        else:
            # Default settings
            self.ignore_pascalcase = False
            self.ignore_uppercase = False
            self.strict_import_tracking = True
        
        self._init_builtins()
    
    def _init_builtins(self):
        """Add built-in functions and keywords to global scope."""
        builtins = [
            # Functions
            'print', 'range', 'len', 'int', 'str', 'list', 'dict', 'set', 'tuple',
            'float', 'bool', 'type', 'object', 'enumerate', 'zip', 'map', 'filter',
            'sorted', 'sum', 'max', 'min', 'abs', 'open', 'input', 'isinstance',
            'issubclass', 'hasattr', 'getattr', 'setattr', 'delattr', 'callable',
            'iter', 'next', 'reversed', 'all', 'any', 'chr', 'ord', 'hex', 'oct',
            'bin', 'round', 'pow', 'divmod', 'compile', 'eval', 'exec',
            'locals', 'globals', 'vars', 'dir', 'help', 'id', 'hash',
            'format', 'repr', 'ascii', 'bytes', 'bytearray', 'memoryview',
            'frozenset', 'complex', 'property', 'classmethod', 'staticmethod',
            'super', 'slice',
            # Common exceptions
            'Exception', 'BaseException', 'ValueError', 'TypeError', 'KeyError',
            'IndexError', 'AttributeError', 'RuntimeError', 'NotImplementedError',
            'ImportError', 'ModuleNotFoundError', 'NameError', 'SyntaxError',
            'IndentationError', 'TabError', 'SystemError', 'StopIteration',
            'GeneratorExit', 'KeyboardInterrupt', 'SystemExit', 'OSError',
            'IOError', 'FileNotFoundError', 'PermissionError', 'ZeroDivisionError',
            'AssertionError', 'EOFError', 'MemoryError', 'RecursionError',
            'UnicodeError', 'UnicodeDecodeError', 'UnicodeEncodeError',
            # Common classes
            'FileStream', 'StringIO', 'BytesIO',
            # Constants
            'None', 'True', 'False', 'NotImplemented', 'Ellipsis',
            '__name__', '__main__', '__file__', '__doc__', '__builtins__'
        ]
        for name in builtins:
            self.current_scope.define(name)
    
    # ===== IMPORTS =====
    
    def visitImport_stmt(self, ctx):
        """
        Handle import statements (both import and from...import)
        """
        try:
            # Check what type of import this is
            full_text = ctx.getText()
            
            if full_text.startswith('from'):
                # from X import Y style
                self._handle_from_import(full_text)
            else:
                # import X style
                self._handle_import(full_text)
        except:
            pass
        
        return None
    
    def _handle_import(self, full_text):
        """Handle: import module [as alias]"""
        try:
            # Remove 'import' keyword (which might not have spaces)
            if 'import' in full_text:
                idx = full_text.find('import')
                imports_text = full_text[idx + 6:].strip()  # len('import') = 6
            else:
                return
            
            # Split by comma
            for item in imports_text.split(','):
                item = item.strip()
                if not item:
                    continue
                
                # Handle "...as..." (look for 'as' keyword)
                if 'as' in item:
                    # Split by 'as'
                    parts = item.split('as')
                    if len(parts) == 2:
                        alias = parts[1].strip()
                        if alias and alias.isidentifier():
                            self.current_scope.define(alias)
                # Handle "module" or "module.submodule"
                elif item:
                    # Take first part for dotted imports
                    module_name = item.split('.')[0]
                    if module_name and module_name.isidentifier():
                        self.current_scope.define(module_name)
        except:
            pass
    
    def _handle_from_import(self, full_text):
        """Handle: from module import name [as alias]"""
        try:
            # Extract the "import ..." part
            import_idx = full_text.find('import')
            if import_idx < 0:
                return
            
            imports_part = full_text[import_idx + 6:].strip()  # len('import') = 6
            
            # Remove parentheses if present (multi-line imports)
            imports_part = imports_part.strip('()')
            
            # Handle wildcard imports
            if imports_part.strip() == '*':
                return
            
            # Split by comma
            for name_part in imports_part.split(','):
                name_part = name_part.strip()
                if not name_part:
                    continue
                
                # Handle "...as..."
                if 'as' in name_part:
                    parts = name_part.split('as')
                    if len(parts) == 2:
                        alias = parts[1].strip()
                        if alias and alias.isidentifier():
                            self.current_scope.define(alias)
                # Handle just "name"
                else:
                    # Clean up any remaining parentheses or whitespace
                    name_part = name_part.strip('() \t\n\r')
                    if name_part and name_part.isidentifier():
                        self.current_scope.define(name_part)
        except:
            pass
    
    # ===== STATEMENTS & ASSIGNMENTS =====
    
    def visitAssignment(self, ctx):
        """
        Handle: target = value
        Register target BEFORE processing value to avoid false "undefined" errors.
        """
        try:
            children = list(ctx.children)
            
            # Find the '=' operator
            eq_idx = -1
            for i, child in enumerate(children):
                if hasattr(child, 'getText') and child.getText() == '=':
                    eq_idx = i
                    break
            
            if eq_idx > 0:
                # Extract LHS names and define them
                lhs = children[0]
                lhs_names = self._extract_names_from_target(lhs.getText())
                
                for name in lhs_names:
                    self.current_scope.define(name)
                
                # Visit RHS (after '=')
                for i in range(eq_idx + 1, len(children)):
                    self.visit(children[i])
                
                return None
        except:
            pass
        
        return self.visitChildren(ctx)
    
    def _extract_names_from_target(self, text):
        """Extract variable names from assignment target."""
        text = text.strip()
        names = []
        
        # Handle tuple unpacking
        if ',' in text:
            for part in text.split(','):
                part = part.strip()
                if part and part.isidentifier():
                    names.append(part)
        # Handle simple name
        elif text.isidentifier():
            names.append(text)
        
        return names
    
    # ===== FUNCTION DEFINITIONS =====
    
    def visitFunction_def(self, ctx):
        """
        Handle: def func_name(params): body
        Create new scope for function body.
        """
        try:
            # Extract function name
            func_name = self._extract_function_name(ctx)
            
            if not func_name:
                return self.visitChildren(ctx)
            
            # Define function in current scope
            self.current_scope.define(func_name)
            
            # Create new scope for function body
            parent_scope = self.current_scope
            self.current_scope = Scope(func_name, parent=parent_scope)
            
            # Extract and define parameters
            self._define_function_params(ctx)
            
            # Visit function body
            self.visitChildren(ctx)
            
            # Restore parent scope
            self.current_scope = parent_scope
            
        except:
            pass
        
        return None
    
    # ===== CLASS DEFINITIONS =====
    
    def visitClass_def(self, ctx):
        """
        Handle: class ClassName: body
        Define class name in current scope and create new scope for class body.
        """
        try:
            # Extract class name
            class_name = self._extract_class_name(ctx)
            
            if not class_name:
                return self.visitChildren(ctx)
            
            # Define class in current scope (so it can be instantiated later)
            self.current_scope.define(class_name)
            
            # Create new scope for class body
            parent_scope = self.current_scope
            self.current_scope = Scope(class_name, parent=parent_scope)
            
            # Visit class body
            self.visitChildren(ctx)
            
            # Restore parent scope
            self.current_scope = parent_scope
            
        except:
            pass
        
        return None
    
    # ===== LOOPS (FOR, WHILE) =====
    
    def visitFor_stmt(self, ctx):
        """
        Handle: for target in iter: body
        Define the loop variable(s) in current scope.
        Grammar: 'for' star_targets 'in' star_expressions ':' block
        """
        try:
            # Get star_targets (the loop variable(s))
            # Children are: [for, star_targets, in, star_expressions, :, block]
            if len(ctx.children) >= 4:
                # star_targets is typically the second child (index 1)
                star_targets = ctx.children[1]
                var_text = star_targets.getText()
                
                # Extract variable names
                if var_text:
                    # Handle simple case: for x in ...
                    if var_text.isidentifier():
                        self.current_scope.define(var_text)
                    # Handle tuple unpacking: for x, y in ...
                    elif ',' in var_text:
                        for name in var_text.split(','):
                            name = name.strip()
                            if name and name.isidentifier():
                                self.current_scope.define(name)
        except:
            pass
        
        return self.visitChildren(ctx)
    
    # ===== EXCEPTION HANDLING =====
    
    def visitTry_stmt(self, ctx):
        """
        Handle try statements.
        Process except blocks to define exception variables.
        """
        return self.visitChildren(ctx)
    
    def visitExcept_block(self, ctx):
        """
        Handle: except ExceptionType as e:
        Define the exception variable in current scope.
        """
        try:
            full_text = ctx.getText()
            
            # Look for 'as' keyword to get exception variable
            as_idx = full_text.find(' as ')
            if as_idx < 0:
                as_idx = full_text.find('as')
            
            if as_idx >= 0:
                # Get text after 'as'
                after_as = full_text[as_idx:].lstrip('as').strip()
                
                # Extract variable name (up to ':')
                colon_idx = after_as.find(':')
                if colon_idx > 0:
                    var_name = after_as[:colon_idx].strip()
                else:
                    var_name = after_as.strip()
                
                # Define the exception variable
                if var_name and var_name.isidentifier():
                    self.current_scope.define(var_name)
        except:
            pass
        
        return self.visitChildren(ctx)
    
    # ===== WITH STATEMENTS =====
    
    def visitWith_stmt(self, ctx):
        """
        Handle: with expression as name: body
        Define the 'as' variable in current scope.
        Example: with open('file') as f:
        Grammar: 'with' with_item (',' with_item)* ':' block
        where with_item: expression ('as' star_target)?
        """
        try:
            # Process all with_items to extract 'as' variables
            # Children: ['with', with_item, ',', with_item, ..., ':', block]
            for child in ctx.children:
                child_type = child.__class__.__name__
                if child_type == 'With_itemContext':
                    self._extract_with_item_variable(child)
        except:
            pass
        
        return self.visitChildren(ctx)
    
    def _extract_with_item_variable(self, with_item_ctx):
        """
        Extract variable from a with_item node.
        Grammar: expression ('as' star_target)?
        Children: [expression, 'as', star_target] (if 'as' clause exists)
        """
        try:
            children = list(with_item_ctx.children)
            
            # Look for 'as' keyword (should be child[1] if present)
            for i, child in enumerate(children):
                child_text = child.getText() if hasattr(child, 'getText') else str(child)
                
                # If this is 'as', the next child is the star_target with the variable name
                if child_text == 'as' and i + 1 < len(children):
                    target = children[i + 1]
                    var_text = target.getText()
                    
                    # Extract identifier(s)
                    if var_text and var_text.isidentifier():
                        self.current_scope.define(var_text)
                    elif ',' in var_text:
                        # Tuple unpacking: with ... as (x, y):
                        for name in var_text.split(','):
                            name = name.strip('()')
                            if name and name.isidentifier():
                                self.current_scope.define(name)
        except:
            pass
    
    # ===== COMPREHENSIONS & GENERATORS =====
    
    def visitListcomp(self, ctx):
        """
        Handle list comprehension: [expr for x in iter]
        Create a new scope and define loop variables before visiting expression.
        """
        # Create new scope for comprehension
        parent_scope = self.current_scope
        self.current_scope = Scope("Comprehension", parent=parent_scope)
        
        try:
            # Extract and define variables from for_if_clauses FIRST
            self._define_comp_for_variables(ctx)
            
            # Then visit the expression and clauses
            self.visitChildren(ctx)
        finally:
            # Restore parent scope
            self.current_scope = parent_scope
        
        return None
    
    def visitDictcomp(self, ctx):
        """
        Handle dict comprehension: {k: v for x in iter}
        Create a new scope and define loop variables before visiting expression.
        """
        # Create new scope for comprehension
        parent_scope = self.current_scope
        self.current_scope = Scope("Comprehension", parent=parent_scope)
        
        try:
            # Extract and define variables from for_if_clauses FIRST
            self._define_comp_for_variables(ctx)
            
            # Then visit the expression and clauses
            self.visitChildren(ctx)
        finally:
            # Restore parent scope
            self.current_scope = parent_scope
        
        return None
    
    def visitSetcomp(self, ctx):
        """
        Handle set comprehension: {expr for x in iter}
        Create a new scope and define loop variables before visiting expression.
        """
        # Create new scope for comprehension
        parent_scope = self.current_scope
        self.current_scope = Scope("Comprehension", parent=parent_scope)
        
        try:
            # Extract and define variables from for_if_clauses FIRST
            self._define_comp_for_variables(ctx)
            
            # Then visit the expression and clauses
            self.visitChildren(ctx)
        finally:
            # Restore parent scope
            self.current_scope = parent_scope
        
        return None
    
    def visitGenexp(self, ctx):
        """
        Handle generator expression: (expr for x in iter)
        Create a new scope and define loop variables before visiting expression.
        """
        # Create new scope for generator
        parent_scope = self.current_scope
        self.current_scope = Scope("Generator", parent=parent_scope)
        
        try:
            # Extract and define variables from for_if_clauses FIRST
            self._define_comp_for_variables(ctx)
            
            # Then visit the expression and clauses
            self.visitChildren(ctx)
        finally:
            # Restore parent scope
            self.current_scope = parent_scope
        
        return None
    
    def _define_comp_for_variables(self, ctx):
        """
        Extract and define loop variables from for_if_clauses.
        This is called BEFORE visiting the expression part.
        Grammar: listcomp: '[' named_expression for_if_clauses ']'
        We need to find for_if_clauses child and extract star_targets from it.
        """
        try:
            # Walk through children to find for_if_clauses
            for child in ctx.children:
                child_type = child.__class__.__name__
                
                # Found the for_if_clauses node
                if child_type == 'For_if_clausesContext':
                    self._extract_for_if_variables(child)
                    break
        except:
            pass
    
    def _extract_for_if_variables(self, for_if_clauses_ctx):
        """
        Extract variables from for_if_clauses node.
        Grammar: for_if_clauses: for_if_clause+
        Grammar: for_if_clause: 'async'? 'for' star_targets 'in' disjunction ('if' disjunction)*
        """
        try:
            # for_if_clauses contains one or more for_if_clause
            for child in for_if_clauses_ctx.children:
                child_type = child.__class__.__name__
                
                if child_type == 'For_if_clauseContext':
                    # for_if_clause children: ['for', star_targets, 'in', disjunction, ...]
                    # We need the star_targets (second or third child depending on 'async')
                    for i, subchild in enumerate(child.children):
                        subchild_text = subchild.getText() if hasattr(subchild, 'getText') else str(subchild)
                        
                        # If this is 'for', the next child is star_targets
                        if subchild_text == 'for' and i + 1 < len(child.children):
                            star_targets = child.children[i + 1]
                            var_text = star_targets.getText()
                            
                            # Define the variables
                            if var_text and var_text.isidentifier():
                                self.current_scope.define(var_text)
                            elif ',' in var_text:
                                for name in var_text.split(','):
                                    name = name.strip()
                                    if name and name.isidentifier():
                                        self.current_scope.define(name)
                            break
        except:
            pass
    
    def visitAtom(self, ctx):
        """
        Check NAME tokens in atoms (simple variable references).
        Report undefined variables based on configuration.
        """
        text = ctx.getText()
        
        # Don't process comprehensions here - they're handled by their own visit methods
        # Just check variable usage in simple atoms
        try:
            # Only check if it's a simple identifier
            if text.isidentifier() and not text[0].isdigit():
                # Skip keywords and special names
                if text not in ['None', 'True', 'False', 'self', '__name__', '__main__']:
                    # Check if defined
                    if not self.current_scope.resolve(text):
                        # Apply ignore rules based on configuration
                        should_ignore = False
                        
                        if self.ignore_pascalcase and text[0].isupper() and not text.isupper():
                            # PascalCase check
                            should_ignore = True
                        elif self.ignore_uppercase and text.isupper():
                            # UPPERCASE check
                            should_ignore = True
                        
                        if not should_ignore:
                            # Report error with line number
                            line_num = self._get_line_number(ctx)
                            location = f"line {line_num}" if line_num else "unknown location"
                            print(f"  ❌ [ERROR] Undefined variable: '{text}' ({location}) in scope '{self.current_scope.name}'")
        except:
            pass
        
        return self.visitChildren(ctx)
    
    # ===== FUNCTION DEFINITIONS =====
    
    def _extract_function_name(self, ctx):
        """Extract function name from function_def context."""
        try:
            full_text = ctx.getText()
            
            # Look for pattern: "def NAME("
            def_idx = full_text.find('def')
            if def_idx >= 0:
                after_def = full_text[def_idx + 3:].lstrip()
                # Get everything before '('
                paren_idx = after_def.find('(')
                if paren_idx > 0:
                    name = after_def[:paren_idx].strip()
                    if name and name.isidentifier():
                        return name
        except:
            pass
        
        return None
    
    def _extract_class_name(self, ctx):
        """Extract class name from class_def context."""
        try:
            full_text = ctx.getText()
            
            # Look for pattern: "class NAME:" or "class NAME("
            class_idx = full_text.find('class')
            if class_idx >= 0:
                after_class = full_text[class_idx + 5:].lstrip()
                # Get everything before ':' or '(' (for inheritance)
                colon_idx = after_class.find(':')
                paren_idx = after_class.find('(')
                
                # Find the first delimiter
                end_idx = len(after_class)
                if colon_idx >= 0:
                    end_idx = min(end_idx, colon_idx)
                if paren_idx >= 0:
                    end_idx = min(end_idx, paren_idx)
                
                if end_idx > 0:
                    name = after_class[:end_idx].strip()
                    if name and name.isidentifier():
                        return name
        except:
            pass
        
        return None
    
    def _define_function_params(self, ctx):
        """Extract function parameters and define them in current scope."""
        try:
            full_text = ctx.getText()
            
            # Extract text between '(' and ')'
            start = full_text.find('(')
            end = full_text.find(')')
            
            if start >= 0 and end > start:
                params_str = full_text[start + 1:end]
                
                # Split by comma
                for param in params_str.split(','):
                    # Clean: "name: Type = default" -> "name"
                    param = param.split('=')[0].split(':')[0].strip()
                    # Skip *, **, etc
                    if param and param not in ['*', '**', 'self']:
                        self.current_scope.define(param)
        except:
            pass
    
    # ===== VARIABLE USAGE & LINE NUMBER EXTRACTION =====
    
    def _get_line_number(self, ctx):
        """
        Extract line number from parse tree context.
        """
        try:
            # Try to get start token with line info
            if hasattr(ctx, 'start') and ctx.start is not None:
                return ctx.start.line
            elif hasattr(ctx, 'getStart'):
                start_token = ctx.getStart()
                if start_token and hasattr(start_token, 'line'):
                    return start_token.line
        except:
            pass
        return None
    
    # Default: visit children
    def visitChildren(self, ctx):
        """Default implementation: visit all children."""
        return super().visitChildren(ctx)