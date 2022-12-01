import unittest
from webFileHelper import *


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

    def tearDown(self):
        print("tearDown")
        del self.image_url
        del self.image_url_list

    def test___init___01(self):
        """引数無コンストラクタ"""
        with self.assertRaises(ValueError):
            WebFileHelper()

    def test___init___02(self):
        """引数有コンストラクタ"""
        with self.assertRaises(ValueError):
            WebFileHelper(self.image_url_list)

    def test___init___03(self):
        """引数有コンストラクタ"""
        test_target = WebFileHelper(self.image_url)
        self.assertTrue(isinstance(test_target, WebFileHelper))
        self.assertNotEqual(WebFileHelper.dst_file_name, test_target.dst_file_name)
        self.assertEqual(WebFileHelper.ext_list, test_target.ext_list)
        self.assertNotEqual(WebFileHelper.value_object, test_target.value_object)
        self.assertEqual(WebFileHelper.folder_path, test_target.folder_path)
        self.assertEqual(WebFileHelper.folder_path, test_target.value_object.folder_path)
        self.assertEqual(self.image_url, test_target.value_object.url)

    def test___init___04(self):
        """引数有コンストラクタ"""
        __web_file_helper = WebFileHelper(self.image_url)
        test_target = WebFileHelper(__web_file_helper.value_object)
        self.assertTrue(isinstance(test_target, WebFileHelper))
        self.assertNotEqual(WebFileHelper.dst_file_name, test_target.dst_file_name)
        self.assertEqual(WebFileHelper.ext_list, test_target.ext_list)
        self.assertNotEqual(WebFileHelper.value_object, test_target.value_object)
        self.assertEqual(WebFileHelper.folder_path, test_target.folder_path)
        self.assertEqual(WebFileHelper.folder_path, test_target.value_object.folder_path)
        self.assertEqual(self.image_url, test_target.value_object.url)

    def test_is_image(self):
        """対象URLは画像ファイルである"""
        test_target = WebFileHelper(self.image_url)
        self.assertTrue(test_target.is_image())

    def test_is_exist(self):
        """対象URLのファイルはローカルに存在する"""
        test_target = WebFileHelper(self.image_url)
        self.assertFalse(test_target.is_exist())

    def test_get_url(self):
        """対象URLを取得する"""
        test_target = WebFileHelper(self.image_url)
        self.assertEqual(test_target.get_url(), self.image_url)

    def test_get_path(self):
        """ファイルのフルパスを得る"""
        test_target = WebFileHelper(self.image_url)
        self.assertEqual(test_target.get_path(), os.path.join(test_target.get_folder_path(),
                                                              test_target.get_filename() + test_target.get_ext(),
                                                              ).replace(os.sep, '/'))

    def test_get_folder_path(self):
        """フォルダーパスを得る"""
        test_target = WebFileHelper(self.image_url)
        self.assertEqual(test_target.get_folder_path(), test_target.value_object.folder_path)

    def test_download_requests(self):
        """フォルダーパスを得る"""
        test_target = WebFileHelper(self.image_url)
        test_target.download_requests()
        self.assertTrue(test_target.is_exist())
        # 後処理
        test_target.delete_local_file()


if __name__ == '__main__':
    unittest.main()

