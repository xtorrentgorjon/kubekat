import unittest
from app import string_to_list

class TestApp(unittest.TestCase):
    def test_unittest_string_to_list(self):
        input_string = "sla, teststr :  value1, maintainer:value2   ,, team     :SRE"
        output_compare = ["sla", "teststr:value1", "maintainer:value2", "team:SRE"]
        output_list = string_to_list(input_string)
        self.assertEqual(output_list, output_compare)

if __name__ == '__main__':
    unittest.main()
