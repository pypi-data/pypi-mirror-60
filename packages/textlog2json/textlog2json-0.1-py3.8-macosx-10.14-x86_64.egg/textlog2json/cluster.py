from typing import Optional, List
from uuid import UUID
import random
from textlog2json.lexer.token import Token
from textlog2json.pattern_format import pattern_serialize
from hashlib import md5

class Cluster():
    def __init__(self, pattern: Optional[List[Token]]):
        self.guid = (UUID(int=random.getrandbits(128), version=4)).bytes.hex()
        self.name = None
        self.counter = 0

        if pattern is None:
            self.pattern = []
        else:
            self.pattern = pattern

    def serializePattern(self) -> str:
        """ Serialize pattern to json and calcualte a hash """

        pattern_json = pattern_serialize(self.pattern)
        self.pattern_hash = md5(pattern_json.encode()).hexdigest()
        return pattern_json
