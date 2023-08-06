

def forall(p, domain):
    for x in domain:
        if not p(x):
            return False
    return True


def exists(p, domain):
    for x in domain:
        if p(x):
            return True
    return False
