import os
from setuptools import setup, find_packages
from setuptools.dist import Distribution

class BinaryDistribution(Distribution):
    def is_pure(self):
        return False

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

__version__ = 'v1.0'

setup(
    name='OpenaiBatchAPI',
    packages=find_packages(),
    version=__version__,
    author='IT.DAINB',
    author_email='it.dainb@gmail.com',
    description='OpenaiBatchAPI: A Python Library that support OpenAI Batch API',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords='openai batch_api batch api',
    url='https://github.com/it-dainb/batch_api.git',
	license='Apache License 2.0',
    classifiers=[
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    include_package_data=True,
    python_requires='>=3.8',
    install_requires = [
        'uuid',
        'orjsonl',
        'openai',
        'tempfile',
        'tqdm'
    ]
)
