
class Domain(object):

    def __init__(self, begin, end):
        super().__init__()

        # self._begin = begin
        # self._begin_inf = (begin == INF) or (begin == POS_INF) or (begin == NEG_INF)

        # self._end = end
        # self._end_inf = (end == INF) or (end == POS_INF) or (end == NEG_INF)

        self._discretes = []

    def add(self, value):
        self._discretes.append(value)