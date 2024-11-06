from setuptools import setup, find_packages

# Read the long description from the README.md file
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

# Define the package version
__version__ = '1.0.1'

# Setup function for your package
setup(
    name='openai_batch_api',
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
    python_requires='>=3.8, <=3.12',
    install_requires=[
        'uuid',
        'orjsonl',
        'openai',
        'tqdm',
    ]
)
