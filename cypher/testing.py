from unittest import TestCase

from .configuration import Config


class CypherTestCase(TestCase):
    """
    TestCase for this library.
    """
    @classmethod
    def setUpClass(cls):
        """
        Sets `testing` flag to the configuration.
        """
        Config.set_testing(True)
