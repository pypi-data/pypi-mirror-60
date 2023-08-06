from pylint.interfaces import IAstroidChecker
from pylint.checkers import BaseChecker


class SingleElementDestructuring(BaseChecker):
    __implements__ = IAstroidChecker

    name = 'single-element-destructuring-checker'

    SINGLE_ELEMENT_DESTRUCTURING_MSG = 'single-element-destructuring'
    msgs = {
        'W0001': (
            'Uses single element destructuring',
            SINGLE_ELEMENT_DESTRUCTURING_MSG,
            'Single element destructuring should not be used.'
        ),
    }
    options = ()

    priority = -1

    def visit_assign(self, node):
        targets = node.targets
        if len(targets) != 1:
            return
        target = targets[0]
        if hasattr(target, "pytype") and target.pytype() in ["builtins.tuple", "builtins.list"]:
            if len(list(target.get_children())) == 1:
                self.add_message(self.SINGLE_ELEMENT_DESTRUCTURING_MSG, node=node)


def register(linter):
    linter.register_checker(SingleElementDestructuring(linter))
