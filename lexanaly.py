import regex
from collections import deque

class lex:
    def __init__(self, name, pattern, flag = 0):
        self.name = name
        self.pattern = pattern
        self.r = regex.compile(pattern, flag)
    def recompile(self,pattern = '', flag = 0):
        if pattern == '':
            return
        else:
            self.r = regex.compile(pattern, flag)

LexDefs = []
LexDefs.append(lex("Num", '[0-9]'))
LexDefs.append(lex("*", '\*'))
LexDefs.append(lex("+", '\+'))
LexDefs.append(lex(None, '\s'))

class token:
    def __init__(self, category, value):
        self.category = category
        self.value = value

class EOFtoken(token):
    def __init__(self):
        self.category = "EOF"
        self.value = None

class Lexer:
    def __init__(self, LexDefsList):
        self.LDList = LexDefsList
        for lex in self.LDList:
            lex.recompile(lex.pattern, regex.IGNORECASE)
    def read(self, str):
        tokenDeque = deque()
        c = 0
        while c < len(str):
            t = str[c:]
            for pattern in self.LDList:
                m = pattern.r.match(t)
                if m != None and pattern.name != None:
                    tokenDeque.append(token(pattern.name, m.group()))
                    c += len(m.group())  
                    break
                elif pattern.name == None:
                    c += len(m.group())
                    break
        tokenDeque.append(EOFtoken())
        return tokenDeque
