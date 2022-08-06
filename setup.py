from setuptools import setup, find_packages

VERSION = '1.0'

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='pyLegoMario',
    version=VERSION,
    author='Jamin Kauf, Bruno Hautzenberger',
    author_email='jamin.kauf@yahoo.de',
    description='Module for handling connections with the Lego Mario toy',
    long_description_content_type='text/markdown',
    long_description=long_description,
    packages=find_packages(),
    install_requires=['bleak', 'pathlib', 'asyncio', 'pillow', 'pygame'],
    keywords=['lego', 'python', 'super mario', 'lego mario', 'bluetooth'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Operating System :: Microsoft :: Windows',
        'License :: OSI Approved :: MIT License'
    ],
    python_requires='>=3.9',
    project_urls = {'repository': r'https://github.com/Jackomatrus/pyLegoMario'},
    include_package_data=True
)