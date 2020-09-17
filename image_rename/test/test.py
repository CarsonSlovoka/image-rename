from unittest import TestCase

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
        cli_main()


if __name__ == '__main__':
    ImageRenameAppTests().test_default()
    ...
