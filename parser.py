import camxes
import traceback

try:
    from pudb import set_trace
    set_trace()
except:
    pass

class Node(object):
    def __init__(self, typ, content):
        self.typ = typ
        self.content = content

    def extend(self, other):
        if isinstance(self.content, list):
            self.content.append(other)
        elif isinstance(self.content, Node):
            self.content = [self.content, other]
        elif isinstance(self.content, basestring):
            if isinstance(other, basestring):
                self.content += " " + other
            else:
                self.content = [self.content, other]
        elif not self.content:
            self.content = other

    def __repr__(self):
        return "<Node %s %r>" % (self.typ, self.content)

class Tree(object):
    def __init__(self, tree, stream):
        self.tree = tree
        self.stream = stream

    def render(self, tree=None, indent=3):
        if not tree:
            return ""

        res = "    " * indent;

        if isinstance(tree, basestring):
            res += tree + "\n"
        elif isinstance(tree.content, (basestring, Token)):
            res += """<span class="%s">%s</span>\n""" % (tree.typ, str(tree.content))
        elif not tree.content:
            res += """<span class="%s"></span>""" % (tree.typ)
        elif isinstance(tree.content, list):
            res += """<span class="%(type)s">\n""" % {"type":tree.typ}
            if isinstance(tree.content, (basestring, TokenStream, Token)):
                res += "    " + str(tree.content) + "\n"
            else:
                res += " ".join([self.render(a, indent + 1) for a in tree.content])
            res += "    " * indent + """</span>\n"""
        elif isinstance(tree.content, Node):
            res += self.render(tree.content, indent)
        else:
            raise Exception

        return res

    def __str__(self):
        return """    <span class="text">
%(parsed)s
        <span class="unparsed">

        </span>
    </span>
""" % {"parsed": self.render(self.tree),
       "unparsed": str(self.stream.rest())}

    def __repr__(self):
        return "<Tree %r  %r>" % (self.tree, self.stream.rest())

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
        self.tree = Tree(None, None)

    def next(self):
        n = self.ts.next()
        print "next word: %r" % n
        traceback.print_stack()
        return n

    def peek(self):
        return self.ts.peek()

    def explain(self, text):
        add = str(self.tree) + "<br/>\n"
        add += text + "<br/><br/>\n"
        print add
        #self.output += add

    def __call__(self):
        treenode = Node("parsed", None)
        self.tree = Tree(treenode, self.ts)
        self.explain("Start with the text")

        self.parse_start(treenode)

        return self.output

    def parse_start(self, target):
        nt = self.peek()
        while nt.typ != "EOF":
            nt = self.peek()
            if nt.typ in ["COI", "DOI"]:
                self.next()
                newtarget = Node("free", nt.word)
                target.extend(newtarget)
                self.explain("%s is a vocative and starts a free" % nt.word)
                self.parse_sumti(newtarget, "vocative")
            elif nt.typ in ["LE", "LA"]:
                self.next()
                newtarget = Node("sumti", nt.word)
                target.extend(newtarget)
                self.explain("%s is a gadri and starts a sumti." % nt.word)
                self.parse_sumti(newtarget, "gadri")

    def parse_sumti(self, target, parent_rule=None):
        nt = self.peek()

        if nt.typ.startswith("KOhA"):
            target.extend(nt.word)
            self.next()
            self.explain("%s is a prosumti" % nt.word)
        elif nt.typ == "cmene" and parent_rule in ["vocative", "gadri"]:
            target.extend(nt.word)
            self.next()
            self.explain("%s in a cmevla (name-word). It gets eaten by the vocative." % nt.word)
            self.parse_cmene(target, "cmene")
        else:
            print "parse_sumti hit thin air: %r" % (nt, )
            return

        self.parse_after_sumti(target, "sumti")
        print "parse after sumti has finished"
        print self.tree
    
    def parse_cmene(self, target, parent_rule=None):
        nt = self.peek()
        if nt.typ == "CMENE":
            self.next()
            target.extend(nt.word)
            if parent_rule == "cmene":
                self.explain("%s is a cmevla, too, and gets appended to the previous one." % nt.word)
            else:
                self.explain("FIXME: explanation for parse_cmene wtih parent_rule == %s" % parent_rule)
            self.parse_cmene(target, "cmene")

    def parse_after_sumti(self, target, parent_rule=None):
        nt = self.peek()
        if nt.typ == "GOI": # pe and friends
            self.next()
            print
            print
            print self.tree
            print "parse_after_sumti appended", nt.word, "to", target
            print
            newt = Node("subsumti", nt.word)
            target.extend(newt)
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

