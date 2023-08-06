import unittest

import numpy as np

from jina.indexer.chunk.numpy import NumpyIndexer
from jina.proto import jina_pb2


class TestMetaIndex(unittest.TestCase):
    def test_add(self):
        a = NumpyIndexer(data_path='numpyid.data')
        for _ in range(10):
            b = np.random.random([11, 25])
            c = [jina_pb2.Chunk() for _ in range(11)]
            a.add(b, c)
        print(a.size)

        a.dump('nptest.bin')
        a.close()
        d = NumpyIndexer.load('nptest.bin')
        print(d.size)
