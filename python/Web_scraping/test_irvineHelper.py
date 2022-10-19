import unittest
from irvineHelper import *
from webFileListHelper import *


class MyTestCase(unittest.TestCase):

    def setUp(self):
        print("setup")
        # テスト　若者 | かわいいフリー素材集 いらすとや
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
        del self.image_url_list

    def test___init___01(self):
        """引数無コンストラクタ"""
        with self.assertRaises(ValueError):
            IrvineHelper()

    def test___init___02(self):
        """引数有コンストラクタ"""
        with self.assertRaises(ValueError):
            IrvineHelper("test.txt")

    def test___init___03(self):
        """引数有コンストラクタ"""
        with self.assertRaises(ValueError):
            IrvineHelper(IrvineHelper.list_path, "test.txt")

    def test___init___04(self):
        """引数有コンストラクタ"""
        test_target = IrvineHelper(self.image_url_list)
        self.assertTrue(isinstance(test_target, IrvineHelper))
        self.assertEqual(IrvineHelper.list_path, test_target.list_path)
        self.assertEqual(IrvineHelper.running, test_target.running)
        self.assertNotEqual(IrvineHelper.value_object, test_target.value_object)
        self.assertEqual(IrvineHelper.list_path, test_target.value_object.list_path)
        self.assertEqual(IrvineHelperValue.exe_path, test_target.value_object.exe_path)

    def test___init___05(self):
        """引数有コンストラクタ"""
        __irvine_helper = IrvineHelper(self.image_url_list)
        test_target = IrvineHelper(__irvine_helper.value_object)
        self.assertTrue(isinstance(test_target, IrvineHelper))
        self.assertEqual(IrvineHelper.list_path, test_target.list_path)
        self.assertEqual(IrvineHelper.running, test_target.running)
        self.assertNotEqual(IrvineHelper.value_object, test_target.value_object)
        self.assertEqual(IrvineHelper.list_path, test_target.value_object.list_path)
        self.assertEqual(IrvineHelperValue.exe_path, test_target.value_object.exe_path)

    def test_download(self):
        """ダウンロード"""
        test_target = IrvineHelper(self.image_url_list)
        test_target.download()
        __test_target = WebFileListHelper(self.image_url_list)
        self.assertTrue(__test_target.is_exist())
        # 後始末
        __test_target.delete_images()


if __name__ == '__main__':
    unittest.main()
