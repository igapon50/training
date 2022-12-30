import unittest
from scraping import *


class MyTestCase(unittest.TestCase):
    def setUp(self):
        print("setup")
        # テスト　若者 | かわいいフリー素材集 いらすとや
        self.site_url = 'https://www.irasutoya.com/p/figure.html'
        self.selectors = {
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
        del self.selectors

    def test___init___01(self):
        """引数無コンストラクタ"""
        with self.assertRaises(ValueError):
            test_target = Scraping()

    def test___init___02(self):
        """引数無コンストラクタ"""
        with self.assertRaises(ValueError):
            test_target = Scraping(self.site_url)

    def test___init___03(self):
        """引数有コンストラクタ"""
        test_target = Scraping(self.site_url, self.selectors)
        self.assertTrue(isinstance(test_target, Scraping))
        self.assertNotEqual(Scraping.value_object, test_target.value_object)
        self.assertEqual(self.site_url, test_target.value_object.site_url)

    def test_scraping_chrome_driver(self):
        """スクレイピング結果"""
        test_target = Scraping(self.site_url, self.selectors)
        # TODO: 以下に対応させたい。selectorsのkeysとvaluesをスクレイピングして、結果をdictでvalue_objectに保持させる
        # test_target.scraping_chrome_driver()


if __name__ == '__main__':
    unittest.main()
