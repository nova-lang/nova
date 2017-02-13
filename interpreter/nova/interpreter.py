from . import ast


OperationsAdd = '@add'
OperationsSub = '@sub'
OperationsMult = '@mult'
OperationsFDiv = '@fdiv'
OperationsIDiv = '@idiv'
OperationsMod = '@mod'
OperationsNot = '@not'

OperationsAnd = '@and'
OperationsOr = '@or'
OperationsNeg = '@neg'

OperationsEqual = '@eql'
OperationsNotEqual = '@neq'
OperationsLess = '@les'
OperationsGreater = '@grt'
OperationsLessEqual = '@lte'
OperationsGreaterEqual = '@gte'


class IntepreterError(Exception):
    pass


class WalkerBase:
    @classmethod
    def raise_error(cls, node):
        raise IntepreterError(node.key if node is not None else 'None')

    @classmethod
    def assert_node(cls, node, expected):
        if not cls.is_node(node, expected):
            cls.raise_error(node)

    @classmethod
    def is_node(cls, node, expected):
        return node is not None and node.key == expected.key


class UnitWalker(WalkerBase):
    @classmethod
    def walk(cls, node, scope):
        cls.walk_unit(node, scope)

    @classmethod
    def walk_unit(cls, node, scope):
        cls.assert_node(node, ast.Unit)
        for statement in node.statements:
            cls.walk_unit_statement(statement, scope)

    @classmethod
    def walk_unit_statement(cls, node, scope):
        if cls.is_node(node, ast.StatementLet):
            cls.walk_let_statement(node, scope)
        else:
            cls.raise_error(node)

    @classmethod
    def walk_let_statement(cls, node, scope):
        cls.assert_node(node, ast.StatementLet)
        scope.set(node.name, cls.walk_expression(node.expression, scope))

    @classmethod
    def walk_expression(cls, node, scope):
        if cls.is_node(node, ast.ExpressionCall):
            return cls.walk_call_expression(node, scope)
        elif cls.is_node(node, ast.ExpressionVariable):
            return cls.walk_variable_expression(node, scope)
        elif cls.is_node(node, ast.ExpressionNumber):
            return cls.walk_number_expression(node, scope)
        else:
            cls.raise_error(node)

    @classmethod
    def walk_call_expression(cls, node, scope):
        cls.assert_node(node, ast.ExpressionCall)
        return cls.walk_variable_expression(node.function, scope)(*[
            cls.walk_expression(arg, scope) for arg in node.arguments
        ])

    @classmethod
    def walk_variable_expression(cls, node, scope):
        cls.assert_node(node, ast.ExpressionVariable)
        return scope.get(node.path[0])

    @classmethod
    def walk_number_expression(cls, node, scope):
        cls.assert_node(node, ast.ExpressionNumber)
        return node.number


class Function:
    def __init__(self, callback):
        self._callback = callback

    def __call__(self, *args):
        return self._callback(*args)


class Engine:
    def __init__(self):
        self._scopes = {}
        self._prepare_global_scope()

    def add_unit(self, package, name, tree):
        scope = self._global_scope.fork()
        UnitWalker.walk(tree, scope)
        self._scopes[(package, name)] = scope

    def get_unit_scope(self, package, name):
        return self._scopes[(package, name)]

    def _prepare_global_scope(self):
        self._global_scope = Scope()
        self._global_scope.set(OperationsAdd, Function(lambda a, b: a + b))
        self._global_scope.set(OperationsMult, Function(lambda a, b: a * b))
        self._global_scope.set(OperationsSub, Function(lambda a, b: a - b))


class Scope:
    def __init__(self, parent=None):
        self._parent = parent
        self._data = {}

    def fork(self):
        return Scope(self)

    def get(self, key):
        if key in self._data:
            return self._data[key]

        if self._parent is not None:
            return self._parent.get(key)

        raise KeyError(key)

    def set(self, key, value):
        if not self._try_set(key, value):
            self._data[key] = value

    def _try_set(self, key, value):
        if key in self._data:
            self._data[key] = value
            return True

        if self._parent is not None:
            return self._parent._try_set(key, value)

        return False
