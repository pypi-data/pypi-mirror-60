from pathlib import Path

from unittest import TestCase
from netaddr import IPAddress

import clustipy


class TestClustIPy(TestCase):
    def setUp(self):
        self.ipaddr = [IPAddress(_) for _ in Path('tests/test_address').read_text().splitlines()]

    def test_agglomerative(self):
        result = clustipy.agglomerative(self.ipaddr, 20)
        self.assertLessEqual(len(result), 20)
        for a in self.ipaddr:
            self.assertGreater(len([_ for _ in result if a in _]), 0)

    def test_kmeans(self):
        result = clustipy.kmeans(self.ipaddr, 20)
        self.assertLessEqual(len(result), 20)
        for a in self.ipaddr:
            self.assertGreater(len([_ for _ in result if a in _]), 0)
