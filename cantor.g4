grammar cantor;

// ── Parser ──────────────────────────────────────────────

program
    : main_dir definition* EOF
    ;

main_dir
    : MAIN ID
    ;

definition
    : DEFINE ID doc body
    ;

doc
    : DOC
    ;

body
    : PAIR ID ID
    | COMP ID ID
    ;

// ── Lexer ────────────────────────────────────────────────

MAIN   : 'main' ;
DEFINE : 'define' ;
PAIR   : 'pair' ;
COMP   : 'comp' ;

ID     : [a-zA-Z_][a-zA-Z0-9_]* ;
DOC    : '[' ~[\]]* ']' ;

COMMENT : '#' ~[\r\n]* -> skip ;
WS      : [ \t\r\n]+   -> skip ;