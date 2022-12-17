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

    def test___init___00(self):
        with self.assertRaisesRegex(ValueError, f'^{self.__class__.__name__}.{sys._getframe().f_code.co_name}$'):
            raise ValueError(f'{self.__class__.__name__}.{sys._getframe().f_code.co_name}')

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
        with self.assertRaisesRegex(ValueError, '^ChromeDriverHelper.__init__引数エラー:'):
            test_target = ChromeDriverHelper("test")

    def test___init___04(self):
        """引数有コンストラクタ"""
        with self.assertRaises(ValueError):
            test_target = ChromeDriverHelper(self.url, "")

    def test___init___05(self):
        """引数有コンストラクタ"""
        test_target = ChromeDriverHelper(self.url, self.selectors)
        self.assertTrue(isinstance(test_target, ChromeDriverHelper))
        self.assertTrue(isinstance(test_target.value_object, ChromeDriverHelperValue))
        self.assertNotEqual(ChromeDriverHelper.value_object, test_target.value_object)
        self.assertEqual(ChromeDriverHelper.root_path, test_target.root_path)
        self.assertEqual(ChromeDriverHelper.driver_path, test_target.driver_path)
        self.assertEqual(ChromeDriverHelper.chrome_path, test_target.chrome_path)
        self.assertEqual(ChromeDriverHelper.profile_path, test_target.profile_path)

    def test___init___06(self):
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

    def test_get_value_object_01(self):
        test_target = ChromeDriverHelper(self.url, self.selectors)
        self.assertTrue(isinstance(test_target.get_value_object(), ChromeDriverHelperValue))

    def test_get_url_01(self):
        test_target = ChromeDriverHelper(self.url, self.selectors)
        self.assertTrue(isinstance(test_target.get_url(), str))
        self.assertEqual(test_target.get_url(), self.url)

    def test_get_selectors_01(self):
        test_target = ChromeDriverHelper(self.url, self.selectors)
        self.assertTrue(isinstance(test_target.get_selectors(), dict))
        # NOTE: 何故か以下がfailする
        self.assertEqual(test_target.get_selectors(), self.selectors)

    def test_get_items_01(self):
        """スクレイピング結果を得る"""
        test_target = ChromeDriverHelper(self.url, self.selectors)
        items = test_target.get_items()
        self.assertTrue(isinstance(items, dict))
        self.assertEqual(items['title_jp'], ['カテゴリー「若者」'])
        self.assertEqual(items['title_en'], ['カテゴリー「若者」'])
        self.assertEqual(items['image_urls'], ['https://1.bp.blogspot.com/-A2JAQ-NYAIA/YP9C6be6d0I/AAAAAAABe8A/iIY2L0uZJE4Iu-mLkqw93IX-a7-iAawMgCNcBGAsYHQ/s180-c/thumbnail_ofuro_onsen.jpg.', 'https://1.bp.blogspot.com/-jZrwPE-844I/YHDkKP6KJtI/AAAAAAABdlU/o8APw7M0MSIdQwk7gzjdp7vcUrgL45eMwCNcBGAsYHQ/s180-c/idol_fan_doutan_kyohi.png', 'https://1.bp.blogspot.com/-6Oh327001K4/YHDkJjqoolI/AAAAAAABdlQ/qTuxRmBLrFUas301O-jUVT9K5-N3CMSFQCNcBGAsYHQ/s180-c/idol_fan_doutan.png', 'https://1.bp.blogspot.com/-JFbAyXmlpck/X911Vz95oUI/AAAAAAABdBQ/nq2ko_9yom0E9UI6B3u2GxqX5q-oSSAVgCNcBGAsYHQ/s180-c/thumbnail_penlight_woman.jpg.', 'https://1.bp.blogspot.com/-LhO-bU-BDNE/X911V2ZkMAI/AAAAAAABdBU/NlRBsuo-fC8nwMwGP6MXAaZ2EkMZjEpYgCNcBGAsYHQ/s180-c/thumbnail_penlight_man.jpg.', 'https://1.bp.blogspot.com/-XkpQ9FZV518/X9GYKY4t4NI/AAAAAAABct0/qaGq803mkXwkpeiunKYL8JGfWZqupi5MQCNcBGAsYHQ/s180-c/idol_koisuru_girl_woman.png', 'https://1.bp.blogspot.com/-qJOC3lNBx-o/X9GYKL3X61I/AAAAAAABctw/gcQUKI_5cIoM1HEm794M2SxTP31HAcTPgCNcBGAsYHQ/s180-c/idol_koisuru_boy_man.png', 'https://1.bp.blogspot.com/-YxoakR5y2YQ/X3hGPNxXUcI/AAAAAAABbqU/VoO1RYvMaZE2NPOrrQcN0clr1W2KQ3OFQCNcBGAsYHQ/s180-c/school_kataomoi_kyoushitsu_girl.png', 'https://1.bp.blogspot.com/-eK4ppw33tg8/X3hGOyJr1lI/AAAAAAABbqQ/PkNuDBfjGhcxeBpiWu47w3LCtWGwxMSdACNcBGAsYHQ/s180-c/school_kataomoi_kyoushitsu_boy.png', 'https://1.bp.blogspot.com/-tzoOQwlaRac/X1LskKZtKEI/AAAAAAABa_M/89phuGIVDkYGY_uNKvFB6ZiNHxR7bQYcgCNcBGAsYHQ/s180-c/fashion_dekora.png', 'https://1.bp.blogspot.com/-gTf4sWnRdDw/X0B4RSQQLrI/AAAAAAABarI/MJ9DW90dSVwtMjuUoErxemnN4nPXBnXUwCNcBGAsYHQ/s180-c/otaku_girl_fashion.png', 'https://1.bp.blogspot.com/--L0axHlIFJ0/X0B4RtkgVQI/AAAAAAABarM/3S2zDdrLpFo6OsoPfo3_IdYZt0RIZuFVACNcBGAsYHQ/s180-c/otaku_girl_fashion_penlight.png', 'https://1.bp.blogspot.com/-K8DEj7le73Y/XuhW_wO41mI/AAAAAAABZjQ/NMEk02WcUBEVBDsEJpCxTN6T0NmqG20qwCNcBGAsYHQ/s180-c/kesyou_jirai_make.png', 'https://1.bp.blogspot.com/-DU9jll2ZQ38/XexqGlVzO9I/AAAAAAABWdQ/m0lQONbEfSgEjIN14h7iIfRh8WS5qwrFACNcBGAsYHQ/s180-c/gal_o_man.png', 'https://1.bp.blogspot.com/-1eGaiXw2_uI/XdttfhDU0GI/AAAAAAABWI0/w6sBI2UpvkcZzVGbn4b29Y5xJK5nBsG7gCNcBGAsYHQ/s180-c/jitensya_dekochari_man.png', 'https://1.bp.blogspot.com/-RQznwdreaqo/XWS5caChTnI/AAAAAAABUSY/eGJnuLSqmM8yyBuQIEQkY9OhesWtjAVBQCLcBGAs/s180-c/ensoku_picnic_people.png', 'https://1.bp.blogspot.com/-0mSeVobCq4g/XQjuUWYppcI/AAAAAAABTRI/OdgYzTfSmSM9Wwx6DU-PGt9R1Vy19FiFQCLcBGAs/s180-c/music_dance_sedai_takenokozoku.png', 'https://1.bp.blogspot.com/-3580-XaJKZs/XRbxHyuTD-I/AAAAAAABTcs/O5VKGJKxlh0Jm6jVqYBNv4fiJ1GWiDGUACLcBGAs/s180-c/thumbnail_gang_group.jpg'])

    def test_open_tabs(self):
        """open_new_tabs/save_image/next_tab/previous_tab/closeメソッドのテスト"""
        __driver = ChromeDriverHelper()
        __driver.open_new_tabs(self.image_url_list)
        for __url in self.image_url_list:
            uri = UriHelper(__url)
            __driver.save_image(uri.get_filename(), uri.get_ext())
            __driver.next_tab()
            time.sleep(1)
        for _ in self.image_url_list:
            __driver.previous_tab()
            time.sleep(1)
        for _ in self.image_url_list:
            __driver.close()
            time.sleep(1)
        # NOTE: prefsオプションが機能しないので、downloadsフォルダで確認する
        downloads_path = os.path.join(os.getenv("HOMEDRIVE"), os.getenv("HOMEPATH"), "downloads")
        __web_file_list = WebFileListHelper(self.image_url_list,
                                            '.png',
                                            # downloads_path,
                                            )
        self.assertTrue(__web_file_list.is_exist())
        # 後処理
        __web_file_list.delete_local_files()
        self.assertFalse(__web_file_list.is_exist())

    def test_download_image(self):
        """download_imageメソッドのテスト"""
        __driver = ChromeDriverHelper()
        for __url in self.image_url_list:
            __driver.download_image(__url)
            time.sleep(1)
        # NOTE: prefsオプションが機能しないので、downloadsフォルダで確認する
        downloads_path = os.path.join(os.getenv("HOMEDRIVE"), os.getenv("HOMEPATH"), "downloads")
        __web_file_list = WebFileListHelper(self.image_url_list,
                                            '.png',
                                            downloads_path,
                                            )
        self.assertTrue(__web_file_list.is_exist())
        # 後処理
        __web_file_list.delete_local_files()
        self.assertFalse(__web_file_list.is_exist())


if __name__ == '__main__':
    unittest.main()
