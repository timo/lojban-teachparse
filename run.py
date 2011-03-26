from flask import Flask, request

from parser import Parser

from lojbansuggest.suggest import LojbanText, LojbanSentence, UnparsableText
from urllib2 import quote

app = Flask(__name__)

htmltempl = """<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd"> 
<html> 
    <head> 
        <title>learn how to parse lojban in your head</title>
        <link rel="stylesheet" href="/static/boxes.css" type="text/css">
    </head>
    <body>
    <form method="GET" action="explain"><input name="text"/><input type="submit"/></form><br/><br/>
%s
    </body>
</html>"""

def rendersugs(sent):
    return "".join("""<li>%s</li>""" % sent.sug)

@app.route("/")
def main():
    return htmltempl % ("""input some (very) simple lojbanic text and see what happens!""")

@app.route("/explain", methods=["POST", "GET"])
def explain():
    text = request.form["text"] if "text" in request.form else request.args.get("text", "coi do lo gerku ui ku klama lo zarci")
    
    lojbansugoutput = ""
    
    # run the text throug lojbansuggest to find out if it parses at all and has common newbie mistakes
    try:
        lt = lojbantext(text)

        if len(lt.items) > 1:
            sentencelist = "".join(["""<li><a href="/explain?text=%(textenc)s">%(text)s</a></li>\n""" % {"textenc": quote(sent.td), "text": sent.td} for sent in lt.items])
            return htmltempl % ("""
            <p>This software can only work with one sentence at a time.</p>
            <p>Try a single one instead:</p>
            <ul>
                %s
            </ul>""" % (sentencelist, ))
        else:
            thesent = lt.items[0]
            if isinstance(thesent, unparsabletext):
                return htmltempl % ("""        <p>The sentence you supplied could not be parsed by the official parser.</p>
            <p>Look at these suggestions or ask in the lojban irc channel or the mailing list for help</p>
            <ul>
    %s
            </ul>""" % rendersugs(thesent))
            else:
                if len(thesent.sug) > 0:
                    lojbansugoutput = """        <p>I may have found possible mistakes in your sentence. Please consider them and ask on the mailing list or IRC channel if you're unsure.<p>
            <ul>
    %s
            </ul><br/>""" % rendersugs(thesent)

    except Exception, e:
        print e

    p = Parser(text)
    return htmltempl % (lojbansugoutput + p())

if __name__ == "__main__":
    app.run(host="0.0.0.0")
