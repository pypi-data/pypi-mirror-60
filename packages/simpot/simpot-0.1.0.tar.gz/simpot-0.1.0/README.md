# Simple Object-triple Mapping

![Python application](https://github.com/lads-gp/simpot/workflows/Python%20application/badge.svg)

## 1. Requirements 
This module requires the rdflib package installation:
> $ pip install rdflib

## 2. How to Install
For install this package execute the command in your environment:
> $ pip install crdf-serializer

or:
> $ pip install -i https://test.pypi.org/simple/ crdf-serializer


## 3. How to use

```python
import simpot

from rdflib import Namespace, Literal, URIRef,RDF
from simpot import RdfsClass, BNamespace, graph
from rdflib.namespace import DC, FOAF


# exemplo do rdflib
class Person:
    nick = FOAF.nick
    name = FOAF.name
    email = FOAF.mbox

    @RdfsClass(FOAF.Person, None) # blank node
    @BNamespace("dc", DC)
    @BNamespace("foaf", FOAF)
    def __init__ (self, name, nick, email):
        self.nick = Literal(nick, lang="foo")
        self.name = Literal (name)
        self.email = URIRef(email) 

p = Person ("Donna Fales","donna", "mailto:donna@example.org")
print (graph(p).serialize())
```

https://docs.python-guide.org/writing/structure/#test-suite