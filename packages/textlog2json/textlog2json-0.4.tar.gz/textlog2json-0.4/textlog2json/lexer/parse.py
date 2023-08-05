from textlog2json.lexer._loglexer import ffi, lib
from textlog2json.lexer.exception import LoglexerException
from textlog2json.lexer.token import Token

def parse(msg: str):
    cdata = lib.parse(ffi.new("char[]", msg.encode()))

    if (cdata == ffi.NULL):
        raise LoglexerException(ffi.string(cdata.errormsg))

    pdata = ctypes_to_python(cdata)

    lib.freeToken(cdata)
    return pdata

def ctypes_to_python(cdata):
    t = Token()
    t.type = cdata.type
    t.hash = cdata.hash
    t.text = ffi.string(cdata.text).decode("utf-8")
    t.whitespace_prefix = ffi.string(cdata.whitespace_prefix).decode("utf-8")
    t.whitespace_prefix_regexp = ffi.string(cdata.whitespace_prefix_regexp).decode("utf-8")
    t.pattern_name = ffi.string(cdata.pattern_name).decode("utf-8")
    t.pattern_type = cdata.pattern_type

    children = []
    child = cdata.first_child
    while (child != ffi.NULL):
        children.append(ctypes_to_python(child))
        child = child.next

    t.children = children
    return t
