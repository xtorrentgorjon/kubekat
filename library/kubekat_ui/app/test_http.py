# These tests are run against the testing environment
import unittest
import urllib.request
import urllib.error

class TestHTTPReturnCode(unittest.TestCase):
    def setUp(self):
        self.pages_200 = ["https://kubekat-test.home.sendotux.net/label",
            "https://kubekat-test.home.sendotux.net/pvc",
            "https://kubekat-test.home.sendotux.net/about"]
        self.pages_400 = [] # ["https://kubekat-test.home.sendotux.net"]
        self.pages_500 = ["https://kubekat-test.home.sendotux.net/error-http-500-test"]

    def test_http_200(self):
        for page in self.pages_200:
            response = urllib.request.urlopen(page)
            http_code = response.code
            self.assertEqual(http_code, 200)

    def test_http_400(self):
        for page in self.pages_400:
            self.assertRaises(urllib.error.HTTPError, urllib.request.urlopen, page)

    def test_http_500(self):
        for page in self.pages_500:
            self.assertRaises(urllib.error.HTTPError, urllib.request.urlopen, page)

if __name__ == '__main__':
    unittest.main()
