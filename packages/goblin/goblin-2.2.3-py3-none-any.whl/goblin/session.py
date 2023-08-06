"""Main OGM API classes and constructors"""

import asyncio
import collections
import logging
import weakref
import uuid
from typing import Callable, Awaitable, Any, Optional

import aiogremlin # type: ignore
from aiogremlin.driver.protocol import Message # type: ignore
from aiogremlin.driver.resultset import ResultSet # type: ignore
from gremlin_python.process.graph_traversal import __, GraphTraversal # type: ignore
from gremlin_python.driver.remote_connection import RemoteTraversal # type: ignore
from gremlin_python.process.traversal import Binding, Cardinality, Traverser # type: ignore
from gremlin_python.structure.graph import Edge, Vertex # type: ignore

from goblin import exception, mapper
from goblin.element import GenericEdge, GenericVertex, VertexProperty, ImmutableMode, LockingMode
from goblin.manager import VertexPropertyManager

logger = logging.getLogger(__name__)


def bindprop(element_class, ogm_name, val, *, binding=None):
    """
    Helper function for binding ogm properties/values to corresponding db
    properties/values for traversals.

    :param goblin.element.Element element_class: User defined element class
    :param str ogm_name: Name of property as defined in the ogm
    :param val: The property value
    :param str binding: The binding for val (optional)

    :returns: tuple object ('db_property_name', ('binding(if passed)', val))
    """
    db_name = getattr(element_class, ogm_name, ogm_name)
    _, data_type = element_class.__mapping__.ogm_properties[ogm_name]
    val = data_type.to_db(val)
    if binding:
        val = (binding, val)
    return db_name, val


