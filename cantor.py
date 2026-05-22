import sys
from antlr4 import FileStream, CommonTokenStream
from antlr4.error.ErrorListener import ErrorListener
from cantorLexer import cantorLexer
from cantorParser import cantorParser
from visitor import CantorVisitor
from cantor_math import encode_list


class SyntaxErrorListener(ErrorListener):
    def syntaxError(self, _recognizer, _offendingSymbol, line, column, msg, _e):
        print(f"Error sintàctic [{line}:{column}]: {msg}", file=sys.stderr)
        sys.exit(1)


def main():
    if len(sys.argv) != 2:
        print("Ús: python cantor.py <fitxer.cantor>", file=sys.stderr)
        sys.exit(1)

    try:
        input_stream = FileStream(sys.argv[1], encoding='utf-8')
    except FileNotFoundError:
        print(f"Error: fitxer no trobat: '{sys.argv[1]}'", file=sys.stderr)
        sys.exit(1)

    lexer = cantorLexer(input_stream)
    lexer.removeErrorListeners()
    lexer.addErrorListener(SyntaxErrorListener())

    stream = CommonTokenStream(lexer)

    parser = cantorParser(stream)
    parser.removeErrorListeners()
    parser.addErrorListener(SyntaxErrorListener())

    tree = parser.program()

    try:
        visitor = CantorVisitor(sys.argv[1])
        main_func = visitor.visitProgram(tree)
    except KeyError as e:
        print(f"Error: funció no definida: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"Error: fitxer importat no trobat: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error en la definició: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        data = sys.stdin.read().split()
        encoded = encode_list([int(x) for x in data])
        result = main_func(encoded)
        print(result)
    except ValueError as e:
        print(f"Error d'entrada: {e}", file=sys.stderr)
        sys.exit(1)
    except RecursionError:
        print("Error: recursió massa profunda", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error en l'execució: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
