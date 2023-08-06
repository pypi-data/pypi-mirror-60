from distutils.core import setup
from pathlib import Path

from setuptools import find_packages

this_file = Path(__file__).resolve()
readme = this_file.parent / 'README.md'

setup(
    name='autorec',
    version='0.0.1',
    description='AutoRec for automated recommendation',
    package_data={'': ['README.md']},
    long_description=readme.read_text(encoding='utf-8'),
    long_description_content_type='text/markdown',
    author='Data Analytics at Texas A&M (DATA) Lab, AutoRec Team',
    author_email='thwang1231@tamu.edu',
    url='https://github.com/thwang1231/autorec',
    download_url='',
    keywords=['Automated Machine Learning', 'Recommender System'],
    # TODO: Do not install tensorflow if tensorflow-gpu is installed.
    install_requires=[
        'packaging',
        'keras-tuner>=1.0.1',
        'scikit-learn',
        'numpy',
        'pandas',
    ],
    extras_require={
        'tests': ['pytest>=4.4.0',
                  'flake8',
                  'isort',
                  'pytest-xdist',
                  'pytest-cov',
                  'coverage'
                  ],
    },
    packages=find_packages(exclude=('tests',)),
)
