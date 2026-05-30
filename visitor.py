import itertools
import os
import sys
from antlr4 import CommonTokenStream, FileStream
from cantorLexer import cantorLexer
from cantorParser import cantorParser
from cantorVisitor import cantorVisitor
from cantor_math import pi, unpi


class CantorVisitor(cantorVisitor):

    def __init__(self, file_path):
        self.base_dir = os.path.dirname(file_path)
        self.extended = False
        self.imported = set()
        self.functions = {
            'k_1':  lambda x: 1,
            'id':   lambda x: x,
            'add':  lambda x: (lambda a, b: a + b)(*unpi(x)),
            'mul':  lambda x: (lambda a, b: a * b)(*unpi(x)),
            'diff': lambda x: (lambda a, b: max(0, a - b))(*unpi(x)),
            'fst':  lambda x: unpi(x)[0],
            'snd':  lambda x: unpi(x)[1],
        }

    def visitProgram(self, ctx):
        if ctx.extended_dir():
            self.extended = True
        for import_dir in ctx.import_dir():
            self.visitImport_dir(import_dir)
        for definition in ctx.definition():
            self.visitDefinition(definition)
        return self.visitMain_dir(ctx.main_dir())

    def visitMain_dir(self, ctx):
        return self.functions[ctx.ID().getText()]

    def visitImport_dir(self, ctx):
        name = ctx.ID().getText() + '.cantor'
        filepath = os.path.join(self.base_dir, name)

        if filepath in self.imported:
            return
        self.imported.add(filepath)

        input_stream = FileStream(filepath, encoding='utf-8')
        lexer = cantorLexer(input_stream)
        stream = CommonTokenStream(lexer)
        parser = cantorParser(stream)
        tree = parser.program()

        if tree.extended_dir():
            self.extended = True
        for import_dir in tree.import_dir():
            self.visitImport_dir(import_dir)
        for definition in tree.definition():
            self.visitDefinition(definition)

    def visitDefinition(self, ctx):
        name = ctx.ID().getText()
        if name in self.functions:
            print(f"Warning: la funció '{name}' ja està definida",
                  file=sys.stderr)
        self.functions[name] = self.visitBody(ctx.body())

    def visitBody(self, ctx):
        if ctx.ID(0):
            f = self.functions[ctx.ID(0).getText()]
        if ctx.ID(1):
            g = self.functions[ctx.ID(1).getText()]

        if ctx.PAIR():
            return lambda x: pi(f(x), g(x))
        elif ctx.COMPAIR():
            if not self.extended:
                raise RuntimeError("'compair' requereix mode extended")
            if ctx.ID(2) is None:
                raise RuntimeError("compair requereix tres funcions: compair <f> <g> <h>")
            h = self.functions[ctx.ID(2).getText()]
            return lambda x: f(pi(g(x), h(x)))
        elif ctx.MU():
            if not self.extended:
                raise RuntimeError("'mu' requereix mode extended")
            return lambda x: next(
                (k for k in itertools.count() if f(pi(x, k)) != 0), -1
            )
        elif ctx.PRIMREC():
            if not self.extended:
                raise RuntimeError("'primrec' requereix mode extended")
            if ctx.ID(2) is None:
                raise RuntimeError("primrec requereix tres funcions: primrec <f> <g> <h>")
            h = self.functions[ctx.ID(2).getText()]
            return self._make_primrec(f, g, h)
        else:
            return lambda x: f(g(x))

    def _make_primrec(self, f, g, h):
        diff = self.functions['diff']

        def predecessor(x):
            return diff(pi(x, 1))

        def s(x):
            if f(x) != 0:
                return pi(g(x), 0)
            prev = s(predecessor(x))
            return pi(h(pi(x, prev)), prev)

        return lambda x: unpi(s(x))[0]
