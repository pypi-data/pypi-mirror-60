from enum import IntEnum
from textlog2json.lexer.exception import LoglexerException

class TokenType(IntEnum):
    RootToken = -1
    UndefinedToken = 0
    NoSpecialToken = 1
    WordToken = 2
    HexdumpToken = 3
    SeparatorToken = 4
    DoubleQuotesToken = 5
    SingleQuotesToken = 6
    ParenthesesToken = 7
    BracesToken = 8
    BracketsToken = 9
    CharToken = 10
    NoSpaceToken = 11
    GreedyToken = 12
    DateToken = 13
    TimeToken = 14
    DatestampToken = 15
    DatestampRFC2822Token = 16
    DatestampRFC822Token = 17
    DatestampOtherToken = 18
    DatestampEventlogToken = 19
    TimestampISO8601Token = 20
    IntToken = 21
    IPToken = 22
    NumberToken = 23
    UUIDToken = 24
    UriToken = 25
    MacToken = 26
    LoglevelToken = 27
    HttpdateToken = 28
    Base16NumberToken = 29
    Base16FloatToken = 30
    PathToken = 31
    GermanNumberToken = 32
    PriceToken = 33
    TokenLength = 34

typeToString = [
    'Undefined',
    'NoSpecial',
    'Word',
    'Hexdump',
    'Separator',
    'DoubleQuotes',
    'SingleQuotes',
    'Parentheses',
    'Braces',
    'Brackets',
    'Char',
    'NoSpace',
    'Greedy',
    'Date',
    'Time',
    'Datestamp',
    'DatestampRFC2822',
    'DatestampRFC822',
    'DatestampOther',
    'DatestampEventlog',
    'TimestampISO8601',
    'Int',
    'IP',
    'Number',
    'UUID',
    'Uri',
    'Mac',
    'Loglevel',
    'Httpdate',
    'Base16Number',
    'Base16Float',
    'Path',
    'GermanNumber',
    'Price',
]

def token_type_to_string(token_type: int):
    if token_type < -1 or token_type > TokenType.TokenLength:
        raise LoglexerException("invalid token type")

    if token_type == -1:
        return "Root"

    return typeToString[token_type]
