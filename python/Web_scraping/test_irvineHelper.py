import unittest
from irvineHelper import *
from webFileListHelper import *


class MyTestCase(unittest.TestCase):

    def setUp(self):
        print("setup")
        # TODO: gitに画像アップロードして、その画像ダウンロードに変更する
        self.image_url_list = [
            'https://・・・/画像1.png',
            'https://・・・/画像2.png',
        ]
        self.download_file_name = [
            '0000.png',
            '0001.png',
        ]

    def tearDown(self):
        print("tearDown")
        del self.image_url_list
        del self.download_file_name

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

    def test_download_01(self):
        """ダウンロード"""
        test_target = IrvineHelper(self.image_url_list)
        test_target.download()
        __test_target = WebFileListHelper(self.image_url_list)
        self.assertTrue(__test_target.is_exist())
        # 後処理
        __test_target.delete_local_files()
        self.assertFalse(__test_target.is_exist())

    def test_download_02(self):
        """ダウンロード"""
        test_target = IrvineHelper(self.image_url_list, None, self.download_file_name)
        test_target.download()
        __test_target = WebFileListHelper(self.image_url_list)
        self.assertTrue(__test_target.is_exist())
        # 後処理
        __test_target.delete_local_files()
        self.assertFalse(__test_target.is_exist())


if __name__ == '__main__':
    unittest.main()
