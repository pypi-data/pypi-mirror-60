# coding=utf-8
from __future__ import unicode_literals
import unittest

from pod_base import InvalidDataException

from tests.config import *
from pod_export import PodExport


class TestPodExport(unittest.TestCase):
    __slots__ = "__export"

    def setUp(self):
        self.__export = PodExport(api_token=API_TOKEN, server_type=SERVER_MODE)

    def test_01_get_export_list(self):
        result = self.__export.get_export_list()
        self.assertIsInstance(result, list, msg="get export list : check instance")

    def test_01_get_export_list_validation_error(self):
        with self.assertRaises(InvalidDataException, msg="get export list : validation error"):
            self.__export.get_export_list(statusCode="ABCD")
