import unittest
from . import lexer, parser
from nova import ast, interpreter


class TestNovaParser(unittest.TestCase):
    def test_correct_parsing_of_let_expression(self):
        source = '''let a = b'''
        expected = ast.Unit([
            ast.StatementLet('a', ast.ExpressionVariable(['b']))])
        self._assert_parsing_equals(source, expected)

    def test_correct_parsing_of_sum_expression(self):
        source = '''let a = b + c
let d = e'''
        expected = ast.Unit([
            ast.StatementLet(
                'a',
                ast.ExpressionCall(
                    ast.ExpressionVariable([interpreter.OperationsAdd]), [
                        ast.ExpressionVariable(['b']),
                        ast.ExpressionVariable(['c'])])),
            ast.StatementLet(
                'd',
                ast.ExpressionVariable(['e']))])

        self._assert_parsing_equals(source, expected)

    def _assert_parsing_equals(self, source, expected):
        result = parser.parse(lexer.parse(source))
        self.assertEqual(expected, result)
