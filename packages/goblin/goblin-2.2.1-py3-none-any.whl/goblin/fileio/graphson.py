import collections
try:
    import ujson as json
except ImportError:
    import json

from gremlin_python.structure.io.graphsonV3d0 import GraphSONWriter
from goblin.element import Vertex, Edge, VertexProperty
from goblin.manager import ListVertexPropertyManager


writer = GraphSONWriter()


AdjList = collections.namedtuple("AdjList", "vertex inE outE")

vp_id = 10


def dump(fpath, *adj_lists, mode="w"):
    """Convert Goblin elements to GraphSON"""
    with open(fpath, mode) as f:
        for adj_list in adj_lists:
            dumped = dumps(adj_list)
            f.write(dumped + '\n')


def dumps(adj_list):
    """Convert Goblin elements to GraphSON"""
    vertex = _prep_vertex(adj_list.vertex)
    for inE in adj_list.inE:
        prepped = _prep_edge(inE, "inV")
        label = inE.__label__
        vertex["inE"].setdefault(label, [])
        vertex["inE"][label].append(prepped)
    for outE in adj_list.outE:
        prepped = _prep_edge(outE, "outV")
        label = outE.__label__
        vertex["outE"].setdefault(label, [])
        vertex["outE"][label].append(prepped)
    return json.dumps(vertex)


def _prep_edge(e, t):
    if t == 'inV':
        other = "outV"
        other_id = e.source.id
    elif t == 'outV':
        other = "inV"
        other_id = e.target.id
    else:
        raise RuntimeError('Invalid edge type')
    edge = {
        "id": {
            "@type": "g:Int32",
            "@value": e.id,

        },
        other: {
            "@type": "g:Int32",
            "@value": other_id,
        },
        "properties": {}
    }
    for db_name, (ogm_name, _) in e.__mapping__.db_properties.items():
        edge["properties"][db_name] = writer.toDict(getattr(e, ogm_name))

    return edge


def _prep_vertex(v):
    global vp_id
    mapping = v.__mapping__
    properties = v.__properties__
    vertex = {
            "id": {
                "@type": "g:Int32",
                "@value": v.id
            },
            "label": v.__label__,
            "properties": {},
            "outE": {},
            "inE": {}
    }



    for db_name, (ogm_name, _) in mapping.db_properties.items():
        prop = properties[ogm_name]
        vertex["properties"].setdefault(db_name, [])
        if isinstance(prop, VertexProperty):
            prop = getattr(v, ogm_name)
            if isinstance(prop, ListVertexPropertyManager):
                for p in prop:
                    value = p.value
                    vp = _prep_vp(p, value, v, db_name)
                    vp_id += 1
                    vertex["properties"][db_name].append(vp)
                continue
            else:
                value = prop.value
        else:
            value = getattr(v, ogm_name)
        vp = _prep_vp(prop, value, v, db_name)
        vp_id += 1
        vertex["properties"][db_name].append(vp)
    return vertex


def _prep_vp(prop, value, v, db_name):
    vp = {
            "id": {
                "@type": "g:Int64",
                "@value": vp_id
            },
            "value": writer.toDict(value),
            "properties": {}
    }
    if isinstance(prop, VertexProperty):
        for db_name, (ogm_name, _) in prop.__mapping__.db_properties.items():
            vp["properties"][db_name] = writer.toDict(getattr(prop, ogm_name))
    return vp



def _dump_edge(e):
    pass
