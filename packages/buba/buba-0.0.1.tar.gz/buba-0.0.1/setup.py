"""
Publish a new version:
$ git tag X.Y.Z -m "Release X.Y.Z"
$ git push --tags
$ pip install --upgrade twine wheel
$ python setup.py sdist bdist_wheel --universal
$ twine upload dist/*
"""

import codecs
import setuptools

BUBA_VERSION = '0.0.1'
BUBA_DOWNLOAD_URL = (
        'https://github.com/code-impactor/buba/releases/tag/' + BUBA_VERSION
)


def read_file(filename):
    """
    Read a utf8 encoded text file and return its contents.
    """
    with codecs.open(filename, 'r', 'utf8') as f:
        return f.read()


setuptools.setup(
    name='buba',
    packages=['buba'],
    version=BUBA_VERSION,
    description="Multi-environment yaml settings following 12 Factor App methodology.",
    long_description=read_file('README.md'),
    long_description_content_type="text/markdown",
    license='MIT',
    author="Andrei Roskach",
    author_email="code.impactor@gmail.com",
    url="https://github.com/code-impactor/buba",
    download_url=BUBA_DOWNLOAD_URL,
    keywords=[
        'multi-environment', 'yaml', 'settings', 'config', '12 Factor', 'python', 'nested'
    ],
    install_requires=['PyYAML >= 5.3'],
    platforms=['Any'],
    classifiers=[
        'Intended Audience :: Developers',
        "Programming Language :: Python",
        'Natural Language :: English',
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Topic :: Software Development :: Libraries',
    ],
    python_requires='>=2.7'
)
