import unittest
from irvineHelper import *


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
        irvine_helper = IrvineHelper()
        self.assertTrue(isinstance(irvine_helper, IrvineHelper))
        self.assertEqual(IrvineHelper.list_path, irvine_helper.list_path)
        self.assertEqual(IrvineHelper.running, irvine_helper.running)
        self.assertNotEqual(IrvineHelper.value_object, irvine_helper.value_object)
        self.assertEqual(IrvineHelper.list_path, irvine_helper.value_object.list_path)
        self.assertEqual(IrvineHelperValue.exe_path, irvine_helper.value_object.exe_path)

    def test___init___02(self):
        """引数有コンストラクタ"""
        irvine_helper = IrvineHelper(self.image_url_list)
        self.assertTrue(isinstance(irvine_helper, IrvineHelper))
        self.assertEqual(IrvineHelper.list_path, irvine_helper.list_path)
        self.assertEqual(IrvineHelper.running, irvine_helper.running)
        self.assertNotEqual(IrvineHelper.value_object, irvine_helper.value_object)
        self.assertEqual(IrvineHelper.list_path, irvine_helper.value_object.list_path)
        self.assertEqual(IrvineHelperValue.exe_path, irvine_helper.value_object.exe_path)

    def test___init___03(self):
        """引数有コンストラクタ"""
        __irvine_helper = IrvineHelper(self.image_url_list)
        irvine_helper = IrvineHelper(__irvine_helper)
        self.assertTrue(isinstance(irvine_helper, IrvineHelper))
        self.assertEqual(IrvineHelper.list_path, irvine_helper.list_path)
        self.assertEqual(IrvineHelper.running, irvine_helper.running)
        self.assertNotEqual(IrvineHelper.value_object, irvine_helper.value_object)
        self.assertEqual(IrvineHelper.list_path, irvine_helper.value_object.list_path)
        self.assertEqual(IrvineHelperValue.exe_path, irvine_helper.value_object.exe_path)

    def test_something(self):
        """引数有コンストラクタ"""
        irvine_helper = IrvineHelper(self.image_url_list)
        # irvine_helper.download()
        self.assertTrue(isinstance(irvine_helper, IrvineHelper))
        self.assertEqual(True, False)  # add assertion here


if __name__ == '__main__':
    unittest.main()
