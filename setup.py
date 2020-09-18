import setuptools
from setuptools import setup, find_packages, find_namespace_packages
from setuptools.command.test import test as test_class
from pathlib import Path

if 'env path':
    import image_rename
    from image_rename import __version__, __description__
    from image_rename.test.test import test_setup

VERSION_NUMBER = __version__
DOWNLOAD_VERSION = __version__
PACKAGES_DIR = image_rename.__name__
SETUP_NAME = PACKAGES_DIR.replace('_', '-')
GITHUB_URL = f'https://github.com/CarsonSlovoka/{SETUP_NAME}'
GITHUB_BRANCH = f'https://github.com/CarsonSlovoka/{SETUP_NAME}/tree/master'

# Store original `find_package_modules` function
find_package_modules = setuptools.command.build_py.build_py.find_package_modules


def custom_find_package_modules(self, package, package_dir):
    all_info_list = find_package_modules(self, package, package_dir)

    accepted_info_list = []

    for pkg_full_name, module_bare_name, module_path in all_info_list:
        next_flag = False
        for exclude_file in ('test_entry.py', 'test.old.py',):
            if exclude_file in module_path:
                next_flag = True
                break
        if next_flag:
            continue
        accepted_info_list.append((pkg_full_name, module_bare_name, module_path))
    return accepted_info_list


# Replace original `find_package_modules` function with the custom one.
setuptools.command.build_py.build_py.find_package_modules = custom_find_package_modules

LONG_DESCRIPTION = ""
with open('README.rst', encoding='utf-8') as f:
    # https://pepy.tech can't be attached.
    for begin_idx, line in enumerate(f):
        if line.strip().startswith('===='):
            break
    f.seek(0)
    LONG_DESCRIPTION = ''.join([line if line.strip() != '.. uml::' else line.replace('..', '...')  # PyPI does not support uml
                                for idx, line in enumerate(f) if idx >= begin_idx])

with open('requirements.txt') as req_txt:
    LIST_REQUIRES = [line.strip() for line in req_txt if not line.startswith('#') and line.strip() != '']

setup(
    name=SETUP_NAME,
    version=VERSION_NUMBER,  # x.x.x.{dev, a, b, rc}

    packages=find_packages(exclude=['*.test_cases']),
    package_data={f'{PACKAGES_DIR}.test': ['image/*.*', ],
                  f'{PACKAGES_DIR}': ['asset/icon/*.*', ]},
    include_package_data=True,
    license="BSD 3-Clause",

    author='Carson',
    author_email='jackparadise520a@gmail.com',

    install_requires=LIST_REQUIRES,

    url=GITHUB_BRANCH,

    description=__description__,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/x-rst',
    keywords=['opencv', ],

    python_requires='>=3.6.2,',

    zip_safe=True,
    classifiers=[  # https://pypi.org/classifiers/
        'Development Status :: 3 - Alpha',

        'License :: OSI Approved',

        'Natural Language :: Chinese (Traditional)',
        'Natural Language :: English',

        'Operating System :: Microsoft',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Operating System :: MacOS',

        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',

        'Topic :: Desktop Environment :: File Managers',
        'Topic :: System :: Filesystems'
    ],

    project_urls={
        'Homepage': GITHUB_BRANCH,
        'Documentation': f'https://carsonslovoka.github.io/{SETUP_NAME}/en/index.html',
        'Code': GITHUB_BRANCH,
        'Issue Tracker': f'{GITHUB_URL}/issues',
        'Download': GITHUB_BRANCH,
    },

    entry_points={
        'console_scripts': [
            f'img_rename={PACKAGES_DIR}.cli:main',
        ],
    },
    test_suite='setup.test_setup',  # `python setup.py test` will call this function. # return value must is `suite`
)
