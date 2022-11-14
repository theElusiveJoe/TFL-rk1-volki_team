import uuid
import json
from cfg.tools import *


class FA:
    def __init__(self):
        self.start_node = gen_unique_node()
        self.finish_node = gen_unique_node()
        self.nodes = set([self.start_node, self.finish_node])
        self.transits = set()
        self.alphabeth = set()

    def __repr__(self):
        nl = '\n'
        return (
            '#'*10
            + nl
            + nl.join(map(
                lambda x: '#   ' + str(x),
                [
                    'FA',
                    'nodes: ' + str(self.nodes), 
                    'start: ' + str(self.start_node),
                    'finish: ' + str(self.finish_node),
                    'alphabeth: ' + str(self.alphabeth),
                    'transits:', *list(map(
                        lambda x: '    ' +
                        str(x[0])+' -- '+ ( f'"{str(x[2])}"' if x[2] else '"ε"') +' -> '+str(x[1]),
                        self.transits
                    )),
                ]))
            + nl
            + '#'*10
        )

    def to_json(self, indent=None):
        ret = {
            'nodes': list(self.nodes),
            'alphabeth': list(self.alphabeth),
            'transits': list(self.transits),
            'start': self.start_node,
            'finish': self.finish_node
        }
        return json.dumps(ret, indent=indent)

    def add_nodes(self, l):
        self.nodes.update(list(map(str, l)))

    def add_transit(self, src, dst, char):
        assert src in self.nodes and dst in self.nodes

        self.transits.add(
            (src, dst, char)
        )
        self.alphabeth.add(char)

    def concat(self, fa2):
        new_fa = FA()

        new_fa.nodes.update(self.nodes | fa2.nodes)
        new_fa.alphabeth.update(self.alphabeth | fa2.alphabeth)
        new_fa.transits.update(self.transits | fa2.transits)
        new_fa.transits.update(self.transits | fa2.transits)

        new_fa.add_transit(self.finish_node, fa2.start_node, '')
        new_fa.add_transit(new_fa.start_node, self.start_node, '')
        new_fa.add_transit(fa2.finish_node, new_fa.finish_node, '')

        return new_fa

    def insert(self, fa2, insert_start=None, insert_end=None):
        if not insert_start:
            insert_start=self.start_node
        if not insert_end:
            insert_end=self.finish_node
        
        self.nodes.update(fa2.nodes)
        self.transits.update(fa2.transits)
        self.alphabeth.update(fa2.alphabeth)

        self.add_transit(insert_start, fa2.start_node, '')
        self.add_transit(fa2.finish_node, insert_end, '')
