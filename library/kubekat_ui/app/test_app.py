import unittest
import app

class TestKube(unittest.TestCase):
    def test_1(self):
        input_string = "sla, teststr :  value1, maintainer:value2   ,, team     :SRE"
        output_compare = ["sla", "teststr:value1", "maintainer:value2", "team:SRE"]
        output_list = app.string_to_list(input_string)
        self.assertEqual(output_list, output_compare)

if __name__ == '__main__':
    unittest.main()
