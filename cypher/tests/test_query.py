"""
Tests for `query.py`.
"""
# from datetime import date
from unittest import TestCase

from ..props import Props
from ..models import Edge, Node
from ..query import Query


class MatchTests(TestCase):
    """
    Test building queries.
    """
    def test_match_by_none(self):
        """
        Match all the nodes.
        """
        query = Query().match(None).result(no_exec=True)
        expected = (
            'MATCH (_a)\n'
            'RETURN _a'
        )
        self.assertEqual(query, expected)

    def test_match_by_class(self):
        """
        The most simple `match` scenario by class.
        """
        class Human(Node):
            """
            Example of Node.
            """

        query = Query().match(Human).result(no_exec=True)
        expected = (
            'MATCH (_a:Human)\n'
            'RETURN _a'
        )
        self.assertEqual(query, expected)

    def test_match_type_error(self):
        """
        Pass wrong type to match.
        """
        class Human:
            """
            Example of not Node.
            """

        with self.assertRaises(TypeError):
            # noinspection PyTypeChecker
            Query().match(Human)

    def test_match_by_instance(self):
        """
        Match by instance.
        """
        class Human(Node):
            """
            Example of Node.
            """
            class Meta(Node.Meta):
                """
                Example of Node.Meta.
                """
                primary_key = 'name'

            name = Props.String()

        human = Human(name='John')

        query = Query().match(human).result(no_exec=True)
        expected = (
            'MATCH (_a:Human)\n'
            'WHERE _a.name = "John"\n'
            'RETURN _a'
        )
        self.assertEqual(query, expected)

    def test_combined_match_by_class(self):
        """
        Combination of 2 most simple `match` scenarios.
        """
        class Human(Node):
            """
            Example of Node.
            """

        class Animal(Node):
            """
            Example of Node.
            """

        query = Query().match(Human).match(Animal).result(no_exec=True)
        expected = (
            'MATCH (_a:Human)\n'
            'MATCH (_b:Animal)\n'
            'RETURN _a, _b'
        )
        self.assertEqual(query, expected)

    def test_combined_match_by_class_and_instance(self):
        """
        Combination of matching by class and instance.
        """
        # pylint: disable=invalid-name
        # This suppresses error for the method name.
        # pylint: enable=no-member
        class Human(Node):
            """
            Example of Node.
            """
            class Meta(Node.Meta):
                """
                Example of Node.Meta.
                """
                primary_key = 'name'

            name = Props.String()

        class Animal(Node):
            """
            Example of Node.
            """

        human = Human(name='human_name')
        query = Query()\
            .match(human)\
            .match(Animal)\
            .result(no_exec=True)
        expected = (
            'MATCH (_a:Human)\n'
            'WHERE _a.name = "human_name"\n'
            'MATCH (_b:Animal)\n'
            'RETURN _a, _b'
        )
        self.assertEqual(query, expected)

    def test_match_by_class_with_comparison(self):
        """
        Add a `where` to the most simple `match` scenario.
        """
        # pylint: disable=invalid-name
        # This suppresses error for the method name.
        # pylint: enable=no-member
        class Human(Node):
            """
            Example of Node.
            """
            admin = Props.Boolean()
            age = Props.Integer()

        # pylint: disable=singleton-comparison
        query = Query()\
            .match(Human)\
            .where(Human.admin == True, Human.age > 21)\
            .result(no_exec=True)
        # pylint: enable=singleton-comparison
        expected = (
            'MATCH (_a:Human)\n'
            'WHERE _a.admin = true\n'
            '  AND _a.age > 21\n'
            'RETURN _a'
        )
        self.assertEqual(query, expected)

    def test_defined_result(self):
        """
        Pass variables to the `result` method.
        """
        query = Query()\
            .match(None, 'a')\
            .match(None)\
            .result('a', no_exec=True)
        expected = (
            'MATCH (a)\n'
            'MATCH (_a)\n'
            'RETURN a'
        )
        self.assertEqual(query, expected)

    def test_match_path_no_direction(self):
        """
        Match a path with front or back direction.
        """
        class Human(Node):
            """
            Example of Node.
            """

        class Knows(Edge):
            """
            Example of Edge.
            """

        query = Query()\
            .match(None)\
            .connected_through(Knows)\
            .with_(Human)\
            .connected_through(None)\
            .with_(None)\
            .result(no_exec=True)
        expected = (
            'MATCH _p1 = (_a)-[_b:Knows]-(_c:Human)\n'
            'MATCH _p2 = (_c)-[_d]-(_e)\n'
            'RETURN _a, _b, _c, _d, _e'
        )
        self.assertEqual(query, expected)

    def test_match_path_with_directions(self):
        """
        Match a path with directions.
        """
        query = Query()\
            .match(None)\
            .connected_through(None)\
            .by(None)\
            .connected_through(None)\
            .to(None)\
            .result(no_exec=True)
        expected = (
            'MATCH _p1 = (_a)<-[_b]-(_c)\n'
            'MATCH _p2 = (_c)-[_d]->(_e)\n'
            'RETURN _a, _b, _c, _d, _e'
        )
        self.assertEqual(query, expected)

    def test_path_with_edge_instance(self):
        """
        Match a path with edge instance instead of Edge type.
        """
        class Knows(Edge):
            """
            Example of Edge.
            """
            class Meta(Edge.Meta):
                """
                Example of Edge.Meta.
                """
                primary_key = 'reason'

            reason = Props.String()

        instance = Knows(reason='some reason')
        query = Query()\
            .match(None)\
            .connected_through(instance)\
            .to(None)\
            .result(no_exec=True)
        expected = (
            'MATCH _p1 = (_a)-[_b:Knows]->(_c)\n'
            'WHERE _b.reason = "some reason"\n'
            'RETURN _a, _b, _c'
        )

        self.assertEqual(query, expected)

    def test_connected_through_with_connection_length(self):
        """
        Pass `conn` argument to the `connected_through` method.
        """
        # pylint: disable=invalid-name
        # This suppresses error for the method name.
        # pylint: enable=no-member
        class User(Node):
            """
            Example of Node.
            """

        class Knows(Edge):
            """
            Example of edge.
            """

        query = Query()\
            .match(User)\
            .connected_through(Knows, conn=(None, None))\
            .with_(User)\
            .connected_through(None, conn=(None, 3))\
            .with_(User)\
            .connected_through(Knows, conn=(3, None))\
            .with_(User)\
            .connected_through(None, conn=(1, 3))\
            .with_(User)\
            .result(no_exec=True)
        expected = (
            'MATCH _p1 = (_a:User)-[:Knows *]-(_c:User)\n'
            'WITH *, relationships(_p1) as _b\n'
            'MATCH _p2 = (_c)-[*..3]-(_e:User)\n'
            'WITH *, relationships(_p2) as _d\n'
            'MATCH _p3 = (_e)-[:Knows *3..]-(_g:User)\n'
            'WITH *, relationships(_p3) as _f\n'
            'MATCH _p4 = (_g)-[*1..3]-(_i:User)\n'
            'WITH *, relationships(_p4) as _h\n'
            'RETURN _a, _b, _c, _d, _e, _f, _g, _h, _i'
        )
        self.assertEqual(query, expected)
