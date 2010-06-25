import camxes

class Token(object):
    def __init__(self, typ, word):
        if typ.startswith(("gismu", "lujvo", "fu'ivla")):
            self.typ = "BRIVLA"
        elif typ == "cmavo(s)":
            self.typ = camxes.selmaho(word)[1][0]
        self.word = word
    
    def __repr__(self):
        return "(%s \"%s\") " % (self.typ, self.word)

    def __str__(self):
        return self.word

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
        self.pos += 1
        return self.iterator.next()

    def rest(self):
        return TokenStream(self.tokens[self.pos:])

    def parsed(self):
        return TokenStream(self.tokens[:self.pos])

    def __str__(self):
        return " ".join(map(str, self.tokens))

class Parser(object):
    def __init__(self, text):
        self.ts = iter(TokenStream(text))
        self.output = ""

    def next(self):
        n = self.ts.next()
        print n
        return n

    def explain(self, text):
        self.output += "<div>" + self.render_tree() + "<br/></div>\n"
        self.output += text + "<br/><br/>\n"

    def render_tree(self, tree=None, indent=1):
        if tree is None:
            tree = ["text", ["parsed", self.tree], ["unparsed", self.ts.rest()]]
        elif not tree:
            return ""
        print "render tree ", tree
        if len(tree) == 1:
            res = "    " * indent + """<span class="leaf">%s</span>\n""" % str(tree[0])
        else:
            res = "    " * indent + """<span class="%(type)s"><h1>%(type)s</h1>\n""" % {"type":tree[0]}
            if isinstance(tree[1], (basestring, TokenStream)):
                res += "    " * (indent + 1) + str(tree[1]) + "\n"
            else:
                res += " ".join([self.render_tree(a, indent + 1) for a in tree[1:]])
            res += "    " * indent + """</span>\n"""

        return res

    def __call__(self):
        self.tree = []
        self.explain("Start with the text")

        self.parse_start(self.tree)

        return self.output

    def parse_start(self, target):
        nt = self.next()
        if nt.typ in ["COI", "DOI"]:
            newtarget = [nt.word]
            target.extend(["free", newtarget])
            self.explain("%s is a vocative and starts a free" % nt.word)
            self.parse_sumti(newtarget, "vocative")

    def parse_sumti(self, target, parent_rule=None):
        nt = self.next()
        if nt.typ.startswith("KOhA"):
            print "adding a koha."
            print self.tree
            target[0] = target[0] + " " + nt.word
            print self.tree
            self.explain("%s is a prosumti" % nt.word)

def parse(text):
    # TODO: sanitize input, use camxes/vlatai to split into words?
    r = Parser(text)
    print r()
    return r.output

if __name__ == "__main__":
    while True:
        parse(raw_input())

