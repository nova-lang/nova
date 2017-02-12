import ply.yacc as yacc
from . import ast
from . import interpreter


class LexerWrapper:
    def __init__(self, tokens):
        self._index = 0
        self._tokens = list(tokens)

    def token(self):
        if self._index < len(self._tokens):
            self._index += 1
            return self._tokens[self._index - 1]
        return None


class NovaParser:
    precedence = (
        ('left', 'PLUS'),
    )

    def __init__(self, lexer):
        self.tokens = lexer.tokens
        self._parser = yacc.yacc(module=self)

    def parse(self, tokens):
        return self._parser.parse(lexer=LexerWrapper(tokens))

    def p_unit(self, t):
        '''unit : unit_statements'''
        t[0] = ast.Unit(t[1])

    def p_unit_statements(self, t):
        '''unit_statements : unit_statement unit_statements
                           | empty'''
        t[0] = [t[1]] + t[2] if len(t) == 3 else []

    def p_unit_statement_let(self, t):
        'unit_statement : INDENT statement_let'
        t[0] = t[2]

    def p_statement_let(self, t):
        'statement_let : LET IDENTIFIER EQUAL expression'
        t[0] = ast.StatementLet(t[2], t[4])

    def p_expression_binop(self, t):
        '''expression : expression PLUS expression'''
        t[0] = ast.ExpressionCall(interpreter.OperationsAdd, [t[1], t[3]])

    def p_expression_identifier(self, t):
        'expression : IDENTIFIER'
        t[0] = ast.ExpressionVariable([t[1]])

    def p_empty(self, p):
        'empty :'
        pass

    # Error rule for syntax errors
    def p_error(self, p):
        print("Syntax error in input!")
