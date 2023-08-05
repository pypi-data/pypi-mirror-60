import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="aiobooru",
    version="0.1.0",
    author="Yui Yukihira",
    author_email="yuiyukihira1@gmail.com",
    description="A danbooru API helper using aiohttp",
    license="MIT",
    packages=find_packages(where='src'),
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    install_requires=["aiohttp>=3.5.4"],
    extras_require={"aiofiles": ["aiofiles"]},
    package_dir={"":"src"},
    python_requires='>=3.7.0',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    url='https://github.com/YuiYukihira/aiobooru'
)