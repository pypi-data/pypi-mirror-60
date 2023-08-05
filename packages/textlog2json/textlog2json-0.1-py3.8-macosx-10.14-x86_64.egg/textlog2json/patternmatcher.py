# Scores the distance between two token streams and creates regular expressions from them.
# Basically uses Needleman–Wunsch algorithm.

from textlog2json.lexer.token_type import TokenType
from textlog2json.lexer.token import Token
from typing import List
from textlog2json.distance import distanceTokens
from textlog2json.pattern_type import PatternType

TRANSITION = 0 # identical or substitution
INSERTION  = 1
DELETION   = 2

# Punishment values
MATCH_PUNISHMENT    = -2
MISMATCH_PUNISHMENT = 4
GAP_START_PUNISHMENT = 3
GAP_EXTENSION_PUNISHMENT = 1

# Matrix used to merge pattern types on transitions.
TransitionTypeMergingMatrix = [0]*(PatternType.LENGTH*PatternType.LENGTH)

TransitionTypeMergingMatrix[PatternType.LENGTH*PatternType.STATIC + PatternType.STATIC] = PatternType.ONCE
TransitionTypeMergingMatrix[PatternType.LENGTH*PatternType.STATIC + PatternType.ONCE] = PatternType.ONCE
TransitionTypeMergingMatrix[PatternType.LENGTH*PatternType.STATIC + PatternType.MULTIPLE] = PatternType.MULTIPLE

TransitionTypeMergingMatrix[PatternType.LENGTH*PatternType.ONCE + PatternType.STATIC] = PatternType.ONCE
TransitionTypeMergingMatrix[PatternType.LENGTH*PatternType.ONCE + PatternType.ONCE] = PatternType.ONCE
TransitionTypeMergingMatrix[PatternType.LENGTH*PatternType.ONCE + PatternType.MULTIPLE] = PatternType.MULTIPLE

TransitionTypeMergingMatrix[PatternType.LENGTH*PatternType.MULTIPLE + PatternType.STATIC] = PatternType.MULTIPLE
TransitionTypeMergingMatrix[PatternType.LENGTH*PatternType.MULTIPLE + PatternType.ONCE] = PatternType.MULTIPLE
TransitionTypeMergingMatrix[PatternType.LENGTH*PatternType.MULTIPLE + PatternType.MULTIPLE] = PatternType.MULTIPLE


# Matrix used when merging two tokens.
TypeMergingMatrix = [0]*(TokenType.TokenLength*TokenType.TokenLength)

wordToken = [
    TokenType.WordToken,
    TokenType.IntToken,
    TokenType.NumberToken,
    TokenType.LoglevelToken,
    TokenType.Base16NumberToken,
    TokenType.Base16FloatToken,
]

noSpaceToken = [
    TokenType.NoSpecialToken,
    TokenType.WordToken,
    TokenType.SeparatorToken,
    TokenType.CharToken,
    TokenType.NoSpaceToken,
    TokenType.DateToken,
    TokenType.TimeToken,
    TokenType.IntToken,
    TokenType.IPToken,
    TokenType.NumberToken,
    TokenType.UUIDToken,
    TokenType.MacToken,
    TokenType.LoglevelToken,
    TokenType.Base16NumberToken,
    TokenType.Base16FloatToken,
    TokenType.GermanNumberToken,
]

for typeA in range(0, TokenType.TokenLength):
    for typeB in range(0, TokenType.TokenLength):
        if typeA == typeB:
            TypeMergingMatrix[TokenType.TokenLength*typeA + typeB] = typeA
        elif (typeA in wordToken) and (typeB in wordToken):
            TypeMergingMatrix[TokenType.TokenLength*typeA + typeB] = TokenType.WordToken
        elif (typeA in noSpaceToken) and (typeB in noSpaceToken):
            TypeMergingMatrix[TokenType.TokenLength*typeA + typeB] = TokenType.NoSpaceToken
        else:
            TypeMergingMatrix[TokenType.TokenLength*typeA + typeB] = TokenType.GreedyToken

