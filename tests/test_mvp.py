import unittest

def hello_world():
    return "Hello World!"

class TestMVP(unittest.TestCase):

    def test_mvp(self):
        self.assertEqual(1, 1)

    def test2(self):
        self.assertEqual(hello_world(), "Hello World!")    

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)