class Session:
    """
    Provides the main API for interacting with the database. Does not
    necessarily correpsond to a database session. Don't instantiate directly,
    instead use :py:meth:`Goblin.session<goblin.app.Goblin.session>`.

    :param goblin.app.Goblin app:
    :param aiogremlin.driver.connection.Connection conn:
    """

    def __init__(self, app, remote_connection, get_hashable_id):
        self._app = app
        self._remote_connection = remote_connection
        self._loop = self._app._loop
        self._use_session = False
        self._pending = collections.deque()
        self._current = dict()
        self._get_hashable_id = get_hashable_id
        self._graph = aiogremlin.Graph()

    @property
    def graph(self):
        return self._graph

    @property
    def app(self):
        return self._app

    @property
    def remote_connection(self):
        return self._remote_connection

    @property
    def current(self):
        return self._current

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        self.close()

    def close(self):
        """
        """
        self._remote_connection = None
        self._app = None

    # Traversal API
    @property
    def g(self):
        """
        Get a simple traversal source.

        :returns:
            `gremlin_python.process.GraphTraversalSource`
            object
        """
        return self.traversal()

    @property
    def _g(self):
        """
        Traversal source for internal use. Uses undelying conn. Doesn't
        trigger complex deserailization.
        """
        return self.graph.traversal().withRemote(self.remote_connection)

    def traversal(self, element_class=None):
        """
        Generate a traversal using a user defined element class as a
        starting point.

        :param goblin.element.Element element_class: An optional element
            class that will dictate the element type (vertex/edge) as well as
            the label for the traversal source

        :returns: `aiogremlin.process.graph_traversal.AsyncGraphTraversal`
        """
        traversal = self.graph.traversal().withRemote(self)
        if element_class:
            label = element_class.__mapping__.label
            if element_class.__type__ == 'vertex':
                traversal = traversal.V()
            if element_class.__type__ == 'edge':
                traversal = traversal.E()
            traversal = traversal.hasLabel(label)
        return traversal

    async def submit(self, bytecode):
        """
        Submit a query to the Gremiln Server.

        :param str gremlin: Gremlin script to submit to server.
        :param dict bindings: A mapping of bindings for Gremlin script.

        :returns:
            `gremlin_python.driver.remove_connection.RemoteTraversal`
            object
        """
        await self.flush()
        remote_traversal = await self.remote_connection.submit(bytecode)
        traversers = remote_traversal.traversers
        side_effects = remote_traversal.side_effects
        result_set = ResultSet(traversers.request_id, traversers._timeout,
                               self._loop)
        self._loop.create_task(self._receive(traversers, result_set))
        return RemoteTraversal(result_set, side_effects)

    async def _receive(self, traversers, result_set):
        try:
            async for result in traversers:
                result = await self._deserialize_result(result)
                msg = Message(200, result, '')
                result_set.queue_result(msg)
        except Exception as e:
            msg = Message(500, None, e.args[0])
            result_set.queue_result(msg)
        finally:
            result_set.queue_result(None)

    async def _deserialize_result(self, result):
        if isinstance(result, Traverser):
            bulk = result.bulk
            obj = result.object
            if isinstance(obj, (Vertex, Edge)):
                hashable_id = self._get_hashable_id(obj.id)
                current = self.current.get(hashable_id, None)
                if isinstance(obj, Vertex):
                    # why doesn't this come in on the vertex?
                    label = await self._g.V(obj.id).label().next()
                    if not current:
                        current = self.app.vertices.get(label, GenericVertex)()
                    props = await self._get_vertex_properties(obj.id, label)
                if isinstance(obj, Edge):
                    props = await self._g.E(obj.id).valueMap(True).next()
                    if not current:
                        current = self.app.edges.get(
                            props.get('label'), GenericEdge)()
                        current.source = GenericVertex()
                        current.target = GenericVertex()
                element = current.__mapping__.mapper_func(obj, props, current)
                self.current[hashable_id] = element
                return Traverser(element, bulk)
            else:
                return result
        # Recursive serialization is broken in goblin
        elif isinstance(result, dict):
            for key in result:
                result[key] = self._deserialize_result(result[key])
            return result
        elif isinstance(result, list):
            return [self._deserialize_result(item) for item in result]
        else:
            return result

    async def _get_vertex_properties(self, vid, label):
        projection = self._g.V(vid).properties() \
                            .project('id', 'key', 'value', 'meta') \
                            .by(__.id()).by(__.key()).by(__.value()) \
                            .by(__.valueMap())
        props = await projection.toList()
        new_props = {'label': label, 'id': vid}
        for prop in props:
            key = prop['key']
            val = prop['value']
            # print('val_type', type(val))
            meta = prop['meta']
            new_props.setdefault(key, [])
            if meta:
                meta['key'] = key
                meta['value'] = val
                meta['id'] = prop['id']
                val = meta

            new_props[key].append(val)
        return new_props

    # Creation API
    def add(self, *elements):
        """
        Add elements to session pending queue.

        :param goblin.element.Element elements: Elements to be added
        """
        for elem in elements:
            self._pending.append(elem)

    async def flush(
                    self,
                    conflicts_query: Optional[GraphTraversal] = None
                  ) -> None:
        """
        Issue creation/update queries to database for all elements in the
        session pending queue.
        """
        transaction_id = str(uuid.uuid4())
        processed = []
        try:
            while self._pending:
                elem = self._pending.popleft()
                actual_id = self.__dirty_element(elem, id=transaction_id)
                if actual_id:
                    processed.append(await self.save(elem))
                else:
                    await self.save(elem)

            if not processed: return
            if not conflicts_query:
                await self.__commit_transaction(transaction_id)
            else:
                await (self.
                       g.
                       E().
                       has('dirty', transaction_id).
                       aggregate('x').
                       fold().
                       V().
                       has('dirty', transaction_id).
                       aggregate('x').
                       choose(
                           conflicts_query,

                           __.
                           select('x').
                           unfold().
                           properties('dirty').
                           drop()).
                       iterate())  # type: ignore
                await self.__rollback_transaction(transaction_id)
        except Exception as e:
            await self.__rollback_transaction(transaction_id)
            raise e
        for elem in processed:
            elem.dirty = None

    async def remove_vertex(self, vertex):
        """
        Remove a vertex from the db.

        :param goblin.element.Vertex vertex: Vertex to be removed
        """
        traversal = self._g.V(Binding('vid', vertex.id)).drop()
        result = await self._simple_traversal(traversal, vertex)
        hashable_id = self._get_hashable_id(vertex.id)
        if hashable_id in self.current:
            vertex = self.current.pop(hashable_id)
        else:
            msg = 'Vertex {} does not belong to this session obj {}'.format(
                vertex, self)
            logger.warning(msg)
        del vertex
        return result

    async def remove_edge(self, edge):
        """
        Remove an edge from the db.

        :param goblin.element.Edge edge: Element to be removed
        """
        eid = edge.id
        if isinstance(eid, dict):
            eid = Binding('eid', edge.id)
        traversal = self._g.E(eid).drop()
        result = await self._simple_traversal(traversal, edge)
        hashable_id = self._get_hashable_id(edge.id)
        if hashable_id in self.current:
            edge = self.current.pop(hashable_id)
        else:
            msg = 'Edge {} does not belong to this session obj {}'.format(
                edge, self)
            logger.warning(msg)
        del edge
        return result

    async def save(self, elem):
        """
        Save an element to the db.

        :param goblin.element.Element element: Vertex or Edge to be saved

        :returns: :py:class:`Element<goblin.element.Element>` object
        """
        if elem.__type__ == 'vertex':
            result = await self.save_vertex(elem)
        elif elem.__type__ == 'edge':
            result = await self.save_edge(elem)
        else:
            raise exception.ElementError("Unknown element type: {}".format(
                elem.__type__))
        return result

    async def save_vertex(self, vertex):
        """
        Save a vertex to the db.

        :param goblin.element.Vertex element: Vertex to be saved

        :returns: :py:class:`Vertex<goblin.element.Vertex>` object
        """
        result = await self._save_element(
            vertex, self._check_vertex, self._add_vertex, self._update_vertex)
        hashable_id = self._get_hashable_id(result.id)
        self.current[hashable_id] = result
        return result

    async def save_edge(self, edge):
        """
        Save an edge to the db.

        :param goblin.element.Edge element: Edge to be saved

        :returns: :py:class:`Edge<goblin.element.Edge>` object
        """
        if not (hasattr(edge, 'source') and hasattr(edge, 'target')):
            raise exception.ElementError(
                "Edges require both source/target vertices")
        result = await self._save_element(edge, self._check_edge,
                                          self._add_edge, self._update_edge)
        hashable_id = self._get_hashable_id(result.id)
        self.current[hashable_id] = result
        return result

    async def get_vertex(self, vertex):
        """
        Get a vertex from the db. Vertex must have id.

        :param goblin.element.Vertex element: Vertex to be retrieved

        :returns: :py:class:`Vertex<goblin.element.Vertex>` | None
        """
        return await self.g.V(Binding('vid', vertex.id)).next()

    async def get_edge(self, edge):
        """
        Get a edge from the db. Edge must have id.

        :param goblin.element.Edge element: Edge to be retrieved

        :returns: :py:class:`Edge<goblin.element.Edge>` | None
        """
        eid = edge.id
        if isinstance(eid, dict):
            eid = Binding('eid', edge.id)
        return await self.g.E(eid).next()

    def __dirty_element(self, elem, id = str(uuid.uuid4())):
        if elem.__locking__ and elem.__locking__ == LockingMode.OPTIMISTIC_LOCKING:
            if not elem.dirty:
                elem.dirty = id
                return id
            else:
                return elem.dirty
        return None

    async def __commit_transaction(self, id):
        if id: await self._g.E().has('dirty',id).aggregate('x').fold().V().has('dirty',id).aggregate('x').select('x').unfold().properties('dirty').drop().iterate()

    async def __rollback_transaction(self, id):
        print("id of: %s" % id)
        if id: await self._g.E().has('dirty',id).aggregate('x').fold().V().has('dirty',id).aggregate('x').select('x').unfold().drop().iterate()

    async def _update_vertex(self, vertex):
        """
        Update a vertex, generally to change/remove property values.

        :param goblin.element.Vertex vertex: Vertex to be updated

        :returns: :py:class:`Vertex<goblin.element.Vertex>` object
        """
        props = mapper.map_props_to_db(vertex, vertex.__mapping__)
        traversal = self._g.V(Binding('vid', vertex.id))
        return await self._update_vertex_properties(vertex, traversal, props)

    async def _update_edge(self, edge):
        """
        Update an edge, generally to change/remove property values.

        :param goblin.element.Edge edge: Edge to be updated

        :returns: :py:class:`Edge<goblin.element.Edge>` object
        """
        props = mapper.map_props_to_db(edge, edge.__mapping__)
        eid = edge.id
        if isinstance(eid, dict):
            eid = Binding('eid', edge.id)
        traversal = self._g.E(eid)
        return await self._update_edge_properties(edge, traversal, props)

    # *metodos especiales privados for creation API

    async def _simple_traversal(self, traversal, element):
        elem = await traversal.next()
        if elem:
            if element.__type__ == 'vertex':
                # Look into this
                label = await self._g.V(elem.id).label().next()
                props = await self._get_vertex_properties(elem.id, label)
            elif element.__type__ == 'edge':
                props = await self._g.E(elem.id).valueMap(True).next()
            elem = element.__mapping__.mapper_func(elem, props, element)
        return elem


    async def __handle_create_func(self, elem, create_func):
        transaction_id = elem.dirty
        if not transaction_id:
            transaction_id = self.__dirty_element(elem)
            if transaction_id:
                result = None
                try:
                    result = await create_func(elem)
                    await self.__commit_transaction(transaction_id)
                    result.dirty = None
                except Exception as e:
                    await self.__rollback_transaction(transaction_id)
                    raise e
                return result

        return await create_func(elem)


    async def _save_element(self, elem, check_func, create_func, update_func):
        if hasattr(elem, 'id'):
            exists = await check_func(elem)
            if not exists:
                result = await self.__handle_create_func(elem, create_func)
            else:
                if elem.__immutable__ and elem.__immutable__ != ImmutableMode.OFF: raise AttributeError("Trying to update an immutable element: %s" % elem)
                result = await update_func(elem)
        else:
            result = await self.__handle_create_func(elem, create_func)
        return result

    async def _add_vertex(self, vertex):
        """Convenience function for generating crud traversals."""
        props = mapper.map_props_to_db(vertex, vertex.__mapping__)
        traversal = self._g.addV(vertex.__mapping__.label)
        return await self._add_properties(traversal, props, vertex)

    async def _add_edge(self, edge):
        """Convenience function for generating crud traversals."""
        props = mapper.map_props_to_db(edge, edge.__mapping__)
        traversal = self._g.V(Binding('sid', edge.source.id))
        traversal = traversal.addE(edge.__mapping__._label)
        traversal = traversal.to(__.V(Binding('tid', edge.target.id)))
        return await self._add_properties(traversal, props, edge)

    async def _check_vertex(self, vertex):
        """Used to check for existence, does not update session vertex"""
        msg = await self._g.V(Binding('vid', vertex.id)).next()
        return msg

    async def _check_edge(self, edge):
        """Used to check for existence, does not update session edge"""
        eid = edge.id
        if isinstance(eid, dict):
            eid = Binding('eid', edge.id)
        return await self._g.E(eid).next()

    async def _update_vertex_properties(self, vertex, traversal, props):
        await self._g.V(vertex.id).properties().drop().iterate()
        return await self._add_properties(traversal, props, vertex)

    async def _update_edge_properties(self, edge, traversal, props):
        await self._g.E(edge.id).properties().drop().iterate()
        return await self._add_properties(traversal, props, edge)

    async def _add_properties(self, traversal, props, elem):
        binding = 0
        for card, db_name, val, metaprops in props:
            if not metaprops:
                metaprops = {}
            if val is not None:
                key = db_name
                #key = ('k' + str(binding), db_name)
                #val = ('v' + str(binding), val)
                if card:
                    # Maybe use a dict here as a translator
                    if card == Cardinality.list_:
                        card = Cardinality.list_
                    elif card == Cardinality.set_:
                        card = Cardinality.set_
                    else:
                        card = Cardinality.single
                    metas = [
                        j
                        for i in zip(metaprops.keys(), metaprops.values())
                        for j in i
                    ]
                    traversal = traversal.property(card, key, val, *metas)
                else:
                    metas = [
                        j
                        for i in zip(metaprops.keys(), metaprops.values())
                        for j in i
                    ]
                    traversal = traversal.property(key, val, *metas)
                binding += 1
        return await self._simple_traversal(traversal, elem)
