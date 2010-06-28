import camxes
import traceback

try:
    from pudb import set_trace
except:
    pass

class CancelParseException(Exception): pass

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

    def last(self):
        if isinstance(self.content, Node):
            return self.content
        elif isinstance(self.content, list):
            if not isinstance(self.content[-1], Node):
                self.content[-1] = Node("wtf", self.content[-1])
            return self.content[-1]

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
        return """    <span class="example">
%(parsed)s
        <span class="unparsed">
%(unparsed)s
        </span>
    </span><br/><br/>
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
        if not word:
            self.typ = "EOF"
    
    def __repr__(self):
        return "(%s \"%s\") " % (self.typ, self.word)

    def __str__(self):
        return self.word

eofToken = Token("EOF", "")

class TokenStream(object):
    def __init__(self, text_or_tokens):
        self.tokens = []
        if isinstance(text_or_tokens, basestring):
            words = [camxes.call_vlatai(word) for word in text_or_tokens.split(" ")]
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
        try:
            return " ".join(map(str, self.tokens))
        except:
            return "uninitialized TokenStream"

    def __repr__(self):
        try:
            return "<TokenStream of %s>" % self.tokens.__repr__()
        except:
            return "<TokenStream uninitialized>"

class Parser(object):
    def __init__(self, text):
        self.ts = iter(TokenStream(text))
        self.output = ""
        self.tree = Tree(None, None)

    def next(self):
        n = self.ts.next()
        return n

    def peek(self):
        return self.ts.peek()

    def explain(self, text):
        add = "<p>%s</p>" % text + "\n"
        add += str(self.tree) + "<br/><br/><br/>\n"
        self.output += add

    def __call__(self):
        treenode = Node("parsed", None)
        self.tree = Tree(treenode, self.ts)
        
        print
        print
        print "going to parse a new sentence:"
        print
        print str(self.ts)
        print `self.ts`

        self.explain("Start with the text")
        
        try:
            self.parse_start(treenode)
        except CancelParseException:
            self.output += "\n<br/><p>Here the parser was unable to continue. Sorry!</p>"
        except Exception, e:
            print e

        self.output += "\n<br/><p>And that's how you parse that sentence! I hope this was at least a bit helpful to you.</p>"

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
                if self.parse_sumti(newtarget, "vocative"):
                    self.parse_after_sumti(newtarget.last(), "vocative")
            elif nt.typ in ["LE", "LA"]:
                #newtarget = Node("sumti", nt.word)
                #target.extend(newtarget)
                #self.explain("%s is a gadri and starts a sumti." % nt.word)
                if self.parse_sumti(target, "gadri"):
                    self.parse_after_sumti(target.last(), "gadri")
            elif nt.typ.startswith("KOhA"):
                if self.parse_sumti(target, "start"):
                    self.parse_after_sumti(target.last(), "sumti")
            elif nt.typ == "BRIVLA":
                # since we are in sentence context we has our selbri
                self.parse_brivla(target, "sentence")
            elif nt.typ == "EOF":
                pass
            else:
                self.next()
                self.explain("i apologize, but i don't know what to do with %r at this place :(" % nt)
                print
                print `nt`
                print
                traceback.print_stack()
                print

    def parse_sumti(self, target, parent_rule=None):
        nt = self.peek()

        if nt.typ.startswith("KOhA"):
            target.extend(Node("sumti", nt.word))
            self.next()
            self.explain("%s is a prosumti" % nt.word)
        elif nt.typ == "cmene" and parent_rule in ["vocative", "gadri"]:
            target.extend(nt.word)
            self.next()
            if parent_rule == "gadri":
                self.explain("%s in a cmevla (name-word). It gets eaten by the gadri before it." % nt.word)
            else:
                self.explain("%s in a cmevla (name-word). It gets eaten by the vocative." % nt.word)
            self.parse_cmene(target, "cmene")
        elif nt.typ == "LA":
            # nest it up a bit.
            self.next()
            newtarget = Node("sumti", nt.word)
            target.extend(newtarget)
            self.explain("%s is a gadri and starts a sumti." % nt.word)
            if self.parse_cmene(newtarget, "gadri"):
                return True
            elif self.parse_brivla(newtarget, "gadri"):
                return True
            return None
        elif nt.typ == "LE":
            newt = Node("sumti", nt.word)
            self.next()
            target.extend(newt)
            self.explain("%s is a gadri and starts a sumti." % nt.word)
            self.parse_brivla(newt, "sumti")
            print "after parse_brivla, we still have ", self.peek()
            if self.peek().word == "ku":
                nt = self.next()
                target.last().extend(nt.word)
                self.explain("ku ends a sumti, so we stop parsing the sumti here.")
        else:
            print "parse_sumti hit thin air: %r" % (nt, )
            return None
        
        return True
    
    def parse_cmene(self, target, parent_rule=None):
        nt = self.peek()
        retval = False
        while nt.typ == "cmene":
            nt = self.next()
            target.extend(nt.word)
            if parent_rule == "cmene":
                self.explain("%s is a cmevla, too, and gets appended to the previous one." % nt.word)
                parent_rule = "cmene"
            elif parent_rule == "gadri":
                self.explain("%s is a cmevla and gets 'eaten' by the gadri" % nt.word)
                parent_rule = "cmene"
            else:
                self.explain("FIXME: explanation for parse_cmene wtih parent_rule == %s" % parent_rule)
            retval = True
            nt = self.peek()
        return retval

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
            if self.parse_sumti(newt, "subsumti"):
                self.parse_after_sumti(newt.last(), "subsumti")
            return True
        return False

    def parse_brivla(self, target, parent_rule=None):
        if self.peek().typ != "BRIVLA":
            return False
        # when this is called, peeking will get us a BRIVLA, which we will "eat" immediately
        nt = self.next()
        prev = None
        brivla = Node("selbri", nt.word)
        target.extend(brivla)
        self.explain("%s is a brivla, so we start reading brivla" % nt.word)
        prev = nt
        nt = self.peek()
        okToEnd = True
        while nt.typ in ["BRIVLA", "SE", "CO", "KE", "KEhE", "NU", "BE"]:
            brivla.extend(nt.word)
            if nt.typ == "BRIVLA":
                self.next()
                self.explain("%s is another brivla, getting appended to our tanru" % nt.word)
                okToEnd = True
            elif nt.typ == "SE":
                self.next()
                if prev.typ == "SE":
                    self.explain("%(nt)s is in SE just like %(prev)s. %(now)s gets treated before %(prev)s." % {"nt": nt, "prev": prev})
                else:
                    self.explain("%s is in SE and changes the place structure of what comes after it." % nt.word)
                okToEnd = False
            elif nt.typ == "EOF":
                return
            else:
                self.next()
                self.explain("I'm sorry, I don't know how to cope with %s (from selma'o %s) yet :(" % (nt.word, nt.typ))
                print
                print `nt`
                print
                traceback.print_stack()
                print
            
            prev = nt
            nt = self.peek()

        if not okToEnd:
            raise CancelParseException("This tanru was not well-formed. It can only end in a valid tanru unit.")
        return True

def parse(text):
    # TODO: sanitize input, use camxes/vlatai to split into words?
    r = Parser(text)
    print r()
    return r.output

if __name__ == "__main__":
    try:
        set_trace()
    except:
        pass
    while True:
        parse(raw_input())

