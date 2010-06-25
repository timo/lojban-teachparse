import camxes
import traceback

try:
    from pudb import set_trace
    set_trace()
except:
    pass

class Token(object):
    def __init__(self, typ, word):
        if typ.startswith(("gismu", "lujvo", "fu'ivla")):
            self.typ = "BRIVLA"
        elif typ == "cmavo(s)":
            self.typ = camxes.selmaho(word)[1][0]
        else:
            self.typ = typ
        self.word = word
    
    def __repr__(self):
        return "(%s \"%s\") " % (self.typ, self.word)

    def __str__(self):
        return self.word

eofToken = Token("EOF", "")

class TokenStream(object):
    def __init__(self, text_or_tokens):
        if isinstance(text_or_tokens, basestring):
            words = [camxes.call_vlatai(word) for word in text_or_tokens.split(" ")]
            self.tokens = []
            for word in words:
                self.tokens.append(Token(word[1], word[2]))
        elif isinstance(text_or_tokens, list):
            self.tokens = text_or_tokens

        self.pos = 0

        self.iterator = iter(self.tokens)

    def __iter__(self):
        return self

    def next(self):
        try:
            self.pos += 1
            return self.iterator.next()
        except:
            return eofToken

    def peek(self):
        try:
            return self.tokens[self.pos]
        except IndexError:
            return eofToken

    def rest(self):
        return TokenStream(self.tokens[self.pos:])

    def parsed(self):
        return TokenStream(self.tokens[:self.pos])

    def __str__(self):
        return " ".join(map(str, self.tokens))

    def __repr__(self):
        return self.tokens.__repr__()

class Parser(object):
    def __init__(self, text):
        self.ts = iter(TokenStream(text))
        self.output = ""

    def next(self):
        n = self.ts.next()
        print "next word: %r" % n
        traceback.print_stack()
        return n

    def peek(self):
        return self.ts.peek()

    def explain(self, text):
        add = self.render_tree() + "<br/>\n"
        add += text + "<br/><br/>\n"
        print add
        #self.output += add

    def render_tree(self, tree=None, indent=1):
        if tree is None:
            tree = ["example", ["parsed", self.tree], ["unparsed", self.ts.rest()]]
            print "render tree ", tree
        elif not tree:
            return ""
        
        if isinstance(tree, list):
            for part in tree:
                if isinstance(part, list) and len(part) == 1 and isinstance(part[0], list):
                    part.append(part.pop())
        
        if len(tree) == 1 and isinstance(tree[0], basestring):
            res = "    " * indent + """%s\n""" % str(tree[0])
        elif len(tree) == 1:
            res = "    " * indent + """<span class="%(type)s">\n""" % {"type":tree[0]}
            if isinstance(tree[1], (basestring, TokenStream)):
                res += "    " * (indent + 1) + str(tree[1]) + "\n"
            else:
                res += " ".join([self.render_tree(a, indent + 1) for a in tree[1:]])
            res += "    " * indent + """</span>\n"""

        else:
            raise Exception

        return res

    def __call__(self):
        self.tree = []
        self.explain("Start with the text")

        self.parse_start(self.tree)

        return self.output

    def parse_start(self, target):
        nt = self.peek()
        while nt.typ != "EOF":
            nt = self.peek()
            if nt.typ in ["COI", "DOI"]:
                self.next()
                newtarget = ["free", [nt.word]]
                target.append(newtarget)
                self.explain("%s is a vocative and starts a free" % nt.word)
                self.parse_sumti(newtarget, "vocative")
            elif nt.typ in ["LE", "LA"]:
                self.next()
                newtarget = ["sumti", [nt.word]]
                target.append(newtarget)
                self.explain("%s is a gadri and starts a sumti." % nt.word)
                self.parse_sumti(newtarget, "gadri")

    def parse_sumti(self, target, parent_rule=None):
        nt = self.peek()

        if nt.typ.startswith("KOhA"):
            target[1][0] = target[1][0] + " " + nt.word
            self.next()
            self.explain("%s is a prosumti" % nt.word)
        elif nt.typ == "cmene" and parent_rule in ["vocative", "gadri"]:
            target[1][0] = target[1][0] + " " + nt.word
            self.next()
            self.explain("%s in a cmevla (name-word). It gets eaten by the vocative." % nt.word)
            self.parse_cmene(target, "cmene")
        else:
            print "parse_sumti hit thin air: %r" % (nt, )
            return
 
        newt = []
        target.append(newt)
        if not self.parse_after_sumti(newt, "sumti"):
            target.remove(newt)
    
    def parse_cmene(self, target, parent_rule=None):
        nt = self.peek()
        if nt.typ == "CMENE":
            self.next()
            target[0] = target[0] + " " + nt.word
            if parent_rule == "cmene":
                self.explain("%s is a cmevla, too, and gets appended to the previous one." % nt.word)
            else:
                self.explain("FIXME: explanation for parse_cmene wtih parent_rule == %s" % parent_rule)
            self.parse_cmene(target, "cmene")

    def parse_after_sumti(self, target, parent_rule=None):
        nt = self.peek()
        if nt.typ == "GOI": # pe and friends
            self.next()
            newt = ["subsumti", [nt.word]]
            target.append(newt)
            self.explain("%s is in selma'o GOI, which append a sumti to a sumti." % nt.word)
            self.parse_sumti(newt, "subsumti")
            return True
        return False


def parse(text):
    # TODO: sanitize input, use camxes/vlatai to split into words?
    r = Parser(text)
    print r()
    return r.output

if __name__ == "__main__":
    while True:
        parse(raw_input())

