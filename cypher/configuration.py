from typing import Mapping

from neo4j.v1 import GraphDatabase

from .exceptions import NoInitiation


class DB:
    """
    Handler for the database connection.
    """
    def __init__(self, url: str, username: str, password: str):
        """
        @TODO: add DB interface to support other database engines than Neo4j

        :param url: URL of the database
        :param username: username of the database user
        :param password: password of the database user
        """
        self.url = url
        self.username = username
        self.password = password
        self._driver = None

    @property
    def driver(self) -> GraphDatabase.driver:
        """
        Get or create driver.

        :return: database driver
        """
        if not self._driver:
            self._driver = GraphDatabase.driver(
                self.url,
                auth=(self.username, self.password),
            )

        return self._driver


class Config:
    """
    Config singleton.
    """
    databases = {}
    testing = False

    def __init__(self):
        raise NoInitiation

    @classmethod
    def set_databases(cls, databases: Mapping[str, Mapping[str, str]]):
        cls.databases = {}
        for key, value in databases.items():
            cls.databases[key] = DB(**value)

    @classmethod
    def set_testing(cls, value: bool):
        cls.testing = value
