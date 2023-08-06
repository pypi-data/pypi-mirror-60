from setuptools import setup, find_packages
import os
from os import path
from io import open

version = os.getenv("CI_COMMIT_TAG", os.getenv("CI_JOB_ID", "SNAPSHOT"))

# read the contents of your README file

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='banditsbook',  # Required
    version=version,
    description='Python code from the book Bandit Algorithms for Website Optimization',  # Optional
    long_description=long_description,  # Optional
    long_description_content_type='text/markdown',  # Optional (see note above)
    url='https://gitlab.com/winderresearch/rl/BanditsBook/',  # Optional
    author='Phil Winder',  # Optional
    author_email='phil@WinderResearch.com',  # Optional
    classifiers=[  # Optional
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='rl bandits abtesting',  # Optional
    packages=find_packages(where="python", exclude=["Package.egg_info", ]),
    package_dir={'': 'python'},
    python_requires='>=3.5',
    project_urls={  # Optional
        'Bug Reports': 'https://gitlab.com/winderresearch/rl/BanditsBook/issues',
        'Source': 'https://gitlab.com/winderresearch/rl/BanditsBook/',
    },
)
