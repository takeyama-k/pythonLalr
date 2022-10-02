import lexanaly

class syn:
    def __init__ (self, ltoken, pattern):
        self.ltoken = ltoken
        self.pattern = pattern

synList = []
"""
synList.append(syn("EXP", ["EXP", "PLUS"]))
synList.append(syn("EXP", ["TERM"]))
synList.append(syn("TERM", ["TERM","ASTERISK","ATOM"]))
synList.append(syn("TERM", ["ATOM"]))
synList.append(syn("ATOM", ["DIGITS"]))
synList.append(syn("ATOM", ["LPAREN","EXP","RPAREN"]))

synList.append(syn("A", ["E", "=", "E"]))
synList.append(syn("A", ["Id"]))
synList.append(syn("E", ["E", "+", "T"]))
synList.append(syn("E", ["T"]))
synList.append(syn("T", ["Num"]))
synList.append(syn("T", ["Id"]))
"""

synList.append(syn("E", ["E", "+", "T"]))
synList.append(syn("E", ["T"]))
synList.append(syn("T", ["T", "*", "Num"]))
synList.append(syn("T", ["Num"]))


class syntaxHelper:
    def __init__ (self, synList):
        self.syL = synList
        self.terminal = set()
        self.nonterminal = set()
        for a in self.syL:
            self.nonterminal.add(a.ltoken)
        for a in self.syL:
            for b in a.pattern:
                self.terminal.add(b)
        self.terminal = self.terminal - self.nonterminal

        self.nulls = set()
        #nullable集合を求める
        #patternの長さがゼロのltokenはnulls
        for a in self.syL:
            if len(a.pattern) == 0:
                self.nulls.add(a.ltoken)

        #右にnullsを持つ左辺はnullable
        for a in self.syL:
            for b in a.pattern:
                if b in self.nulls:
                    self.nulls.add(a.ltoken)
        
        #first集合
        self.first = {}
        s = set()
        s.add("EOF")
        self.first["EOF"] = s

        for a in self.terminal:
            s = set()
            s.add(a)
            self.first[a] = s
        
        for a in self.nonterminal:
            self.first[a] = set()
        
        #制約の登録
        constraint = []
        for a in self.syL:
            for b in a.pattern:
                constraint.append([a.ltoken, b])
                if b not in self.nulls:
                    break

        #制約の解消
        flag = True
        while flag == True:
            flag = False
            for constr in constraint:
                sup = constr[0]
                sub = constr[1]
                ori = len(self.first[sup])
                self.first[sup] |= self.first[sub]
                if(ori > len(self.first[sup])):
                    flag = True
    #first関数
    #トークン列を受け取る
    #サニタイズとかは面倒なのでしない
    def funcFirst (self, terms):
        res = set()
        for t in terms:
            res |= self.first[t]
            if t not in self.nulls :
                return res

    def isTerminal (self, term):
        if term in self.terminal:
            return True
        else:
            return False
    def isNonterminal (self, term):
        if term in self.nonterminal:
            return True
        else:
            return False
    def getTerminal (self):
        return self.terminal
    def getNonterminal (self):
        return self.nonterminal
s = syntaxHelper(synList)
print("yey")