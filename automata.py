import syntaxanaly
import lexanaly
import persergen
from collections import deque

class automata:
    def __init__(self,LALRtable, Gototable, Query):
        self.synRules = syntaxanaly.synList
        self.LALRtable = LALRtable
        self.Gototable = Gototable
        self.refq = deque()
        self.refq.append(str(0))
        self.res = []
        self.Query = Query
        self.lex = lexanaly.Lexer(lexanaly.LexDefs)
        self.tokens = self.lex.read(self.Query)
    
    def progress(self) :
        nextref = self.refq[-1]
        nexttoken = self.tokens[0]
        nextcate = nexttoken.category
        nextcommand = self.LALRtable[str(nextref)][nextcate]
        if nextcommand.command == 'accept' :
            return True            
        elif nextcommand.command == 'shift' :
            nexttoken = self.tokens.popleft()
            self.refq.append(str(nextcommand.ref))
        elif nextcommand.command == 'reduce' :
            self.res.append(str(nextcommand.ref))
            l = len(self.synRules[nextcommand.ref].pattern)
            for i in range(l) :
                self.refq.pop()
            nextref = self.refq[-1]
            ltoken = self.synRules[nextcommand.ref].ltoken
            self.refq.append(self.Gototable[str(nextref)][ltoken].ref)

class ASTNode:
    def __init__(self):
        self.label = None
        self.edge = []
        self.pa = None
        self.value = None
        self.n = 0

class ASTree:
    nil = ASTNode()
    nil.label = None
    nil.edge = None
    nil.pa = None
    nil.value = None

    def __init__(self) :
        self.Root = None

    def parse(self, tokens, query, syntax) :
        isDisabled = [False]*len(tokens)
        res = [None]*len(tokens)
        
        for q in query:
            q = int(q)
            syn = syntax[q]
            ltoken = syn.ltoken
            pattern = syn.pattern
            f = None
            g = False
            for i in range(len(tokens)) :
                if isDisabled[i] == True:
                    continue
                t = tokens[i]
                cate = t.category
                value = t.value
                f = True
                if cate == pattern[0]:
                    for j in range(len(pattern)):
                        if isDisabled[i + j] == True:
                            continue
                        p = pattern[j]
                        if p != tokens[i+j].category:
                            f = False
                    if f == False:
                        continue

                    g = True
                    if res[i] is not None :
                        u = ASTNode()
                        u.label = ltoken
                        u.value = value
                        w = res[i]
                        u.edge = []
                        u.edge.append(w)
                        w.pa = u
                        res[i] = u
                        for j in range(len(pattern)):
                            if isDisabled[i + j] == True:
                                continue
                            if j == 0:
                                continue
                            if res[i+j] is not None :
                                w = res[i+j]
                                w.pa = u
                                u.edge.append(w)
                                isDisabled[i+j] = True
                            else:
                                p = pattern[j]
                                w = ASTNode()
                                w.label = p
                                w.value = tokens[i+j].value
                                w.pa = u
                                u.edge.append(w)
                                isDisabled[i+j] = True
                    else :
                        u = ASTNode()
                        u.label = ltoken
                        u.value = value
                        res[i] = u
                        for j in range(len(pattern)):
                            if isDisabled[i + j] == True:
                                continue
                            p = pattern[j]
                            if res[i+j] is not None and j != 0 :
                                w = res[i+j]
                                w.pa = u
                                u.edge.append(w)
                                isDisabled[i+j] = True
                            else:
                                w = ASTNode()
                                w.label = p
                                w.value = tokens[i+j].value
                                w.pa = u
                                u.edge.append(w)
                                isDisabled[i+j] = True
                    isDisabled[i] = False
                    tokens[i].category = ltoken
                if f == True and g == True:
                    break
        return res

p = persergen.perserGenerator()
p.mergeDFAs()
p.travAndMakeTables()

a = automata(p.LALRt.t, p.Gotot.t, "1 + 1 * 2")
r = False;
while r is not True :
    r = a.progress()
ast = ASTree()
lex = lexanaly.Lexer(lexanaly.LexDefs)
tokens = lex.read("1 + 1 * 2")
temp = ast.parse(tokens ,a.res, syntaxanaly.synList)
print("yey")