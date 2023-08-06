import unittest

from jina.executors import MetaIndexer
from jina.proto import jina_pb2


class TestMetaIndex(unittest.TestCase):
    def test_add(self):
        a = MetaIndexer(data_path='meta.data', parse_type='doc')
        dd = []
        for j in range(10):
            d = jina_pb2.Document()
            d.raw_bytes = b'dsa' * j
            d.doc_id = j
            dd.append(d)
        a.add_without_keys(dd)
        print(a.num_metas)
        a.add_without_keys(dd)
        print(a.num_metas)
        a.dump('meta.bin')
        a.close()

        c = MetaIndexer(data_path='meta.data', parse_type='doc', exist_mode='r')

        print(c.query([j for j in range(10, 20)]))

        print(c.num_metas)

        c.add_without_keys(dd)
        print(c.num_metas)
