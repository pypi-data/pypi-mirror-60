#ifndef TOKEN_TYPE_H
#define TOKEN_TYPE_H

#define RootToken -1

enum {
    UndefinedToken,
    NoSpecialToken,
    WordToken,
    HexdumpToken,
    SeparatorToken,
    DoubleQuotesToken,
    SingleQuotesToken,
    ParenthesesToken,
    BracesToken,
    BracketsToken,
    CharToken,
    NoSpaceToken,
    GreedyToken,
    DateToken,
    TimeToken,
    DatestampToken,
    DatestampRFC2822Token,
    DatestampRFC822Token,
    DatestampOtherToken,
    DatestampEventlogToken,
    TimestampISO8601Token,
    IntToken,
    IPToken,
    NumberToken,
    UUIDToken,
    UriToken,
    MacToken,
    LoglevelToken,
    HttpdateToken,
    Base16NumberToken,
    Base16FloatToken,
    PathToken,
    GermanNumberToken,
    PriceToken,
    TokenLength
};

#endif
