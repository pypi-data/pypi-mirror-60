class CPCAException(Exception):
    pass

class PlaceTypeNotExistException(CPCAException):
    pass

class InputTypeNotSuportException(CPCAException):
    input_type = \
"""
输入应该为
|省     |市    |区     |
|河北省 |廊坊市 |三河县 |

"""
    pass