import lexanaly
import syntaxanaly
import queue
import treap
import random
import copy

class LRitem:
    def __init__ (self,left,cursor = 0, tokens = [], lookAheads = set()):
        self.cursor = cursor
        self.left = left
        self.tokens = tokens
        self.lookAheads = lookAheads
        self.ruleID = None
    def appendToken(self, term):
            self.tokens.append(term)

    def appendTokenSorted(self,term):
        idx = 0
        for a in self.tokens:
            if(a > term):
                break
            idx += 1
        self.tokens.insert(idx, term)
    def appendLookAhead(self,term):
        if(type(term) is str):
            self.lookAheads.add(term)
        elif(type(term) is set):
            self.lookAheads |= term
    
    def hashTokens(self):
        str = ""
        for a in self.tokens:
            str += a
        return str
    
    def hashEvery(self):
        res = ""
        res += str(self.cursor)
        res += self.left
        res += "->"
        for a in self.tokens:
            res += a
        res += "|"
        t = list(self.lookAheads)
        t.sort()
        for a in t:
            res += a
        return res
    def hashExLA(self):
        res = ""
        res += str(self.cursor)
        res += self.left
        res += "->"
        for a in self.tokens:
            res += a
        return res
    def putRuleID(self, n):
        self.ruleID = n
    

class DFANode:
    def __init__ (self, items = []):
        self.items = items
        self.edge = None
        self.ID = None
    
    def appendItem(self, item) :
        if type(item) is LRitem :
            self.items.append(item)
        elif type(item) is list :
            self.items |= item

    def hashEverySorted(self) :
        tl = []
        for i in self.items :
            tl.append(i.hashEvery())
        tl.sort()
        res = ""
        for i in tl:
            res += i
            res += "/"
        return res
    def hashExLASorted(self) :
        tl = []
        for i in self.items :
            tl.append(i.hashExLA())
        tl.sort()
        res = ""
        for i in tl:
            res += i
            res += "/"
        return res
    
    def closerDeploy (self):
        syn = syntaxanaly.syntaxHelper(syntaxanaly.synList)
        templist = []
        for i in self.items :
            for a in i.lookAheads:
                s = set()
                s.add(a)
                l = LRitem(i.left,i.cursor,i.tokens,s)
                l.putRuleID(i.ruleID) #忘れずに
                templist.append(l)
        #laを分解し、各アイテムはただ一つだけのlookaheadsを持つ
        q = queue.Queue()
        adhoc = treap.oreTreap() #重複管理
        for i in templist :
            q.put(i)
            adhoc.add(random.random(), i.hashEvery())
        while not q.empty():
            i = q.get()
            if i.cursor == len(i.tokens) :
                continue
            token = i.tokens[i.cursor]
            ridx = 0
            for r in syntaxanaly.synList : 
                if token == r.ltoken :
                    feedTofirst = i.tokens[i.cursor+1:]
                    feedTofirst += list(i.lookAheads)
                    la = syn.funcFirst(feedTofirst)
                    L = LRitem(token,0,r.pattern,la)
                    L.putRuleID(ridx)
                    if adhoc.find(L.hashEvery()) is not None :
                        continue
                    adhoc.add(random.random(), L.hashEvery())
                    q.put(L)
                    templist.append(L)
                ridx += 1
        adhoc = treap.oreTreap() 
        res = []
        for i in templist :
            t = adhoc.add(random.random(), i.hashExLA())
            g = t.getObject()
            if g is None :
                t.assign(i)
                res.append(i)
            else :
                g.lookAheads |= i.lookAheads
        self.items = res

    def progAndSlice (self) :
        synRules = list(syntaxanaly.synList)
        #値のコピー
        syn = syntaxanaly.syntaxHelper(synRules)
        t = copy.deepcopy(self.items)
        t2 = []
        for i in t :
            i.cursor += 1
            ##if i.cursor < len(i.tokens) and i.tokens[i.cursor] in syn.terminal :
            ##        continue
            if i.cursor <= len(i.tokens):
                t2.append(i)
        res = {}
        for i in t2:
            label = i.tokens[i.cursor - 1]
            if label not in res :
                res[label] = DFANode([])
                res[label].appendItem(i)
            else :
                res[label].appendItem(i)
        self.edge = res
        return res
    
    def assignID(self, n) :
        self.ID = n


