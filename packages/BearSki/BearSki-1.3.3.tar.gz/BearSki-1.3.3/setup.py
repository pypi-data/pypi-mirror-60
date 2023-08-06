from setuptools import setup,find_packages
import src

setup (
    name =src.__title__,
    version = src.__version__,
    packages = find_packages('src'),  # 包含所有src中的包
    package_dir = {'':'src'},   # 告诉distutils包都在src下
    package_data = {
        # 任何包中含有.txt文件，都包含它
        '': ['*.txt'],
        # 包含demo包data文件夹中的 *.dat文件
        'BearSki': ['data/*.dat'],
    },
    description = src.__description__,
    author = src.__author__,
    url = src.__url__,
    license =src.__license__,
    # py_modules=['hello'],
    install_requires = ["requests","har2case"],
    entry_points = {
        'console_scripts': [
            'BearSki = runcmd:main'
        ]
    }
)