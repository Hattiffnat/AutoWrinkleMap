"""Debug script"""

import os
import shutil
import subprocess

PACKAGE_NAME = 'auto_wrinkle_map'
ADDONS_FOLDER = os.path.expanduser(r'~/.config/blender/4.4/extensions/user_default')
ADDON_FOLDER = os.path.join(ADDONS_FOLDER, PACKAGE_NAME)

TEST_FILE = r'blend/wrinkle_test.blend'


def main():
    shutil.rmtree(ADDON_FOLDER, ignore_errors=True)
    shutil.copytree(PACKAGE_NAME, ADDON_FOLDER)

    subprocess.call(['/usr/bin/blender', f'{TEST_FILE}', '--addons', PACKAGE_NAME])


if __name__ == '__main__':
    main()