def _alignmentMatrix(patternA: List[Token], patternB: List[Token]):
    """ Align two patterns and calculate the alignment matrix for them """

    aLen = len(patternA) + 1
    bLen = len(patternB) + 1

    scoringMatrix = [0]*(aLen*bLen)
    alignmentMatrix = [0]*(aLen*bLen)

    # Init the axes of the alignment and scoring matrices.
    scoringMatrix[0] = MATCH_PUNISHMENT

    i = 1
    while i < aLen:
        scoringMatrix[bLen*i] = GAP_EXTENSION_PUNISHMENT * i
        alignmentMatrix[bLen*i] = DELETION
        i += 1
    j = 1
    while j < bLen:
        scoringMatrix[j] = GAP_EXTENSION_PUNISHMENT * j
        alignmentMatrix[j] = INSERTION
        j += 1

    # Calculate the scoring matrix and the alignment matrix (used for backtracking).
    # Do this in reverse order, so that we can append instead of prepend to pattern when backtracking.
    row = 1
    indexA = len(patternA) - 1
    while row < aLen:
        col = 1
        indexB = len(patternB) - 1
        while col < bLen:
            if distanceTokens(patternA[indexA], patternB[indexB]) < 1:
                transitionCost = MATCH_PUNISHMENT
            else:
                transitionCost = MISMATCH_PUNISHMENT

            if (alignmentMatrix[bLen*row + (col-1)] != TRANSITION) \
            or (indexB < len(patternB) and (patternB[indexB + 1].pattern_type == PatternType.MULTIPLE)):
                inCost = GAP_EXTENSION_PUNISHMENT
            else:
                inCost = GAP_START_PUNISHMENT

            if (alignmentMatrix[bLen*(row-1) + col] != TRANSITION) \
            or (indexA < len(patternA) and (patternA[indexA + 1].pattern_type == PatternType.MULTIPLE)):
                delCost =  GAP_EXTENSION_PUNISHMENT
            else:
                delCost = GAP_START_PUNISHMENT

            transition = scoringMatrix[bLen*(row-1) + (col-1)] + transitionCost
            insertion  = scoringMatrix[bLen*(row)   + (col-1)] + inCost
            deletion   = scoringMatrix[bLen*(row-1) + (col)] + delCost

            if (transition <= deletion) and (transition <= insertion):
                scoringMatrix[bLen*row + col] = transition
                alignmentMatrix[bLen*row + col] = TRANSITION
            elif deletion < insertion:
                scoringMatrix[bLen*row + col] = deletion
                alignmentMatrix[bLen*row +col] = DELETION
            else:
                scoringMatrix[bLen*row + col] = insertion
                alignmentMatrix[bLen*row + col] = INSERTION

            col, indexB = col+1, indexB-1
        row, indexA = row+1, indexA-1
    return alignmentMatrix

