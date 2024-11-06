import sys
import platform
from setuptools import setup, find_packages

# Read the README.md for long description
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

# Define the version
__version__ = 'v1.0'

# Define the setup configuration
setup(
    name='OpenaiBatchAPI',
    packages=find_packages(),
    version=__version__,
    author='IT.DAINB',
    author_email='it.dainb@gmail.com',
    description='OpenaiBatchAPI: A Python Library that supports OpenAI Batch API',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords='openai batch_api batch api',
    url='https://github.com/it-dainb/batch_api.git',
    license='Apache License 2.0',
    classifiers=[
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    include_package_data=True,
    python_requires='>=3.8',
    install_requires=[
        'uuid',
        'orjsonl',
        'openai',
        'tempfile',
        'tqdm'
    ],
    # This will help include platform-specific options for wheels
    options={
        'bdist_wheel': {
            'universal': True,  # Build a universal wheel, when possible
        },
    },
    # Optional: specify any extra requirements based on platform
    extras_require={
        'dev': ['pytest', 'tox'],
        'linux': ['libssl-dev'],  # Example for platform-specific dependencies
        'windows': ['pywin32'],
    },
)
