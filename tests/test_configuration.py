"""
Tests for `configuration.py`.
"""
from unittest import TestCase

from cypher import Config, exceptions


class ConfigTests(TestCase):
    """
    Tests for `Config`.
    """
    def test_set_databases(self):
        """
        Check if databases are substituted for the new ones.
        """
        Config.set_databases({
            'default': {
                'url': 'bolt://cypher-db:7687',
                'username': 'neo4j',
                'password': 'cypher',
            },
        })

        default_database = Config.databases.get('default', None)
        self.assertIsNotNone(default_database)

    def test_set_testing(self):
        """
        Check if `set_testing` sets the test mode.
        """
        old_value = Config.testing
        Config.set_testing(True)

        self.assertNotEqual(old_value, Config.testing)

    def test_create_instance(self):
        """
        Config instantiation should be impossible.
        """
        with self.assertRaises(exceptions.NoInitiation):
            Config()