class perserGenerator:
    def __init__ (self):
        self.Root = DFANode([LRitem("START",0,["E"],set(['EOF']))])
        self.Root.closerDeploy()
        self.DFAs = treap.oreTreap()
        n = self.DFAs.add(random.random(),self.Root.hashEverySorted())
        n.assign(self.Root)
        self.Root.progAndSlice()
        self.deployR(self.Root.edge) 
        
    def deployR (self, u):
        o = self.DFAs.n
        for e in u.values():    
            t = self.DFAs.add(random.random(),e.hashEverySorted())
            if t.getObject() is None :
                t.assign(e)
            else :
                e = t.getObject()
                
        if self.DFAs.n <= o :
            return
        for e in u.values():
            e.closerDeploy()
            e.progAndSlice()
            self.deployR(e.edge)

    def mergeDFAs(self) :
        self.DFAsExLA = treap.oreTreap()
        self.travAndMerge(self.Root)

    def travAndMerge(self, u):
        t = self.DFAsExLA.add(random.random(),u.hashExLASorted())
        if t.getObject() is None :
            t.assign(u)
            u.assignID(t.putID())
        else :
            o = t.getObject()
            self.mergeDFA(u ,o)
            u.assignID(t.putID())
        if u.edge is None :
            return
        else :
            for e in u.edge.values() :
                self.travAndMerge(e)
    def mergeDFA(self,u ,w) :
        #u←w uがwを吸収合併
        for i in u.items :
            for j in w.items :
                if i.tokens == j.tokens :
                    i.lookAheads |= j.lookAheads
                    j.lookAheads = i.lookAheads
    
    def travAndMakeTables(self) :
        self.LALRt = LALRtable()
        self.Gotot = LALRtable()
        self.maket(self.Root)

    def maket(self,u) :
        if u is None:
            return
        syn = syntaxanaly.syntaxHelper(syntaxanaly.synList)
        #shift and goto commands
        if u.edge is not None:
            for k in u.edge.keys():
                if syn.isTerminal(k) :
                    c = LALRcommand()
                    c.setparam("shift", u.edge[k].ID)
                    self.LALRt.setCommand(u.ID, k, c)
                elif syn.isNonterminal(k) :
                    c = LALRcommand()
                    c.setparam("goto", u.edge[k].ID)
                    self.Gotot.setCommand(u.ID, k, c)
        #reduce and accept commands
        for i in u.items :
            if i.cursor < len(i.tokens) :
                continue
            else :
                if i.ruleID is None :
                    c = LALRcommand()
                    c.setparam("accept", i.ruleID)
                    for la in i.lookAheads :
                        self.LALRt.setCommand(u.ID, la, c)
                else :
                    c = LALRcommand()
                    c.setparam("reduce", i.ruleID)
                    for la in i.lookAheads :
                        self.LALRt.setCommand(u.ID, la, c)
        if u.edge is not None:
            for p in u.edge.values() :
                self.maket(p)

            


class LALRcommand:
    def __init__(self) :
        self.command = None
        self.ref = None
    def setparam(self, c, r):
        self.command = c
        self.ref = r
    def hashcommand(self) :
        s = "" + str(self.command) + ":" + str(self.ref)
        return s

class LALRtable:
    def __init__(self) :
        syn = syntaxanaly.syntaxHelper(syntaxanaly.synList)
        self.alltoken = syn.terminal | syn.nonterminal | {"EOF"}
        self.t = {}

    def setCommand(self, row, column, command):
        assert column in self.alltoken, 'Theres nothing such word as {0}'.format(column)
        if str(row) not in self.t.keys() :
            self.t[str(row)] = dict()
            self.t[str(row)][column] = command
        else :
            #assert column not in self.t[str(row)].keys() , "Conflict?" + 'row {0} column {1} command {2}'.format(row, column, self.t[str(row)][column].hashcommand())
            self.t[str(row)][column] = command
    def putCommand(self, row, column):
        if self.t[str(row)][column] is None:
            return None
        else:
            return self.t[str(row)][column]
