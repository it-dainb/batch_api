import os, sys
from setuptools import setup, find_packages
from setuptools.command.bdist_wheel import bdist_wheel

class CustomBDistWheel(bdist_wheel):
    def finalize_options(self):
        # Calling the base class method to preserve other options
        super().finalize_options()

        # Fetch the Python version and OS type dynamically
        python_version = sys.version_info
        platform = sys.platform  # platform type (e.g., 'linux', 'darwin', 'win32')

        # Determine the correct wheel tag
        wheel_tag = f"cp{python_version.major}{python_version.minor}"

        if platform == "win32" or platform == "cygwin":
            self.dist_dir = os.path.join(self.build_temp, f"{wheel_tag}-win_amd64")
        elif platform == "darwin":
            self.dist_dir = os.path.join(self.build_temp, f"{wheel_tag}-macos")
        elif platform == "linux" or platform == "linux2":
            self.dist_dir = os.path.join(self.build_temp, f"{wheel_tag}-manylinux_2_28_x86_64")
        else:
            self.dist_dir = os.path.join(self.build_temp, f"{wheel_tag}-unknown")

        # Set the final wheel file name dynamically
        self.distribution.metadata.version = f"{self.distribution.metadata.version}-{wheel_tag}"


# Read the long description from the README.md file
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

# Define the package version
__version__ = '1.0'

# Setup function for your package
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
    python_requires='>=3.8, <=3.12',
    install_requires=[
        'uuid',
        'orjsonl',
        'openai',
        'tempfile',
        'tqdm',
        'wheel',  # Ensure the wheel package is installed
    ],
    cmdclass={
        'bdist_wheel': CustomBDistWheel,
    },
)
