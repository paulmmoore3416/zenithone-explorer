"""
ZenithOne Explorer CLI - Setup Configuration

Installation script for the ZenithOne Explorer command-line interface.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = ""
if readme_file.exists():
    long_description = readme_file.read_text(encoding='utf-8')

setup(
    name='zenithone-cli',
    version='1.0.0',
    description='Command-line interface for ZenithOne Explorer - Enterprise LinuxONE Management Platform',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Paul Moore',
    author_email='paulmmoore3416@gmail.com',
    url='https://github.com/paulmmoore3416/zenithone-explorer',
    license='MIT',
    
    packages=find_packages(),
    include_package_data=True,
    
    python_requires='>=3.10',
    
    install_requires=[
        'requests>=2.31.0',
        'pyyaml>=6.0',
        'click>=8.1.0',
    ],
    
    extras_require={
        'dev': [
            'pytest>=7.4.0',
            'pytest-cov>=4.1.0',
            'black>=23.7.0',
            'flake8>=6.1.0',
            'mypy>=1.5.0',
        ],
    },
    
    entry_points={
        'console_scripts': [
            'zenith=cli.main:main',
            'zenithone=cli.main:main',
        ],
    },
    
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3.14',
        'Topic :: System :: Systems Administration',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    
    keywords='linuxone ibm mainframe zos cli management containers workloads',
    
    project_urls={
        'Bug Reports': 'https://github.com/paulmmoore3416/zenithone-explorer/issues',
        'Source': 'https://github.com/paulmmoore3416/zenithone-explorer',
        'Documentation': 'https://github.com/paulmmoore3416/zenithone-explorer/tree/main/docs',
    },
)
