import unittest
from . import lexer, parser
from nova import interpreter


class TestNovaInterpreter(unittest.TestCase):
    def test_correct_parsing_of_let_statement(self):
        source = 'let a = 42'
        expected = {'a': 42}
        self._check_interpreter_context(source, expected)

    def test_correct_parsing_of_sum_expression(self):
        source = '''let a = 4
let b = a + 6'''
        expected = {'a': 4, 'b': 10}
        self._check_interpreter_context(source, expected)

    def test_correct_parsing_of_algebraic_expression(self):
        source = 'let a = (4 - 2) * 8'
        expected = {'a': 16}
        self._check_interpreter_context(source, expected)

    def _check_interpreter_context(self, source, expected):
        tree = parser.parse(lexer.parse(source))

        engine = interpreter.Engine()
        engine.add_unit('default', 'test', tree)

        scope = engine.get_unit_scope('default', 'test')

        print(scope._data)

        for key, value in expected.items():
            result = scope.get(key)
            self.assertEqual(value, result)
