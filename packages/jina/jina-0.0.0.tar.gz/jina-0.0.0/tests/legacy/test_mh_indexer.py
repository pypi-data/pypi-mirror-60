import os
import unittest

from jina.indexer.base import BaseIndexer


class TestMHIndexer(unittest.TestCase):

    def setUp(self):
        dirname = os.path.dirname(__file__)
        self.exec_yaml_path1 = os.path.join(dirname, 'yaml', 'base-indexer2.yml')
        self.exec_yaml_path2 = os.path.join(dirname, 'yaml', 'base-indexer3.yml')
        self.exec_yaml_path3 = os.path.join(dirname, 'yaml', 'base-indexer4.yml')

    def test_ind1(self):
        self.assertRaises(ValueError, BaseIndexer.load_yaml, self.exec_yaml_path1)

    def test_ind3(self):
        self.assertRaises(ValueError, BaseIndexer.load_yaml, self.exec_yaml_path1)

    def test_ind2(self):
        mhi = BaseIndexer.load_yaml(self.exec_yaml_path2)
        print(mhi)
