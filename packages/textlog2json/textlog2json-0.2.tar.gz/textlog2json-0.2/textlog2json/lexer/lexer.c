#include "lexer.h"
#include <stdio.h>
#include <stdint.h>
#include <ctype.h>

// Although PyUnicode_FromString and PyUnicode_DecodeUTF8 are marked deprecated this is the way to go:
// https://stackoverflow.com/a/36099157/1245992

#include "lex.yy.h"
#include "token_type.h"
#include "crc32.h"

struct TokenObject* addChild(struct TokenObject *parent, const char* text, int tokenType);
static void endAll(struct TokenStack *tokenStack);

const char *WhitespacePrefixRegexpMixed = "\\s*";
const char *WhitespacePrefixRegexpSpace = " ";
const char *WhitespacePrefixRegexpTab = "\t";
const char *WhitespacePrefixRegexpEmpty = "";

char* strcpy_schlemiel( char* dest, char* src )
{
     while (*src != 0) {
        *dest++ = *src++;
     }
     *dest = 0;
     return dest;
}

/**
 * Create a new token.
 */
struct TokenObject* newToken(const char *text, int tokenType) {
    struct TokenObject *token = malloc(sizeof(struct TokenObject));
    if (token == 0) {
        goto newToken_error;
    }
    memset(token, 0, sizeof(struct TokenObject));

    token->whitespace_prefix_regexp = WhitespacePrefixRegexpEmpty;
    size_t whitespaceLength = 0;
    if (text[0] != '\0' && isspace(text[0])) {
        switch (text[0]) {
            case ' ':
                token->whitespace_prefix_regexp = WhitespacePrefixRegexpSpace;
                break;
            case '\t':
                token->whitespace_prefix_regexp = WhitespacePrefixRegexpTab;
                break;
            default:
                token->whitespace_prefix_regexp = WhitespacePrefixRegexpMixed;
        }

        for (
            whitespaceLength = 1;
            text[whitespaceLength] != '\0' && isspace(text[whitespaceLength]);
            whitespaceLength++
        ) {
            token->whitespace_prefix_regexp = WhitespacePrefixRegexpMixed;
        }
    }

    token->type = tokenType;

    token->text = malloc(strlen(&text[whitespaceLength])+1);
    if (token->text == 0) { goto newToken_error_1; }
    strcpy(token->text, &text[whitespaceLength]);

    token->whitespace_prefix = malloc(whitespaceLength+1);
    if (token->whitespace_prefix == 0) { goto newToken_error_2; }
    strncpy(token->whitespace_prefix, text, whitespaceLength);
    token->whitespace_prefix[whitespaceLength] = 0;

    token->pattern_name = "";
    token->hash = Crc32_ComputeBuf(0, &text[whitespaceLength], strlen(&text[whitespaceLength]));

    return token;

    newToken_error_2:
        free(token->text);

    newToken_error_1:
        free(token);

    newToken_error:
        return  0;
}

/**
 * Add a child token to a token.
 */
struct TokenObject* addChild(struct TokenObject *parent, const char* text, int tokenType) {
    struct TokenObject *child = newToken(text, tokenType);
    if (child == 0) {
        goto addChild_error;
    }

    if (parent->last_child == 0) {
        parent->first_child = child;
        parent->last_child = child;
    } else {
        parent->last_child->next = child;
        parent->last_child = child;
    }

    return child;

    addChild_error:
        return 0;
}

/**
 * Concat the text of all children and append that to the parent.
 */
int addTextOfChildren(struct TokenObject *parent) {
    if (parent->first_child == 0) {
        return 0;
    }

    // Calculate the necessary combined text length.
    struct TokenObject *child = parent->first_child;
    size_t size = strlen(child->text);
    for (child = child->next; child != 0; child = child->next) {
        size += strlen(child->whitespace_prefix);
        size += strlen(child->text);
    }

    // Allocate memory:
    char *text = malloc(size + 1);
    if (text == 0) {
        goto addTextOfChildren_error;
    }

    // Append texts.
    child = parent->first_child;
    char* ctext = strcpy_schlemiel(text, child->text);
    for (child = child->next; child != 0; child = child->next) {
        ctext = strcpy_schlemiel(ctext, child->whitespace_prefix);
        ctext = strcpy_schlemiel(ctext, child->text);
    }

    parent->hash = Crc32_ComputeBuf(0, text, size);

    size_t whitespace_prefix_length = strlen(parent->first_child->whitespace_prefix);
    char *whitespace_prefix = malloc(whitespace_prefix_length+1);
    if (whitespace_prefix == 0) {
        goto addTextOfChildren_error_1;
    }
    strncpy(whitespace_prefix, parent->first_child->whitespace_prefix, whitespace_prefix_length);
    whitespace_prefix[whitespace_prefix_length] = 0;

    free(parent->whitespace_prefix);
    parent->whitespace_prefix = whitespace_prefix;

    free(parent->text);
    parent->text = text;

    parent->whitespace_prefix_regexp = parent->first_child->whitespace_prefix_regexp;
    return 0;

    addTextOfChildren_error_1:
        free(text);

    addTextOfChildren_error:
        return 1;
}

