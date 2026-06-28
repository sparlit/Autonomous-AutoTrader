import os
import unittest
class TestSystemIntegrity(unittest.TestCase):
    def test_src(self):
        self.assertTrue(os.path.exists("src/python/main_engine.py"))
        self.assertTrue(os.path.exists("src/mql5/Include/AAT_Protocol.mqh"))
    def test_root(self):
        self.assertTrue(os.path.exists("run_aat.py"))
        self.assertTrue(os.path.exists("rules.md"))
        self.assertTrue(os.path.exists("VERSION.txt"))
if __name__ == "__main__": unittest.main()
