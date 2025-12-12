from antlr4.error.ErrorListener import ErrorListener

class CollectingErrorListener(ErrorListener):
    def __init__(self):
        super().__init__()
        self.errors = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        location = f"line {line}, col {column}"
        self.errors.append(f"Syntax error at {location}: {msg}")
