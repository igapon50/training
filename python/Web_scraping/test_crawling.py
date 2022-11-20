import unittest
from crawling import *


class MyTestCase(unittest.TestCase):
    def setUp(self):
        print("setup")
        # テスト　若者 | かわいいフリー素材集 いらすとや
        self.site_url = 'https://www.irasutoya.com/p/figure.html'
        self.site_selectors = {
            'page_urls': [
                (By.XPATH,
                 '//*[@id="banners"]/a/img',
                 lambda el: el.get_attribute("src")
                 ),
            ]
        }
        self.crawling_file_path = './crawling_list_test.txt'

    def tearDown(self):
        print("tearDown")
        del self.site_url
        del self.site_selectors

    def test___init___01(self):
        """引数無コンストラクタ"""
        with self.assertRaises(ValueError):
            test_target = Crawling()

    def test___init___02(self):
        """引数無コンストラクタ"""
        with self.assertRaises(ValueError):
            test_target = Crawling(self.site_url)

    def test___init___03(self):
        """引数無コンストラクタ"""
        test_target = Crawling(self.site_url, self.site_selectors)
        self.assertTrue(isinstance(test_target, Crawling))
        self.assertNotEqual(Crawling.value_object, test_target.value_object)
        self.assertEqual(Crawling.crawling_file_path, test_target.value_object.crawling_file_path)

    def test___init___04(self):
        """引数無コンストラクタ"""
        test_target = Crawling(self.site_url, self.site_selectors, self.crawling_file_path)
        self.assertTrue(isinstance(test_target, Crawling))
        self.assertNotEqual(Crawling.value_object, test_target.value_object)
        self.assertNotEqual(Crawling.crawling_file_path, test_target.value_object.crawling_file_path)

    def test_get_crawling_file_path_01(self):
        test_target = Crawling(self.site_url, self.site_selectors)
        self.assertEqual(Crawling.crawling_file_path, test_target.get_crawling_file_path())

    def test_get_crawling_file_path_02(self):
        test_target = Crawling(self.site_url, self.site_selectors, self.crawling_file_path)
        self.assertNotEqual(Crawling.crawling_file_path, test_target.get_crawling_file_path())

    def test_save_text(self):
        test_target = Crawling(self.site_url, self.site_selectors)
        self.assertTrue(test_target.save_text())

    def test_load_text(self):
        test_target = Crawling(self.site_url, self.site_selectors)
        __value_object = test_target.get_value_object()
        self.assertTrue(test_target.save_text())
        self.assertTrue(test_target.load_text())
        self.assertEqual(__value_object, test_target.get_value_object())


if __name__ == '__main__':
    unittest.main()
