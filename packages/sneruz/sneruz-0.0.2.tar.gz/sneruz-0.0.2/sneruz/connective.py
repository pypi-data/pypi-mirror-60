

def NOT(p):
    return not p


def AND(p, q):
    return p and q


def OR(p, q):
    return p or q


def XOR(p, q):
    return (p and not q) or (not p and q)


def IMPLIES(p, q):
    return (not p) or (p and q)


def IFF(p, q):
    return ((not p and not q) or (p and q))
