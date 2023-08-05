#ifndef LEXER_H
#define LEXER_H

struct TokenObject {
    int type;
    char *text;
    char *whitespace_prefix;
    const char *whitespace_prefix_regexp;
    int pattern_type;
    char *pattern_name;
    unsigned long hash;
    struct TokenObject *first_child;
    struct TokenObject *last_child;
    struct TokenObject *next;
    const char *errormsg;
};

// Log messages really shouldn't use more than 10 layers of nesting.
#define MAX_NESTING 100

struct TokenStack {
    struct TokenObject* tokenStack[MAX_NESTING];
    int tokenStackIndex;
};

void addToken(const char *text, int tokenType, struct TokenStack *tokenStack);
void stackToken(const char *text, int tokenType, struct TokenStack *tokenStack);
 int popToken(const char *text, int tokenType, struct TokenStack *tokenStack);
struct TokenObject* parse(const char *c);
void freeToken(struct TokenObject *token);

// Prevent unistd.h from being included by flex
#define YY_NO_UNISTD_H 1

#endif
