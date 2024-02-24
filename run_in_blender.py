"""Скрипт для дебага"""

import subprocess
import shutil
import os


PACKAGE_NAME = 'auto_wrinkle_map'
ADDONS_FOLDER = os.path.expanduser(r'~/.config/blender/4.0/scripts/addons')
ADDON_FOLDER = os.path.join(ADDONS_FOLDER, PACKAGE_NAME)

TEST_FILE = r'test/Unity Slava wrinkle test.blend'


def main():
    shutil.rmtree(ADDON_FOLDER, ignore_errors=True)

    shutil.copytree(PACKAGE_NAME, ADDON_FOLDER)

    subprocess.call([
        '/usr/bin/blender', f'{TEST_FILE}',
        '--addons', PACKAGE_NAME
    ])


if __name__ == "__main__":
    main()
    