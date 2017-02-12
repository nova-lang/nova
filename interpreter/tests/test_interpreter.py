import unittest
from nova import interpreter
from nova.lexer import NovaLexer
from nova.parser import NovaParser


class TestNovaInterpreter(unittest.TestCase):
    def test_correct_parsing_of_let_expression(self):
        source = '''let a = 42'''
        expected = {'a': 42}
        self._check_interpreter_context(source, expected)

    def test_correct_parsing_of_sum_expression(self):
        source = '''let a = 4
let b = a + 6'''
        expected = {
            'a': 4,
            'b': 10,
        }

        self._check_interpreter_context(source, expected)

    def _check_interpreter_context(self, source, expected):
        lexer = NovaLexer()
        parser = NovaParser(lexer)
        tree = parser.parse(lexer.parse(source))

        engine = interpreter.Engine()
        engine.add_unit('default', 'test', tree)

        scope = engine.get_unit_scope('default', 'test')

        print(scope._data)

        for key, value in expected.items():
            result = scope.get(key)
            self.assertEqual(value, result)