void stackToken(const char *text, int tokenType, struct TokenStack *tokenStack) {
    // create outer token.
    struct TokenObject *token = addChild(tokenStack->tokenStack[tokenStack->tokenStackIndex], "", tokenType);
    if (token == 0) {
        goto stackToken_error;
    }

    // create inner token
    struct TokenObject *child = addChild(token, text, CharToken);
    if (child == 0) {
        goto stackToken_error;
    }

    if (++(tokenStack->tokenStackIndex) >= MAX_NESTING) {
        tokenStack->tokenStack[0]->errormsg = "reached maximum level of nesting";
        goto stackToken_error;
    }

    tokenStack->tokenStack[tokenStack->tokenStackIndex] = token;

    return;

    stackToken_error:
        tokenStack->tokenStack[0]->errormsg = "failed to stack token";
        return;
}

void addToken(const char *text, int tokenType, struct TokenStack *tokenStack) {
    struct TokenObject *child = addChild(tokenStack->tokenStack[tokenStack->tokenStackIndex], text, tokenType);
    if (child == 0) {
        goto addToken_error;
    }

    return;

    addToken_error:
        tokenStack->tokenStack[0]->errormsg = "failed to add token to token stack";
        return;
}

int popToken(const char *text, int tokenType, struct TokenStack *tokenStack) {
	// Try to close parenthesis and quotes.
	// Ignore missing closing parenthesis in enclosed texts.
	for (int i = tokenStack->tokenStackIndex; i >= 0; i--) {
        long childType = tokenStack->tokenStack[i]->type;
		if (childType == tokenType) {
            // Create an inner token with the closing character.
            struct TokenObject *child = addChild(tokenStack->tokenStack[i], text, CharToken);
            if (child == 0) {
                goto popToken_error;
            }

            // Pop all elements on the stack up to the current token.
            do{
                if (addTextOfChildren(tokenStack->tokenStack[tokenStack->tokenStackIndex]) != 0) {
                    goto popToken_error;
                }
            } while((tokenStack->tokenStackIndex)-- > i);

            return 1;
        }

        // parenthesis, Braces and other types of quotes in quotes
        // can't close elements outside of quotes.
        else if (childType == DoubleQuotesToken || childType == SingleQuotesToken) {
            return 0;
		}
	}

	return 0;

    popToken_error:
        tokenStack->tokenStack[0]->errormsg = "failed to pop token from token stack";
        return -1;
}

// Close all open tokens on the stack except for the root token.
static void endAll(struct TokenStack *tokenStack) {
    do {
        addTextOfChildren(tokenStack->tokenStack[tokenStack->tokenStackIndex]);
    } while((tokenStack->tokenStackIndex)-- > 0);
}

// Free token.
void freeToken(struct TokenObject *token) {
    struct TokenObject *child = token->first_child;
    while (child != 0) {
        struct TokenObject *new_child = child->next;
        freeToken(child);
        child = new_child;
    }

    free(token->text);
    free(token->whitespace_prefix);
    free(token);
}

// Parse tokens.
struct TokenObject* parse(const char *text) {
    struct TokenObject *rootToken = newToken("", RootToken);
    if (rootToken == 0) {
        goto parse_error;
    }

    struct TokenStack tokenStack = {{0}, 0};
    tokenStack.tokenStack[0] = rootToken;

    yyscan_t scanner;
    yylex_init(&scanner);
    yyset_extra(&tokenStack, scanner);

    YY_BUFFER_STATE buffer = yy_scan_bytes(text, strlen(text)+1, scanner); // include \0 char
    yylex(scanner);
    yy_delete_buffer(buffer, scanner);
    yylex_destroy(scanner);

    if (rootToken->errormsg != 0) {
        goto parse_error_1;
    }

    endAll(&tokenStack);
    return rootToken;

    parse_error_1:
        freeToken(rootToken);

    parse_error:
        return 0;
}
