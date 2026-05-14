from cantorVisitor import cantorVisitor
from cantor_math import pi, unpi


class CantorVisitor(cantorVisitor):

    def __init__(self):
        # Taula de símbols: nom -> funció Python
        self.functions = {
            'k_1':  lambda x: 1,
            'id':   lambda x: x,
            'add':  lambda x: (lambda x1, y1: x1+y1)(*unpi(x)), 
            'mul':  lambda x: (lambda x1, y1: x1*y1)(*unpi(x)), 
            'diff': lambda x: (lambda x1, y1: max(0,x1-y1))(*unpi(x)), 
        }

    def visitProgram(self, ctx):
        for definition in ctx.definition():
            self.visitDefinition(definition)
        return self.visitMain_dir(ctx.main_dir())

    def visitMain_dir(self, ctx):
        return self.functions[ctx.ID().getText()]

    def visitDefinition(self, ctx):
        name = ctx.ID().getText()
        func = self.visitBody(ctx.body())
        self.functions[name] = func

    def visitBody(self, ctx):
        f = self.functions[ctx.ID(0).getText()]
        g = self.functions[ctx.ID(1).getText()]

        if ctx.PAIR():
            return lambda x: pi(f(x), g(x))
        else:
            return lambda x: f(g(x))