import unittest

import numpy as np

from jina.logging.profile import TimeContext
from jina.proto import array2blob, blob2array


class TestCLI(unittest.TestCase):
    def test_quant(self):
        a = np.random.random([100, 100])
        a = a.astype(np.float32)
        for q in ('none', 'fp16', 'uint8'):
            print('-----%s-----' % q)
            m_a = array2blob(a, quantization=q)
            print('size: %d' % len(m_a.SerializeToString()))
            b = blob2array(m_a)
            self.assertNotEqual(id(a), id(b))
            print('reconstruction err: %.6f' % abs(a - b).mean())

    def test_dtype(self):
        for d in (np.float16, np.float32, np.float64):
            a = np.random.random([100, 100])
            a = a.astype(d)
            m_a = array2blob(a, quantization='uint8')
            print('size: %d' % len(m_a.SerializeToString()))
            b = blob2array(m_a)
            self.assertEqual(b.dtype, a.dtype)

    def test_speed(self):
        num_arrays = 500
        a = [np.random.random([1000, 1000]) for _ in range(num_arrays)]
        for q in ('none', 'fp16', 'uint8'):
            with TimeContext(q):
                for aa in a:
                    blob2array(array2blob(aa, quantization=q))
