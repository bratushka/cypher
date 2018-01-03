from types import GeneratorType
from unittest import TestCase

from . import cypher


class Tests(TestCase):
    def test_generate_tags(self):
        small = cypher.generate_tags(4)
        self.assertIsInstance(small, GeneratorType)

        small_tuple = tuple(small)
        # produces 26 values
        self.assertEqual(len(small_tuple), 26)
        # all values are different
        self.assertEqual(len(small_tuple), len(set(small_tuple)))
        # all values are strings
        self.assertTrue(all(map(lambda v: isinstance(v, str), small_tuple)))

        big_tuple = tuple(cypher.generate_tags(27))
        self.assertEqual(len(big_tuple), 26 * 26)
        self.assertEqual(len(big_tuple), len(set(big_tuple)))
        self.assertTrue(all(map(lambda v: isinstance(v, str), big_tuple)))


class ModelTests(TestCase):
    def test_labels_without_additional(self):
        class MyModel(cypher.Model):
            pass

        self.assertEqual(MyModel().labels, ('MyModel',))

    def test_labels_with_additional(self):
        class MyModel(cypher.Model):
            pass

        instance = MyModel(labels=['a', 'b'])
        self.assertEqual(instance.labels, ('MyModel', 'a', 'b'))

        instance.labels = ['c']
        self.assertEqual(instance.labels, ('MyModel', 'c'))

        instance.labels = ['d', 'MyModel', 'e']
        self.assertEqual(instance.labels, ('MyModel', 'd', 'e'))

    def test_labels_not_iterable(self):
        class MyModel(cypher.Model):
            pass

        with self.assertRaises(TypeError):
            # noinspection PyTypeChecker
            MyModel(labels=[1])
        with self.assertRaises(TypeError):
            # noinspection PyTypeChecker
            MyModel(labels=0)
        with self.assertRaises(TypeError):
            # noinspection PyTypeChecker
            MyModel(labels=False)
        with self.assertRaises(TypeError):
            # noinspection PyTypeChecker
            MyModel(labels=str)

    def test_model_creation_with_props(self):
        class MyModel(cypher.Model):
            integer = cypher.Props.Integer()
            floating = cypher.Props.Float()
            string = cypher.Props.String()

        instance = MyModel(integer=1, floating=1.1, string='text')
        self.assertEqual(instance.integer, 1)
        self.assertEqual(instance.floating, 1.1)
        self.assertEqual(instance.string, 'text')

    def test_model_creation_with_extra_props(self):
        class MyModel(cypher.Model):
            pass

        instance = MyModel(integer=1, floating=1.1)
        expected = dict(integer=1, floating=1.1)
        self.assertEqual(instance._extra_props, expected)

    def test_model_creation_raising_type_error(self):
        class MyModel(cypher.Model):
            integer = cypher.Props.Integer()
            floating = cypher.Props.Float()
            string = cypher.Props.String()

        with self.assertRaises(TypeError):
            MyModel(integer=1.1)
        with self.assertRaises(TypeError):
            MyModel(floating='')
        with self.assertRaises(TypeError):
            MyModel(string=1)

    def test_cypher_repr(self):
        class MyModel(cypher.Model):
            integer = cypher.Props.Integer()
            floating = cypher.Props.Float()
            string = cypher.Props.String()
            boolean = cypher.Props.Boolean()

        instance = MyModel(
            integer=1,
            floating=1.1,
            string='text"',
            boolean=True,
            labels=('First', 'Second`', '!@#$%^&*()'),
        )
        expected = (
            ':`MyModel`:`First`:`Second```:`!@#$%^&*()`'
            ' { `boolean`: true, `floating`: 1.1,'
            ' `integer`: 1, `string`: "text\\"" }'
        )
        self.assertEqual(instance.cypher_repr(), expected)


class DBTests(TestCase):
    def test__get_url_with_valid_url(self):
        address = 'bolt://some.address:7687'

        class MyDB(cypher.DB):
            url = address

        self.assertEqual(MyDB._get_url(), address)

    def test__get_url_with_invalid_url(self):
        class MyDB(cypher.DB):
            url = 'invalid.url'

        with self.assertRaises(cypher.DatabaseAddressException):
            MyDB._get_url()

    def test__get_url_with_host_and_port(self):
        class MyDB(cypher.DB):
            host = 'host'
            port = 1000

        self.assertEqual(MyDB._get_url(), 'bolt://host:1000')

    def test__get_url_with_host_with_bolt(self):
        class MyDB(cypher.DB):
            host = 'bolt://host'
            port = 1000

        self.assertEqual(MyDB._get_url(), 'bolt://host:1000')

    def test_models(self):
        class MyDB(cypher.DB):
            pass

        class MyNode(cypher.Node):
            pass

        class MyEdge(cypher.Edge):
            pass

        my_db = MyDB()
        my_node = MyNode()
        my_other_node = MyNode()
        my_edge = MyEdge(my_node, my_other_node)

        my_db.models = [my_node, my_other_node, my_edge]
        self.assertIsInstance(my_db.models, tuple)
        self.assertIs(my_db.models[0], my_node)
        self.assertIs(my_db.models[1], my_other_node)
        self.assertIs(my_db.models[2], my_edge)

        my_db.models = (my_edge, my_node, my_other_node)
        self.assertIs(my_db.models[0], my_node)
        self.assertIs(my_db.models[1], my_other_node)
        self.assertIs(my_db.models[2], my_edge)

    def test_query_create_without_edges(self):
        class MyDB(cypher.DB):
            pass

        class MyNode(cypher.Node):
            age = cypher.Props.Integer()

        instances = (
            MyNode(age=21),
            MyNode(age=22),
        )

        expected = (
            'CREATE (a:`MyNode` { `age`: 21 }), (b:`MyNode` { `age`: 22 })'
            '\nRETURN a, b'
        )

        self.assertEqual(MyDB().create(*instances).query, expected)

    def test_query_create_with_edges(self):
        class MyDB(cypher.DB):
            pass

        class MyNode(cypher.Node):
            age = cypher.Props.Integer()

        class MyEdge(cypher.Edge):
            parent = cypher.Props.Boolean()

        son = MyNode(age=21)
        father = MyNode(age=47)
        son_to_father = MyEdge(son, father, parent=False)
        father_to_son = MyEdge(father, son, parent=True)
        instances = (son_to_father, father_to_son, son, father)

        expected = (
            'CREATE (a:`MyNode` { `age`: 21 }), (b:`MyNode` { `age`: 47 }),'
            ' (a)-[c:`MyEdge` { `parent`: false }]->(b),'
            ' (b)-[d:`MyEdge` { `parent`: true }]->(a)'
            '\nRETURN a, b, c, d'
        )

        self.assertEqual(MyDB().create(*instances).query, expected)

    def test_query_create_only_edges(self):
        class MyDB(cypher.DB):
            pass

        class MyNode(cypher.Node):
            age = cypher.Props.Integer()

        class MyEdge(cypher.Edge):
            parent = cypher.Props.Boolean()

        son = MyNode(age=21)
        father = MyNode(age=47)
        son_to_father = MyEdge(son, father, parent=False)
        father_to_son = MyEdge(father, son, parent=True)
        instances = (son_to_father, father_to_son)

        expected = (
            'CREATE (a:`MyNode` { `age`: 21 }), (b:`MyNode` { `age`: 47 }),'
            ' (a)-[c:`MyEdge` { `parent`: false }]->(b),'
            ' (b)-[d:`MyEdge` { `parent`: true }]->(a)'
            '\nRETURN a, b, c, d'
        )

        self.assertEqual(MyDB().create(*instances).query, expected)
