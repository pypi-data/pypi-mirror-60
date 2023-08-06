import gzip
import unittest
from pathlib import Path

from openqlab import io

filedir = Path(__file__).parent


class TestInit(unittest.TestCase):
    def test_list_formats(self):
        io.list_formats()
