from cffi import FFI
import os

ffi = FFI()

with open("textlog2json/lexer/lexer.h") as lexer_h:
    ffi.set_source("textlog2json.lexer._loglexer",
        lexer_h.read(),
        sources=['textlog2json/lexer/lexer.c', 'textlog2json/lexer/lex.yy.c', 'textlog2json/lexer/crc32.c'],
        extra_compile_args=["-std=c99"]
        #libraries=["c"],
    )

ffi.cdef("""
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

    struct TokenObject* parse(const char *c);
    void freeToken(struct TokenObject *token);
""")

# if os.system('flex lexer.lex') != 0:
#     raise Exception('flex failed to run')

if __name__ == "__main__":
    os.chdir(os.path.join(os.path.dirname(__file__), '../..'))
    ffi.compile(verbose=True)