def MergePatterns(basePattern: List[Token], newPattern: List[Token]) -> List[Token]:
    """ Merges a new patterns into a new one. The text value is set to the values of newPattern. """

    prefix, innerA, innerB, suffix = _extractPrefixAndSuffix(basePattern, newPattern)

    pattern = prefix
    alignmentMatrix = _alignmentMatrix(innerA, innerB)
    bLen = len(innerB)+1

    # Backtrack the alignment matrix
    row = len(innerA)
    col = len(innerB)
    indexA = 0
    indexB = 0

    lastOperation = TRANSITION
    while (row > 0) or (col > 0):
        operation = alignmentMatrix[(row*bLen)+(col)]

        if operation == TRANSITION:
            if (innerA[indexA].pattern_type == PatternType.STATIC) \
            and (innerB[indexB].pattern_type == PatternType.STATIC) \
            and (innerA[indexA].text == innerB[indexB].text):
                pattern.append(innerB[indexB])
            else:
                token = _mergeTokens(innerA[indexA], innerB[indexB])
                pattern.append(token)

            row, col = row-1, col-1
            indexA, indexB = indexA+1, indexB+1

        elif operation == DELETION:
            if (len(pattern) == 0) or (pattern[-1].pattern_type != PatternType.MULTIPLE):
                t = Token()
                t.type = innerA[indexA].type
                t.text = ""
                t.hash = 0
                t.whitespace_prefix = ""
                t.whitespace_prefix_regexp = innerA[indexA].whitespace_prefix_regexp
                t.pattern_type = PatternType.MULTIPLE
                t.pattern_name = innerA[indexA].pattern_name
                t.children = []
                pattern.append(t)
            else:
                pattern[-1] = _mergeTokens(innerA[indexA], pattern[-1])

            row = row-1
            indexA = indexA+1

        elif operation == INSERTION:
            if (len(pattern) == 0) or (pattern[-1].pattern_type != PatternType.MULTIPLE):
                t = Token()
                t.type = innerB[indexB].type
                t.text = innerB[indexB].text
                t.hash = 0
                t.whitespace_prefix = innerB[indexB].whitespace_prefix
                t.whitespace_prefix_regexp = innerB[indexB].whitespace_prefix_regexp
                t.pattern_type = PatternType.MULTIPLE
                t.pattern_name = ""
                t.children = []
                pattern.append(t)
            else:
                if pattern[-1].text == "":
                    pattern[-1] = _mergeTokens(
                        innerB[indexB], pattern[-1],
                        text=innerB[indexB].text,
                        whitespace_prefix=innerB[indexB].whitespace_prefix
                    )
                else:
                    text = pattern[-1].text + innerB[indexB].whitespace_prefix + innerB[indexB].text
                    pattern[-1] = _mergeTokens(innerB[indexB], pattern[-1], text=text)

            col = col-1
            indexB = indexB+1

        lastOperation = operation

    pattern += suffix
    return pattern

def _extractPrefixAndSuffix(patternA: List[Token], patternB: List[Token]) -> tuple:
    """ Extract the common prefix and suffix of two patterns. """

    # Find common prefix
    offset = 0
    while ((offset < len(patternA)) and (offset < len(patternB))):
        if (patternA[offset].pattern_type != PatternType.STATIC) \
        or (patternB[offset].pattern_type != PatternType.STATIC) \
        or (patternA[offset].text != patternB[offset].text):
            break
        offset += 1


    endA, endB = len(patternA)-1, len(patternB) -1
    while endA >= offset and endB >= offset:
        if (patternA[endA].pattern_type != PatternType.STATIC) \
        or (patternB[endB].pattern_type != PatternType.STATIC) \
        or (patternA[endA].text != patternB[endB].text):
            break
        endA, endB = endA-1, endB-1

    prefix = patternA[0:offset]
    innerA = patternA[offset:endA+1]
    innerB =  patternB[offset:endB+1]
    suffix = patternA[endA+1:]

    return (prefix, innerA, innerB, suffix)

def _mergeTokens(a:Token, b:Token, text:str=None, whitespace_prefix:str=None) -> Token:
    """ Merge two tokens """
    t = Token()

    t.hash = 0
    t.type = TypeMergingMatrix[TokenType.TokenLength * a.type + b.type]
    t.pattern_type = TransitionTypeMergingMatrix[PatternType.LENGTH*a.pattern_type + b.pattern_type]

    if a.pattern_name:
        t.pattern_name = a.pattern_name
    else:
        t.pattern_name = b.pattern_name

    if a.whitespace_prefix_regexp == b.whitespace_prefix_regexp:
        t.whitespace_prefix_regexp = a.whitespace_prefix_regexp
    else:
        t.whitespace_prefix_regexp = '\\s*'

    if text == None:
        t.text = b.text
    else:
        t.text = text

    if whitespace_prefix == None:
        t.whitespace_prefix = b.whitespace_prefix
    else:
        t.whitespace_prefix = whitespace_prefix

    # Merge children (for enclosures like parenthesis quotes, etc.)
    if len(a.children) > 0 and len(b.children) > 0:
        t.children = MergePatterns(a.children, b.children)
    else:
        t.children = []

    return t
