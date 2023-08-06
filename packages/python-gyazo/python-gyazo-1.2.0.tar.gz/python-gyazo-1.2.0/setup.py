from io import open  # For Python 2
from os import path

from setuptools import setup

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

with open(path.join(here, 'gyazo/__about__.py')) as f:
    exec(f.read())

package_data = {
    'gyazo': ['py.typed', '*.pyi'],
}

install_requires = [
    'python-dateutil>=2.4.2',
    'requests>=2.7.0',
]

extras_require = {
    ':python_version < "3.5"': [
        'typing',
    ],
    'docs': [
        'Sphinx>=1.7,<1.8',
        'sphinx_rtd_theme>=0.3.0,<0.4',
    ],
    'mypy:python_version >= "3.4"': [
        'mypy',
    ],
    'test': [
        'coverage>=4.3.4,<5.0.0',
        'coveralls>=1.1,<2.0',
        'flake8>=3.3.0,<4.0.0',
    ],
    'test:python_version < "3.3"': [
        'mock>=2.0.0,<3.0.0',
    ],
}

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Topic :: Internet',
]

setup(
    name='python-gyazo',
    version=__version__,
    description='A Python wrapper for Gyazo API',
    long_description=long_description,
    author='Yusuke Miyazaki',
    author_email='miyazaki.dev@gmail.com',
    url='https://github.com/ymyzk/python-gyazo',
    project_urls={
        'Bug Reports': 'https://github.com/ymyzk/python-gyazo/issues',
        'Source': 'https://github.com/ymyzk/python-gyazo',
    },
    license='MIT',
    packages=['gyazo'],
    package_data=package_data,
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, <4',
    install_requires=install_requires,
    extras_require=extras_require,
    classifiers=classifiers,
    keywords='gyazo',
)
