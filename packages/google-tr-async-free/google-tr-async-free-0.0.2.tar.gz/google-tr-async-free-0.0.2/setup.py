r'''
"google translate async based on token and httpx"
'''
# pylint: disable=invalid-name
from pathlib import Path
import re

from setuptools import setup, find_packages  # type: ignore

name = """google-tr-async-free"""
# description = ' '.join(name.split('-'))
description = 'google trnaslate async for free'
dir_name, = find_packages()

version, = re.findall(r"\n__version__\W*=\W*'([^']+)'", open('%s/__init__.py' % dir_name).read())

README_rst = '%s/README.md' % Path(__file__).parent
long_description = open(README_rst, encoding='utf-8').read() if Path(README_rst).exists() else ''

install_requires = ['httpx', 'js2py', 'loguru', ]
# 'diskcache', 'janus', 'pytest']

setup(
    name=name,
    packages=find_packages(),
    version=version,
    description=description,
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords=['machine translation', 'free', 'scraping', ],
    author="mikeee",
    url='http://github.com/ffreemt/%s' % name,
    download_url='https://github.com/ffreemt/google-tr-free/archive/v_%s.tar.gz' % version,
    install_requires=install_requires,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: MIT License',
    ],
    license='MIT License',
)
