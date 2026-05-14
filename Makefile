ANTLR_JAR = antlr-4.13.2-complete.jar
GRAMMAR = cantor.g4

all: $(GRAMMAR)
	java -jar $(ANTLR_JAR) -Dlanguage=Python3 -visitor $(GRAMMAR)

clean:
	rm -f *.interp *.tokens cantorLexer.py cantorParser.py cantorListener.py cantorVisitor.py
