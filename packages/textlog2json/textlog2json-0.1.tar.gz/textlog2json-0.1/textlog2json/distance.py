from textlog2json.lexer.token import Token
from textlog2json.pattern_type import PatternType
from typing import List

def distanceTokens(a:Token, b:Token) -> int:
    """ Calculate the distance between two tokens. Tokens can have a distance of 0 or 1.
    If tokens have children the distance is 0, when both tokens are of the same type.
    Static tokens have a distance of 0 if they are identical and a distance of 1 if not.
    """

    if a.children and b.children:
        return int(a.type != b.type)

    if (a.pattern_type == PatternType.STATIC) \
    and (b.pattern_type == PatternType.STATIC):
        return int(a.hash != b.hash)

    return 1

def distance(patternA: List[Token], patternB: List[Token]):
    """ Calculate the distance between two patterns."""

    len_s1 = len(patternA)
    len_s2 = len(patternB)

    column = list(range(0, len_s1+1))
    lastdiag = 0
    x = 1
    while x <= len_s2:
        column[0] = x
        lastdiag = x - 1
        y = 1
        while y <= len_s1:
            oldiag = column[y]
            cost = distanceTokens(patternA[y-1], patternB[x-1])
            column[y] = min(column[y]+1, column[y-1]+1, lastdiag+cost)
            lastdiag = oldiag
            y += 1
        x += 1
    return column[len_s1]
