from unittest import TestCase
import unittest

if 'env path':
    from pathlib import Path
    import sys

    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from image_rename import (
        __version__,
    )
    from image_rename.cli import main as cli_main

    sys.path.remove(sys.path[0])


class ImageRenameAppTests(TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.work_dir = Path(__file__).parent / Path('image')

    def test_feed_setting_file(self):
        setting_file_path = Path(__file__).parent / Path('setting.py')
        cli_main(setting_file_path)

    def test_default(self):
        cli_main(Path(__file__).parent.parent / Path('config.py'))


class CLITests(unittest.TestCase):

    def test_show_version(self):
        print(__version__)
        self.assertTrue(len(__version__) > 0)


def test_setup():
    # suite_list = [unittest.TestLoader().loadTestsFromTestCase(class_module) for class_module in (CLITests, )]
    # suite_class_set = unittest.TestSuite(suite_list)

    suite_function_set = unittest.TestSuite()
    suite_function_set.addTest(CLITests('test_show_version'))

    suite = suite_function_set  # pick one of two: suite_class_set, suite_function_set
    # unittest.TextTestRunner(verbosity=1).run(suite)  # self.verbosity = 0  # 0, 1, 2.  unittest.TextTestResult
    return suite


if __name__ == '__main__':
    ImageRenameAppTests().test_default()
    ...
