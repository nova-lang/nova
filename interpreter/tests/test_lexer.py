import unittest
from nova.lexer import NovaLexer


class TestNovaLexer(unittest.TestCase):
    def test_correct_parsing_of_identifier(self):
        source = '''a'''
        expected = [('INDENT', 0, 1, 0),
                    ('IDENTIFIER', 'a', 1, 0)]
        self._assert_lexical_parsing_equals(source, *expected)

    def test_correct_parsing_of_integer(self):
        source = '''42'''
        expected = [('INDENT', 0, 1, 0),
                    ('INTEGER', 42, 1, 0)]
        self._assert_lexical_parsing_equals(source, *expected)

    def test_correct_parsing_of_backtick_enclosed_identifier(self):
        source = '''`this is an identifier`'''
        expected = [('INDENT', 0, 1, 0),
                    ('IDENTIFIER', 'this is an identifier', 1, 0)]
        self._assert_lexical_parsing_equals(source, *expected)

    def test_correct_parsing_of_binary_operation(self):
        source = '''a >= b'''
        expected = [('INDENT', 0, 1, 0),
                    ('IDENTIFIER', 'a', 1, 0),
                    ('GTE', '>=', 1, 2),
                    ('IDENTIFIER', 'b', 1, 5)]
        self._assert_lexical_parsing_equals(source, *expected)

    def _assert_lexical_parsing_equals(self, source, *expected):
        lexer = NovaLexer()
        result = [
            (token.type, token.value, token.lineno, token.lexpos)
            for token in lexer.parse(source)
        ]

        self.assertListEqual(list(expected), result)
