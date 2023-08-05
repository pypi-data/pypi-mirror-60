from textlog2json.lexer.token import Token
from textlog2json.lexer.token_type import TokenType, token_type_to_string
from textlog2json.pattern_type import PatternType
from typing import List,Dict
import json

def PatternValuesAddToDict(output: Dict, pattern: List[Token]):
    """ Populates given dict with the values found in given pattern """
    tokenTypeCount = [1]*TokenType.TokenLength
    return _pattern_values_add_to_dict(output, pattern, tokenTypeCount)

def _pattern_values_add_to_dict(output: Dict, pattern: List[Token], tokenTypeCount):
    for token in pattern:
        if token.pattern_type != PatternType.STATIC:
            _pattern_values_add_to_dict(output, token.children, tokenTypeCount)
            name =_tokenToPatternName(token, tokenTypeCount)
            if name != "_":
                for n in name.split(','):
                    output[n] = token.text

def _tokenToPatternName(token: Token, tokenTypeCount) -> (str):
    if token.pattern_name != "":
        return token.pattern_name
    else:
        s = token_type_to_string(token.type) + str(tokenTypeCount[token.type])
        tokenTypeCount[token.type] += 1
        return s

def pattern_serialize(pattern: List[Token]) -> str:
    """ Serialize pattern to json """
    return json.dumps(_pack_pattern(pattern))

def _pack_pattern(pattern: List[Token]) -> list:
    data = []
    for t in pattern:
        text = ""
        whitespace_prefix = ""
        data.append({
            "type": t.type,
            "text": t.text,
            "hash": t.hash,
            "children": _pack_pattern(t.children),
            "whitespace_prefix": t.whitespace_prefix,
            "whitespace_prefix_regexp": t.whitespace_prefix_regexp,
            "pattern_type": t.pattern_type,
            "pattern_name": t.pattern_name,
        })
    return data

def pattern_deserialize(text: str) -> List[Token]:
    """ Deserialize pattern from json """

    data = json.loads(text)
    return _unpack_pattern(data)

def _unpack_pattern(l: list) -> List[Token]:
    tokens = []

    if not isinstance(l, list):
        raise Exception('malformed pattern')

    for c in l:
        if not (
            isinstance(c, dict)
            and ('type' in c) and ('text' in c) and ('children' in c) and ('whitespace_prefix' in c)
            and ('whitespace_prefix_regexp' in c) and ('pattern_type' in c) and ('pattern_name' in c)
            and isinstance(c['type'], int)
            and isinstance(c['text'], str)
            and isinstance(c['hash'], int)
            and isinstance(c['children'], list)
            and isinstance(c['whitespace_prefix'], str)
            and isinstance(c['whitespace_prefix_regexp'], str)
            and isinstance(c['pattern_type'], int)
            and isinstance(c['pattern_name'], str)
        ):
            raise Exception('malformed pattern')

        t = Token()
        t.type = c['type']
        t.text = c['text']
        t.children = _unpack_pattern(c['children'])
        t.whitespace_prefix = c['whitespace_prefix']
        t.whitespace_prefix_regexp = c['whitespace_prefix_regexp']
        t.pattern_type = c['pattern_type']
        t.pattern_name = c['pattern_name']
        t.hash = c['hash']
        tokens.append(t)

    return tokens

