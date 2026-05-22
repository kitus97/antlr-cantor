grammar cantor;

// ── Parser ──────────────────────────────────────────────

program
    : main_dir extended_dir? import_dir* definition* EOF
    ;

main_dir
    : MAIN ID
    ;

extended_dir
    : EXTENDED
    ;

import_dir
    : IMPORT ID
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
    | COMPAIR ID ID ID
    | MU ID
    | PRIMREC ID ID ID
    ;

// ── Lexer ────────────────────────────────────────────────

MAIN        : 'main' ;
EXTENDED    : 'extended';
IMPORT      : 'import' ;
DEFINE      : 'define' ;
PAIR        : 'pair' ;
COMP        : 'comp' ;
COMPAIR     : 'compair' ;
MU          : 'mu' ;
PRIMREC     : 'primrec' ;

ID     : [a-zA-Z_][a-zA-Z0-9_]* ;
DOC    : '[' ~[\]]* ']' ;

COMMENT : '#' ~[\r\n]* -> skip ;
WS      : [ \t\r\n]+   -> skip ;