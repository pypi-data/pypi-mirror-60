from __future__ import annotations

from sneruz.errors import TruthAssignmentError


class Prop(object):

    def __init__(self, value=None):
        super().__init__()

        self._f = None
        self.set(value)

    def __bool__(self):
        return self.deduce()

    def __call__(self, *args):
        return self.deduce(*args)

    def deduce(self, *args):
        if self._f is None:
            raise TruthAssignmentError(self)
        else:
            return self._f(*args)

    def set(self, value):
        if isinstance(value, bool):
            self._f = lambda *a: value
        elif callable(value):
            self._f = value
        else:
            self._f = None

    def is_tautology(self) -> bool:
        # a wff is a tautology if and only if it is true for all possible truth-value assignments to the statement letters making it up.
        return True

    def is_self_contradiction(self) -> bool:
        # a wff is a self-contradiction if and only if it is false for all possible truth-value assignments to the statement letters making it up.
        return True

    def is_contingent(self) -> bool:
        # A contingent statement is true for some truth-value assignments to its statement letters and false for others.
        return True

    def is_logical_consequence_of(self, wffs: list) -> bool:
        # a wff β is said to be a logical consequence of a set of wffs α1, α2, ..., αn, if and only if there is no truth-value assignment to the statement letters making up these wffs that makes all of α1, α2, ..., αn true but does not make β true.
        return True

    def Not(p: Prop) -> Prop:
        # return Prop(bool(not p))
        return Prop(lambda *a: not p(*a))

    def And(p: Prop, q: Prop) -> Prop:
        # return Prop(bool(p and q))
        return Prop(lambda *a: p(*a) and q(*a))

    def Or(p, q: Prop) -> Prop:
        # return Prop(bool(p or q))
        return Prop(lambda *a: p(*a) or q(*a))

    def Xor(p, q: Prop) -> Prop:
        # return Prop(bool((p and not q) or (not p and q)))
        return Prop(lambda *a: ((p(*a) and not q(*a)) or (not p(*a) and q(*a))))

    def Implies(p, q: Prop) -> Prop:
        # return Prop(bool((not p) or (p and q)))
        return Prop(lambda *a: ((not p(*a)) or (p(*a) and q(*a))))

    def Iff(p, q: Prop) -> Prop:
        # return Prop(bool(((not p and not q) or (p and q))))
        return Prop(lambda *a: ((not p(*a) and not q(*a)) or (p(*a) and q(*a))))

    def Forall(p, d):
        def fa(*a):
            for x in d:
                if not p(*a, x):
                    return False
            return True
        return Prop(lambda *a: fa(*a))

    def Exists(p, d):
        def ex(*a):
            for x in d:
                if p(*a, x):
                    return True
            return False
        return Prop(lambda *a: ex(*a))

    @staticmethod
    def is_consistent(wff1, wff2) -> bool:
        # two wffs are consistent if and only if there is at least one possible truth-value assignment to the statement letters making them up that makes both wffs true.
        # two wffs are inconsistent if and only if there is no truth-value assignment to the statement letters making them up that makes them both true.
        pass

    @staticmethod
    def is_logically_equivalent(prop1: Prop, prop2: Prop) -> bool:
        # wo statements are said to be logically equivalent if and only if all possible truth-value assignments to the statement letters making them up result in the same resulting truth-values for the whole statements.
        pass
