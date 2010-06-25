from flask import Flask, request

from parser import Parser

app = Flask(__name__)

@app.route("/")
def main():
    return """<form method="GET" action="explain"><input name="text"/><input type="submit"/></form>"""

@app.route("/explain", methods=["POST", "GET"])
def explain():
    #text = request.form["text"] if "text" in request.form else request.args.get("text", "coi do lo gerku ui ku klama lo zarci")
    p = Parser("coi do lo gerku ku klama lo zarci")
    return """<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd"> 
<html> 
    <head> 
        <title>learn how to parse lojban in your head</title>
        <link rel="stylesheet" href="/static/boxes.css" type="text/css">
    </head>
    <body>
%s
    </body>
</html>""" % p()

@app.route("/boxes.css")
def getboxcss():
    print "getting boxes"
    return open("boxes.css").read()

if __name__ == "__main__":
    app.run()
