import os
import unittest

from jina.legacy.old_flow import Flow
from jina.proto import remove_envelope


class TestFeatureExtraction(unittest.TestCase):
    def setUp(self):
        self.dirname = os.path.dirname(__file__)
        self.test_file = os.path.join(self.dirname, 'sonnets_small.txt')
        self.yamldir = os.path.join(self.dirname, 'yaml')
        self.dump_flow_path = os.path.join(self.dirname, 'test-flow.bin')

        os.unsetenv('http_proxy')
        os.unsetenv('https_proxy')
        self.test_dir = os.path.join(self.dirname, 'test_flow')
        self.indexer1_bin = os.path.join(self.test_dir, 'my_faiss_indexer.bin')
        self.indexer2_bin = os.path.join(self.test_dir, 'my_fulltext_indexer.bin')
        self.encoder_bin = os.path.join(self.test_dir, 'my_transformer.bin')
        if os.path.exists(self.test_dir):
            self.tearDown()
        os.mkdir(self.test_dir)

        os.environ['TEST_WORKDIR'] = self.test_dir

    def tearDown(self):
        for k in [self.indexer1_bin, self.indexer2_bin, self.encoder_bin, self.dump_flow_path]:
            if os.path.exists(k):
                os.remove(k)
        os.rmdir(self.test_dir)

    def test_index_flow(self):

        flow = (Flow(check_version=False, route_table=False)
                .add_preprocessor(name='prep', yaml_path='SentSplitPreprocessor')
                .add_encoder(yaml_path=os.path.join(self.dirname, 'yaml/flow-transformer.yml'), replicas=3))

        bytes_generator = (v.encode() for v in open(self.test_file, encoding='utf8'))

        cb = lambda x: print(remove_envelope(x))

        with flow.build(backend='thread') as f:
            f.index(bytes_gen=bytes_generator, callback=cb, batch_size=8)
