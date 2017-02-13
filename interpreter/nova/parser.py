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
        ('nonassoc', 'AND', 'OR'),
        ('nonassoc', 'EQUAL', 'NEQ', 'LES', 'GRT', 'LTE', 'GTE'),

        ('left', 'PLUS', 'MINUS'),
        ('left', 'TIMES', 'FDIV', 'DIV', 'MOD'),
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

    def p_expression_binary_operation(self, t):
        '''expression : expression AND expression
                      | expression OR expression
                      | expression EQUAL expression
                      | expression NEQ expression
                      | expression LES expression
                      | expression GRT expression
                      | expression LTE expression
                      | expression GTE expression
                      | expression PLUS expression
                      | expression MINUS expression
                      | expression TIMES expression
                      | expression FDIV expression
                      | expression DIV expression
                      | expression MOD expression'''

        operators = {
            '+': interpreter.OperationsAdd,
            '-': interpreter.OperationsSub,
            '*': interpreter.OperationsMult,
            '/': interpreter.OperationsFDiv,
            'div': interpreter.OperationsIDiv,
            'mod': interpreter.OperationsMod,
        }

        t[0] = ast.ExpressionCall(ast.ExpressionVariable([operators[t[2]]]), [t[1], t[3]])

    def p_expression_unary_operation(self, t):
        '''expression : NOT expression
                      | MINUS expression'''
        operators = {
            'not': interpreter.OperationsNot,
            '-': interpreter.OperationsNeg,
        }

        t[0] = ast.ExpressionCall(ast.ExpressionVariable([operators[t[1]]]), [t[2]])

    def p_expression_parens(self, t):
        'expression : LPAREN expression RPAREN'
        t[0] = t[2]

    def p_expression_identifier(self, t):
        'expression : IDENTIFIER'
        t[0] = ast.ExpressionVariable([t[1]])

    def p_expression_integer(self, t):
        'expression : INTEGER'
        t[0] = ast.ExpressionNumber(t[1])

    def p_empty(self, p):
        'empty :'
        pass

    # Error rule for syntax errors
    def p_error(self, p):
        print("Syntax error in input!")
