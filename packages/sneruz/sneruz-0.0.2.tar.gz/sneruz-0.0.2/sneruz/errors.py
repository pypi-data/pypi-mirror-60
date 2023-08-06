

class Error(Exception):
    """Base class for exceptions in this module"""


class TruthAssignmentError(Error):
    """Raised when a deduction is attempted with no truth assignment"""


class TableFormatError(Error):
    """Raised when a inconsistency in table size/shape is present"""