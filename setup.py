from setuptools import setup

setup(
        name="lojban-teachparse",
        version="0.02",
        scripts=["parser.py",
                 "run.py"],
        install_requires = ["flask", "lojbansuggest", "lojbantools"]
)
