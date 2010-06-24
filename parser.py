import camxes

class Token(object):
    def __init__(self, typ, word):
        if typ.startswith(("gismu", "lujvo", "fu'ivla")):
            self.typ = "BRIVLA"
        elif typ == "cmavo(s)":
            self.typ = camxes.selmaho(word)[1][0]
        self.word = word
    
    def __str__(self):
        return "(%s \"%s\") " % (self.typ, self.word)

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

    def __iter__(self):
        for token in self.tokens:
            yield token
            self.pos += 1

    def rest(self):
        return TokenStream(self.tokens[self.pos:])

    def parsed(self):
        return TokenStream(self.tokens[:self.pos])

    def __str__(self):
        return " ".join(map(str, self.tokens))

class Parser(object):
    def __init__(self, text):
        self.ts = TokenStream(text)
        self.output = ""

    def render_tree(self, tree = None):
        if tree is None:
            tree = ["text", ["parsed", self.tree], ["unparsed", self.ts.rest()]]
        elif not tree:
            return ""
        print "render tree ", tree
        res = """<span class="%(type)s"><h1>%(type)s</h1>""" % {"type":tree[0]}
        if isinstance(tree[1], (basestring, TokenStream)):
            res += str(tree[1])
        elif not tree[1]:
            pass
        else:
            res += " ".join([self.render_tree(a) for a in tree[1:]])
        res += """</span>"""

        return res

    def __call__(self):
        self.tree = []
        self.output += self.render_tree()

        self.parse_sentence(self.tree)

        return self.output

    def parse_sentence(self, target):
        pass

def parse(text):
    # TODO: sanitize input, use camxes/vlatai to split into words?
    r = Parser(text)
    print r()
    return r.output

if __name__ == "__main__":
    while True:
        parse(raw_input())

