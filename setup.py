from setuptools import setup, find_packages

VERSION = '0.9'

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='pyLegoMario',
    version=VERSION,
    author='Jamin Kauf, Bruno Hautzenberger',
    author_email='jamin.kauf@yahoo.de',
    description='Module for handling connections with the Lego Mario toy',
    packages=find_packages(),
    install_requires=['bleak', 'pathlib', 'asyncio', 'pillow'],
    keywords=['lego', 'python', 'super mario', 'lego mario', 'bluetooth'],
    classifiers=[
        'Development Status :: Done',
        'Intended Audience :: Programmers',
        'Programming Language :: Python :: 3',
        'Operating System :: Microsoft :: Windows',
        'License :: MIT License'
    ],
    python_requires='>=3.9',
    project_urls = {'repository': r'https://github.com/Jackomatrus/pyLegoMario'},
    include_package_data=True
)