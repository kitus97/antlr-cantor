import sys
from antlr4 import FileStream, CommonTokenStream
from cantorLexer import cantorLexer
from cantorParser import cantorParser
from visitor import CantorVisitor
from cantor_math import encode_list


def main():
    if len(sys.argv) != 2:
        print(f"[USAGE]: python cantor.py <file.cantor>", file=sys.stderr)
        sys.exit(1)
    
    input_stream = FileStream(sys.argv[1], encoding='utf-8')
    lexer = cantorLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = cantorParser(stream)
    tree = parser.program()

    visitor = CantorVisitor()
    main_func = visitor.visitProgram(tree)

    data = sys.stdin.read().split()
    encoded = encode_list([int(x) for x in data])
    result = main_func(encoded)
    print(result)

if __name__ == '__main__':
    main()
