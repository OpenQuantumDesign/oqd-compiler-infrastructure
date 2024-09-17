from .base import PassBase

########################################################################################

__all__ = [
    "Rewriter",
    "Chain",
    "FixedPoint",
]

########################################################################################


class Rewriter(PassBase):
    """
    This class represents a wrapper for passes to compose and modify their logic without
    affecting the internals of a pass.
    """

    pass


########################################################################################


class Chain(Rewriter):
    """
    This class represents a composite pass where the passes are applied sequentially.
    """

    def __init__(self, *rules):
        super().__init__()

        self.rules = list(rules)
        pass

    @property
    def children(self):
        return self.rules

    def map(self, model):
        new_model = model
        for rule in self.rules:
            new_model = rule(new_model)
        return new_model


class FixedPoint(Rewriter):
    """
    This class represents a wrapped pass that is applied until the object/IR converges to a fixed point
    or reaches a maximum iteration count.
    """

    def __init__(self, rule, *, max_iter=1000):
        super().__init__()

        self.rule = rule
        self.max_iter = max_iter
        pass

    @property
    def children(self):
        return [self.rule]

    def map(self, model):
        i = 0
        new_model = model
        while True:
            _model = self.rule(new_model)

            if _model == new_model or i >= self.max_iter:
                return new_model

            new_model = _model
            i += 1
