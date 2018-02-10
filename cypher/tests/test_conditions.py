# """
# Tests for conditions.py.
# """
# import unittest
#
# from ..conditions import Value, StringValue
# from ..models import ModelDetails, Node
# from ..props import Props
#
#
# class User(Node):
#     """
#     Example of a Node.
#     """
#     job = Props.String()
#     title = Props.String()
#
#
# DETAILS = {
#     'a': ModelDetails(User, 'a'),
# }
#
#
# class ValueTests(unittest.TestCase):
#     """
#     Tests for `Value` class.
#     """
#     def test_eq_to_string(self):
#         """
#         Test equality to a string value.
#         """
#         actual = (User.job == 'some"nameЖ')(DETAILS, 'a')
#         expected = 'a.job = "some\\"nameЖ"'
#         self.assertEqual(actual, expected)
#
#         actual = (User.job.lower() == 'some"nameЖ')(DETAILS, 'a')
#         expected = 'toLower(a.job) = "some\\"nameЖ"'
#         self.assertEqual(actual, expected)
#
#         actual = (Value('a.job') == 'Developer')(DETAILS, 'a')
#         expected = 'a.job = "Developer"'
#         self.assertEqual(actual, expected)
#
#         actual = (Value('a.job').to_bool() == True)(DETAILS, 'a')
#         expected = 'toBoolean(a.job) = true'
#         self.assertEqual(actual, expected)
#
#         actual = (StringValue('a.job').lower() == 'Developer')(DETAILS, 'a')
#         expected = 'toLower(a.job) = "Developer"'
#         self.assertEqual(actual, expected)
#
#     # def test_eq_to_string(self):
#     #     """
#     #     Test equality to a string value.
#     #     """
#     #     actual = (User.job == 'some"nameЖ')(details, 'a')
#     #     expected = 'a.job = "some\\"nameЖ"'
#     #     self.assertEqual(actual, expected)
#     #
#     #     actual = (Value('a.job') == 'Developer')(details, 'a')
#     #     expected = 'a.job = "Developer"'
#     #     self.assertEqual(actual, expected)
#
#     # def test_to_bool(self):
#     #     """
#     #     Test `to_bool` transformation.
#     #     """
#     #     actual = (Value('name').to_bool() == 'some"nameЖ')('a')
#     #     expected = 'toBoolean(a.name) = true'
#     #     self.assertEqual(actual, expected)
#
#
# # User.job == 'Developer'
# # Value('a.job') == 'Developer'
# # 'a.job = "Developer"'
# #
# # User.job == User.title
# # User.job == Value('a.title')
# # Value('a.job') == User.title
# # Value('a.job') == Value('a.title')
# # 'a.job = a.title'
# #
# # User.job.lower() == User.title
# # User.job.lower() == Value('a.title')
# # Value('a.job').lower() == User.title
# # Value('a.job').lower() == Value('a.title')
# # 'toLower(a.job) = a.title'
# #
# # User.job.toLower() == 'Developer'
# # Value('a.job').toLower() == 'Developer'
# # 'toLower(a.job) = "Developer"'
# #
# # User.job == User.title.lower()
# # User.job == Value('a.title').lower()
# # Value('a.job') == User.title.lower()
# # Value('a.job') == Value('a.title').lower()
# # 'a.job = toLower(a.title)'
# #
# # User.job.lower() == User.title.lower()
# # User.job.lower() == Value('a.title').lower()
# # Value('a.job').lower() == User.title.lower()
# # Value('a.job').lower() == Value('a.title').lower()
# # 'toLower(a.job) = toLower(a.title)'
