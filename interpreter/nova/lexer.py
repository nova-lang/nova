import re
from ply import lex


class NovaTokensDescription:
    keywords = [
        'module', 'let', 'end', 'type', 'match', 'with', 'for', 'do', 'in', 'if', 'then', 'else',
        'fn', 'raise', 'import', 'and', 'or', 'not', 'var', 'div', 'mod',
    ]

    symbols = [
        ('DOT',       '.'),
        ('PLUS',      '+'),
        ('MINUS',     '-'),
        ('TIMES',     '*'),
        ('FDIV',      '/'),
        ('COLON',     ':'),
        ('SEMICOLON', ';'),
        ('COMMA',     ','),
        ('EQUAL',     '='),
        ('LES',       '<'),
        ('GRT',       '>'),
        ('LTE',       '<='),
        ('GTE',       '>='),
        ('NEQ',       '!='),
        ('LPAREN',    '('),
        ('RPAREN',    ')'),
        ('LBRACKET',  '['),
        ('RBRACKET',  ']'),
        ('LBRACE',    '{'),
        ('RBRACE',    '}'),
        ('LARROW',    '<-'),
        ('RARROW',    '->'),
    ]

    indentifier_pattern = r"([a-zA-Z_][a-zA-Z0-9_']*|`[^`\t\n]+`)"
    newline_pattern = r'(\ *\n)+'
    whitespace_pattern = r'\ +'
    integer_pattern = r'\d+'
    string_pattern = r'"(\\"|[^"\n])*"'
    comment_pattern = r'//[^\n]*'


class NovaLexer:
    t_WHITESPACE = NovaTokensDescription.whitespace_pattern
    t_STRING = NovaTokensDescription.string_pattern
    t_COMMENT = NovaTokensDescription.comment_pattern

    def __init__(self, **kwargs):
        self._prepare()
        self._kwargs = kwargs

    def _prepare(self):
        tokens = ['IDENTIFIER', 'WHITESPACE', 'NEWLINE', 'INDENT', 'INTEGER', 'FLOAT', 'COMMENT',
                  'STRING']

        for keyword in NovaTokensDescription.keywords:
            tokens.append(keyword.upper())

        for symbol, pattern in NovaTokensDescription.symbols:
            tokens.append(symbol)
            setattr(self, 't_{}'.format(symbol), re.escape(pattern))

        self.tokens = tuple(tokens)

    @lex.TOKEN(NovaTokensDescription.indentifier_pattern)
    def t_IDENTIFIER(self, t):
        if t.value in NovaTokensDescription.keywords:
            t.type = t.value.upper()

        match = re.match(r'`(.+)`$', t.value)
        if match:
            t.value = match.group(1)

        return t

    @lex.TOKEN(NovaTokensDescription.newline_pattern)
    def t_NEWLINE(self, t):
        t.lexer.lineno += t.value.count('\n')
        return t

    @lex.TOKEN(NovaTokensDescription.integer_pattern)
    def t_INTEGER(self, t):
        t.value = int(t.value)
        return t

    def t_error(self, t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    def parse(self, source):
        lexer = lex.lex(module=self, **self._kwargs)
        lexer.input(source)
        stream = iter(lexer.token, None)
        stream = self._annotate_indentation(stream)
        return stream

    def _annotate_indentation(self, stream):
        line_start = True
        for token in stream:
            if token.type == 'NEWLINE':
                line_start = True
            elif line_start:
                if token.type == 'WHITESPACE':
                    yield self._make_indent_token(len(token.value), token.lineno, token.lexpos)
                else:
                    yield self._make_indent_token(0, token.lineno, token.lexpos)
                    yield token
                line_start = False
            elif token.type != 'WHITESPACE':
                yield token

    def _make_indent_token(self, size, lineno, lexpos):
        return self._make_token('INDENT', size, lineno, lexpos)

    def _make_token(self, type_, value, lineno, lexpos):
        tok = lex.LexToken()
        tok.type = type_
        tok.value = value
        tok.lineno = lineno
        tok.lexpos = lexpos
        return tok
