import unittest

from tests import JinaTestCase


class MyTestCase(JinaTestCase):

    def test_load_yaml1(self):
        from jina.executors.indexers.numpy import NumpyIndexer
        NumpyIndexer.load_config('yaml/dummy_exec1.yml')
        self.add_tmpfile('test.gzip')

    def test_load_yaml2(self):
        from jina.executors import BaseExecutor
        a = BaseExecutor.load_config('yaml/dummy_exec1.yml')
        a.close()
        self.add_tmpfile('test.gzip')
        b = BaseExecutor.load_config('yaml/dummy_exec1.yml')
        b.save()
        self.add_tmpfile(b.save_abspath)
        b.close()


if __name__ == '__main__':
    unittest.main()
