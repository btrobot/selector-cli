"""
Setup script for Selector CLI
"""
from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='selector-cli',
    version='1.0.6',
    author='Selector CLI Team',
    author_email='selector-cli@example.com',
    maintainer='Selector CLI Team',
    description='Interactive web element selection and code generation tool',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/selector-cli/selector-cli',
    download_url='https://github.com/selector-cli/selector-cli/archive/v1.0.0.tar.gz',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'Topic :: Software Development :: Code Generators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
    install_requires=[
        'playwright>=1.40.0',
        'rich>=13.0.0',
        'PyYAML>=6.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-asyncio>=0.21.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'selector=selector_cli.main:main',
        ],
    },
    include_package_data=True,
    keywords='web automation, testing, code generation, playwright, selenium, puppeteer',
    project_urls={
        'Bug Reports': 'https://github.com/selector-cli/selector-cli/issues',
        'Source': 'https://github.com/selector-cli/selector-cli',
        'Documentation': 'https://github.com/selector-cli/selector-cli/blob/main/USER_MANUAL.md',
    },
)
