import unittest
from chromeDriverHelper import *
from webFileListHelper import *


class MyTestCase(unittest.TestCase):

    def setUp(self):
        print("setup")
        # テスト　若者 | かわいいフリー素材集 いらすとや
        self.image_url = 'https://1.bp.blogspot.com/-tzoOQwlaRac/X1LskKZtKEI/AAAAAAABa_M/'\
                         '89phuGIVDkYGY_uNKvFB6ZiNHxR7bQYcgCNcBGAsYHQ/'\
                         's180-c/fashion_dekora.png'
        self.image_url_list = [
            'https://1.bp.blogspot.com/-tzoOQwlaRac/X1LskKZtKEI/AAAAAAABa_M/'
            '89phuGIVDkYGY_uNKvFB6ZiNHxR7bQYcgCNcBGAsYHQ/'
            's180-c/fashion_dekora.png',
            'https://1.bp.blogspot.com/-gTf4sWnRdDw/X0B4RSQQLrI/AAAAAAABarI/'
            'MJ9DW90dSVwtMjuUoErxemnN4nPXBnXUwCNcBGAsYHQ/'
            's180-c/otaku_girl_fashion.png',
            'https://1.bp.blogspot.com/-K8DEj7le73Y/XuhW_wO41mI/AAAAAAABZjQ/'
            'NMEk02WcUBEVBDsEJpCxTN6T0NmqG20qwCNcBGAsYHQ/'
            's180-c/kesyou_jirai_make.png',
        ]
        self.url = 'https://www.irasutoya.com/search/label/%E8%8B%A5%E8%80%85'
        self.selectors = {
            'title_jp': [
                (By.XPATH,
                 '//*[@id="Blog1"]/div[1]/div[3]/h2',
                 lambda el: el.text),
            ],
            'title_en': [
                (By.XPATH,
                 '//*[@id="Blog1"]/div[1]/div[3]/h2',
                 lambda el: el.text),
            ],
            'image_urls': [
                (By.XPATH,
                 '//*[@id="post"]/div[1]/a/img',
                 lambda el: el.get_attribute("src")
                 ),
            ]
        }

    def tearDown(self):
        print("tearDown")
        del self.image_url
        del self.image_url_list

    def test___init___01(self):
        """引数無コンストラクタ"""
        test_target = ChromeDriverHelper()
        self.assertTrue(isinstance(test_target, ChromeDriverHelper))
        self.assertFalse(isinstance(test_target.value_object, ChromeDriverHelperValue))
        self.assertEqual(ChromeDriverHelper.root_path, test_target.root_path)
        self.assertEqual(ChromeDriverHelper.driver_path, test_target.driver_path)
        self.assertEqual(ChromeDriverHelper.chrome_path, test_target.chrome_path)
        self.assertEqual(ChromeDriverHelper.profile_path, test_target.profile_path)

    def test___init___02(self):
        """引数有コンストラクタ"""
        test_target = ChromeDriverHelper("", self.selectors)
        self.assertTrue(isinstance(test_target, ChromeDriverHelper))
        self.assertFalse(isinstance(test_target.value_object, ChromeDriverHelperValue))
        self.assertEqual(ChromeDriverHelper.root_path, test_target.root_path)
        self.assertEqual(ChromeDriverHelper.driver_path, test_target.driver_path)
        self.assertEqual(ChromeDriverHelper.chrome_path, test_target.chrome_path)
        self.assertEqual(ChromeDriverHelper.profile_path, test_target.profile_path)

    def test___init___03(self):
        """引数有コンストラクタ"""
        test_target = ChromeDriverHelper(self.url, "")
        self.assertTrue(isinstance(test_target, ChromeDriverHelper))
        self.assertFalse(isinstance(test_target.value_object, ChromeDriverHelperValue))
        self.assertEqual(ChromeDriverHelper.root_path, test_target.root_path)
        self.assertEqual(ChromeDriverHelper.driver_path, test_target.driver_path)
        self.assertEqual(ChromeDriverHelper.chrome_path, test_target.chrome_path)
        self.assertEqual(ChromeDriverHelper.profile_path, test_target.profile_path)

    def test___init___04(self):
        """引数有コンストラクタ"""
        test_target = ChromeDriverHelper(self.url, self.selectors)
        self.assertTrue(isinstance(test_target, ChromeDriverHelper))
        self.assertTrue(isinstance(test_target.value_object, ChromeDriverHelperValue))
        self.assertNotEqual(ChromeDriverHelper.value_object, test_target.value_object)
        self.assertEqual(ChromeDriverHelper.root_path, test_target.root_path)
        self.assertEqual(ChromeDriverHelper.driver_path, test_target.driver_path)
        self.assertEqual(ChromeDriverHelper.chrome_path, test_target.chrome_path)
        self.assertEqual(ChromeDriverHelper.profile_path, test_target.profile_path)

    def test___init___05(self):
        """引数有コンストラクタ"""
        __web_file_list_helper = ChromeDriverHelper(self.url, self.selectors)
        test_target = ChromeDriverHelper(__web_file_list_helper.value_object)
        self.assertTrue(isinstance(test_target, ChromeDriverHelper))
        self.assertTrue(isinstance(test_target.value_object, ChromeDriverHelperValue))
        self.assertNotEqual(ChromeDriverHelper.value_object, test_target.value_object)
        self.assertEqual(ChromeDriverHelper.root_path, test_target.root_path)
        self.assertEqual(ChromeDriverHelper.driver_path, test_target.driver_path)
        self.assertEqual(ChromeDriverHelper.chrome_path, test_target.chrome_path)
        self.assertEqual(ChromeDriverHelper.profile_path, test_target.profile_path)

    def test_get_title(self):
        """ファイルリストを得る"""
        test_target = ChromeDriverHelper(self.url, self.selectors)
        self.assertEqual(test_target.get_title(), "カテゴリー「若者」")

    def test_open_tabs(self):
        """open_tabs/download_image/next_tab/previous_tab/closeメソッドのテスト"""
        __driver = ChromeDriverHelper()
        __driver.open_tabs(self.image_url_list)
        for _ in self.image_url_list:
            __driver.download_image()
            __driver.next_tab()
            time.sleep(1)
        for _ in self.image_url_list:
            __driver.previous_tab()
            time.sleep(1)
        for _ in self.image_url_list:
            __driver.close()
            time.sleep(1)
        __web_file_list = WebFileListHelper(self.image_url_list)
        self.assertTrue(__web_file_list.is_exist())
        # 後処理
        __web_file_list.delete_images()


if __name__ == '__main__':
    unittest.main()
