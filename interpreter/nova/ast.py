class NodeDef:
    def __init__(self, key, *args):
        self._key = key
        self._args = args

    def __call__(self, *args):
        if len(args) != len(self._args):
            raise ValueError("Invalid parameters, expected: {}, got: {}".format(self._args, args))
        return Node(self._key, **dict(zip(self._args, args)))


class Node:
    def __init__(self, key, **kwargs):
        self._key = key
        self._kwargs = kwargs

    def __eq__(self, other):
        return self._key == other._key and self._kwargs == other._kwargs

    def __str__(self):
        return self._format(0)

    def __repr__(self):
        return str(self)

    def _format(self, indent):
        return '{}({})'.format(self._key, ', '.join(
            '{}={}'.format(key, value) for key, value in self._kwargs.items()))


Unit = NodeDef('Unit', 'stsmts')
StatementLet = NodeDef('StatementLet', 'name', 'expr')
ExpressionCall = NodeDef('ExpressionCall', 'func', 'args')
ExpressionVariable = NodeDef('ExpressionVariable', 'path')
