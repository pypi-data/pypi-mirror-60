import logging
logger = logging.getLogger("pytrips")

import jsontrips
from collections import defaultdict as ddict
import json
import sys
import re

from .structures import TripsRestriction, TripsType, TripsSem
from .helpers import wn, get_wn_key, ss_to_sk, all_hypernyms
from nltk.corpus.reader.wordnet import Synset
import string as _string

from graphviz import Digraph

_gls_re = re.compile(".*-wn\d{5}$")
_gls = lambda x: re.match(_gls_re, x.lower())


class NodeGraph:
    def __init__(self, ont=None):
        self.nodes = {}
        self.node_attrs = {}
        self.edges = set()
        self.ont = ont

    def get_nth_label(self, n):
        if n < 26:
            return _string.ascii_uppercase[n]
        return self.get_nth_label(n // 26) + self.get_nth_label(n % 26)

    def get_label(self, name):
        #res = get_wn_key(name.split("::")[-1])
        #if res:
        #    return res.name()
        return name.lower()

    def escape_label(self, s):
        if not s:
            return ""
        if type(s) is str:
            return "w::"+s
        if type(s) is Synset:
            return "wn::"+s.lemmas()[0].key().lower()#.replace("%", ".")
        if type(s) is TripsType:
            return "ont::"+s.name
        return "any::"+str(s)

    def escape_dot(self, x):
        return x.replace(":", "_").replace("%", ".")

    def node(self, name, attrs=None):
        name = self.escape_label(name)
        if name in self.nodes:
            return
        label = self.get_label(name)
        self.nodes[name] = label
        if attrs:
            self.node_attrs[name] = attrs

    def edge(self, source, target, label=""):
        self.edges.add((self.escape_label(source), 
                    self.escape_label(target), 
                    self.escape_label(label)))

    def graph(self, format='svg'):
        graph = Digraph(format=format)
        for l, t in self.nodes.items():
            over = self.node_attrs.get(t, {})
            attrs = {"shape": "rectangle"}
            if t.startswith("w::"):
                t = t[3:]
                attrs["shape"] = "diamond"
            elif t.startswith("wn::"):
                t = t[4:]
                attrs["shape"] = "oval"
            for a, v in over.items():
                attrs[a] = v
            graph.node(self.escape_dot(l), t, **attrs)
        for s, t, l in self.edges:
            s, t = self.nodes[s], self.nodes[t]
            if l:
                graph.edge(self.escape_dot(s), self.escape_dot(t), l)
            else:
                graph.edge(self.escape_dot(s), self.escape_dot(t))
        return graph

    def source(self):
        return self.graph().source

    def json(self):
        elements = []
        for label, name in self.nodes.items():
            elements.append({"data": {"id": name, "label": label}})
        for source, target, label in self.edges:
            source = self.nodes[source]
            target = self.nodes[target]
            edge = {"data": {"source": source, "target": target}}
            if label:
                edge["data"]["label"] = label
            elements.append(edge)
        return elements


def _is_query_pair(x):
    if type(x) is tuple and len(x) == 2:
        return (type(x[0]) in set([str, TripsType])) and (type(x[1] == str))
    return False

def load_json(ontology, lexicon, use_gloss=False, stop=[], go=[]):
    self = Trips(stop=stop, go=go)
    ontology = ontology.values() # used to be a list, now is a dict
    self.max_wn_depth = 5 # override this for more generous or controlled lookups
    self._data = {}
    self._data['root'] = TripsType("root", None, [], [], [], [], TripsSem(type_="root", ont=self), [], self)
    revwords = ddict(set)
    self._words = ddict(lambda: ddict(set))
    self._wordnet_index = ddict(list)
    self.__definitions = ddict(list)
    if lexicon:
        for word, entry_list in lexicon["words"].items():
            for entry in entry_list:
                # Gather name, entries, pos
                name = entry["name"].lower()
                #cat = entry["cat"].lower()
                entries = lexicon["entries"][entry["entry"]]
                pos = entries['pos'].lower()
                # TODO: incorporate the lexicon
                if not use_gloss:
                    # skip gloss-derived entries if not use_gloss
                    entries['senses'] = [s for s in entries.get('senses', []) if not _gls(s.get("lf_parent", ""))]
                else:
                    entries["senses"] = entries.get("senses", [])
                if len(entries['senses']) > 1:
                    logger.info(entries["name"] + " has " + str(len(entries["senses"])) + " senses")
                for values in entries["senses"]:
                    if "lf_parent" not in values.keys():
                        c = "no_parent"
                    else:
                        c = values["lf_parent"].lower()
                    self._words[pos][word.lower()].add(c)
                    revwords[c].add((word+"."+pos).lower())

    for s in ontology:
        if not use_gloss:
            if _gls(s["name"].lower()):
                # skip gloss-derived times
                continue
            if s.get("children"):
                # filter out gloss-derived children
                s["children"] = [x for x in s["children"] if not _gls(x)]
        arguments = [TripsRestriction(x["role"],
                                      x.get("restriction", []),
                                      str(x["optionality"]), self)
                     for x in s.get('arguments', [])]
        sem_ = s.get("sem", {})
        _d = lambda y: {a.lower(): b for a, b in sem_.get(y, [])}
        sem = TripsSem(_d("features"), _d("default"), sem_.get("type", "").lower(), self)
        t = TripsType(
                s['name'],
                s.get('parent', "ROOT"),
                s.get('children', []),
                list(revwords[s['name'].lower()]),
                s.get('wordnet_sense_keys', []),
                arguments,
                sem,
                s.get('definitions', []),
                self
            )
        self._data[t.name] = t
        for k in s.get('wordnet_sense_keys', []):
            #k = get_wn_key(k) # won't need to do this if I normalize sense_keys to start with
            if k:
                self._wordnet_index[k].append(t)

        if t.definitions:
            self.__definitions[json.dumps(t.definitions)].append(t.name)
    return self

class Trips(object):
    def __init__(self, stop=None, go=None):
        self._data=None
        self._words=None
        self._wordnet_index=None
        self.__definitions=None
        self.__query_cache = {}
        if stop:
            if not go:
                go = []
            self.stop = [s for s in stop if s not in go]
            self.use_stop = True
        else:
            self.stop = []
            self.use_stop = False

    def get_trips_type(self, name):
        """Get the trips type associated with the name"""
        name = name.split("ont::")[-1].lower()
        return self._data.get(name, None)

    def get_word(self, word, pos=None):
        """Lookup all possible types for a word."""
        word = word.split("w::")[-1].lower()
        if pos:
            index = self._words[pos][word]
        else:
            index = set()
            for pos, words in self._words.items():
                index.update(words[word])
        return [self[x] for x in index if self[x]]

    def get_part_of_speech(self, pos, lex):
        """Lookup all possible types or lexical items for the given part of speech"""
        pos = pos.split("p::")[-1]
        words = self._words[pos].keys()
        if lex:
            return words
        res = []
        for x in words:
            res += self.get_word(x, pos=pos)
        return list(set(res))

    def get_word_graph(self, word, pos=None, use_stop=None):
        if use_stop is None:
            use_stop = self.use_stop
        graph = NodeGraph()
        senses = wn.lemmas(word, pos=pos)
        if pos:
            word = word + "." + pos
        graph.node(word)
        for l in senses:
            attrs = {}
            if l.key().lower() in self.stop:
                attrs["style"] = "filled"
                attrs["fillcolor"] = "red"
            graph.node(l.key(), attrs=attrs)
            graph.edge(word, l.key())
        if use_stop:
            senses = [s for s in senses if s.key().lower() not in self.stop]
        for s in senses:
            n, graph = self.get_wordnet(s.synset(), graph=graph, parent=s.key())
        return graph

    def get_wordnet(self, key, max_depth=-1, graph=None, parent=None):
        """Get types provided by wordnet mappings"""
        def _return(val):
            if graph:
                return (val, graph)
            return val

        if graph == True:
            graph = NodeGraph()

        if max_depth == -1:
            max_depth = self.max_wn_depth
        elif max_depth == 0:
            return _return([])

        if type(key) is str:
            key = get_wn_key(key)
        if not key:
            return _return([])

        if graph:
            graph.node(key)
            if parent:
                graph.edge(parent, key)
        res = []
        if ss_to_sk(key) in self._wordnet_index:
            res = self._wordnet_index[ss_to_sk(key)][:]
            if graph:
                for r in res:
                    graph.node(r)
                    graph.edge(key, r)
        else: #if (key.lemmas()[0].key().lower() not in self.stop) or not use_stop:
            res = set()
            for k in all_hypernyms(key):
                n = self.get_wordnet(k, max_depth=max_depth-1, graph=graph, parent=key)
                if graph:
                    n, graph = n
                res.update(n)
        return _return(res)

    def lookup(self, word, pos, use_stop=None):
        #TODO what kind of information does this need in general?
        if use_stop is None:
            use_stop = self.use_stop
        word = word.split("q::")[-1]
        #1 get word lookup
        w_look = self.get_word(word, pos=pos)
        #2 get wordnet
        wnlook = set()
        if wn:
            keys = wn.lemmas(word, pos=pos)
            if use_stop:
                keys = [s for s in keys if s.key().lower() not in self.stop]
            keys = [s.synset() for s in keys]
            for k in keys:
                wnlook.update(self.get_wordnet(k))
        return {"lex" : w_look, "wn": list(wnlook)}

    def get_definition(self, name):
        """Get types that contain the given name in their definitions
        """
        name = name.split("d::")[-1].split("ont::")[-1].upper() #definitions are in uppercase, names are in lower case.
        return list(set(["ont::"+df for lst in self.__definitions.keys() for df in self.__definitions[lst] if ""+name+"" in lst]))

    def __getitem__(self, key):
        """if the input is "w::x" lookup x as a word
        if the input is "ont::x" lookup x as a type
        if the input is "wn::x" lookup x as a wordnet sense
        else lookup as an ont type.
        """
        if key not in self.__query_cache:
            self.__query_cache[key] = self.make_query(key)
        return self.__query_cache[key]

    def make_query(self, key):
        pos = None
        if _is_query_pair(key):
            key, pos = key
        if type(key) is TripsType:
            return key
        if type(key) is Synset:
            return self.get_wordnet(key)
        elif type(key) is not str:
            return None
        if key is None:
            return None
        key = key.lower()
        if key.startswith("w::"):
            return self.get_word(key, pos=pos)
        elif key.startswith("wn::"):
            return self.get_wordnet(key)
        elif key.startswith("q::"):
            return self.lookup(key, pos=pos)
        elif key.startswith("p::"):
            return self.get_part_of_speech(key, lex=pos)
        elif key.startswith("d::") and self.get_trips_type(key.split("d::")[-1]):
            return self.get_definition(key)
        else:
            return self.get_trips_type(key)

    def __iter__(self):
        """return an iterator with all the types."""
        # TODO: guarantee order
        return self._data.values()


def load(skip_lexicon=False, use_gloss=False, log=False):
    if use_gloss:
        print("loading gloss-derived ontology")
    else:
        print("loading regular ontology")

    if not log:
        logging.disable(logging.CRITICAL)
    logger.info("Loading ontology")

    ont = jsontrips.ontology()

    logger.info("Loaded ontology")
    logger.info("Loading lexicon")
    
    if skip_lexicon:
        lex = {}
    else:
        lex = jsontrips.lexicon()

    logger.info("Loaded lexicon")
    return load_json(ont, lex, use_gloss=use_gloss, stop=jsontrips.stoplist(), go=jsontrips.golist())

__ontology__ = {}

def get_ontology(skip_lexicon=False, use_gloss=False, single=False, log=False):
    global __ontology__
    if not __ontology__.get(use_gloss):
        __ontology__[use_gloss] = load(skip_lexicon=skip_lexicon, use_gloss=use_gloss, log=log)
        if single:
            __ontology__[not use_gloss] = __ontology__[use_gloss]
    return __ontology__[use_gloss]