#
#
# # class MegaTests(TestCase):
# #     """
# #     Complex tests to cover everything.
# #     """
# #     def test_match(self):
# #         """
# #         Test `match` query.
# #         """
# #         class User(Node):
# #             """
# #             Example of Node.
# #             """
# #             name = Props.String()
# #
# #         class Knows(Edge):
# #             """
# #             Example of edge.
# #             """
# #             since = Props.Date()
# #
# #         user = User(name='John', uid='john')
# #         knows = Knows(since=date(1, 2, 3), uid='knows')
# #
# #         query = Query()\
# #             .match(None)\
# #             \
# #             .match(User, User.uid == 'some_uid', User.name == 'Kate')\
# #             \
# #             .match(user)\
# #             \
# #             .match(User)\
# #             .connected_through(Knows, Knows.since > date(1, 2, 3), conn=(1, 3))\
# #             .with_(None)\
# #             \
# #             .match(None)\
# #             .connected_through(None)\
# #             .with_(User)\
# #             \
# #             .match(user)\
# #             .connected_through(knows)\
# #             .with_((None, 'blah'))\
# #             \
# #             .result(no_exec=True)
# #         expected = (
# #             'MATCH (_a)\n'
# #             'MATCH (_b:User)\n'
# #             'WHERE _b.uid = "some_uid"\n'
# #             '  AND _b.name = "Kate"\n'
# #             'MATCH (_c:User)\n'
# #             'WHERE _c.uid = "john"\n'
# #             'MATCH _p1 = (_d:User)-[:Knows *1..3]-(_f)\n'
# #             'WITH *, relationships(_p1) as _e\n'
# #             'WHERE all(el in _e WHERE el.since > 34)\n'
# #             'MATCH _p2 = (_g)-[_h]-(_i:User)\n'
# #             'MATCH _p3 = (_j:User)-[_k:Knows]-(blah)\n'
# #             'WHERE _j.uid = "john"\n'
# #             '  AND _k.uid = "knows"\n'
# #             'RETURN _a, _b, _c, _d, _e, _f, _g, _h, _i, _j, _k, blah'
# #         )
# #
# #         self.assertEqual(query, expected)
