# -*- coding: utf-8 -*-
"""
 __author__:  @haopeng_dong
 __datetime__:  2020/1/23
"""
import io
import re

from setuptools import setup, find_packages

with io.open("README.rst", "rt", encoding="utf8") as f:
    readme = f.read()

with io.open("src/rflask/__init__.py", "rt", encoding="utf8") as f:
    version = re.search(r'__version__ = "(.*?)"', f.read()).group(1)

setup(
    name="rflask",
    version=version,
    packages=find_packages("src"),
    package_dir={"": "src"},
    include_package_data=True,
    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires=[
        "Click>=5.1",
    ],
    extras_require={
        "dotenv": ["python-dotenv"],
        "dev": [
            "pytest",
            "coverage",
            "tox",
            "sphinx",
            "pallets-sphinx-themes",
            "sphinxcontrib-log-cabinet",
            "sphinx-issues",
        ],
        "docs": [
            "sphinx",
            "pallets-sphinx-themes",
            "sphinxcontrib-log-cabinet",
            "sphinx-issues",
        ],
    },
    entry_points='''
        [console_scripts]
        rflask=rflask.commands:rflask
    ''',

    package_data={
        # If any package contains *.txt or *.rst files, include them:
        "": ["*.md", "*.py"],
        # And include any *.msg files found in the "hello" package, too:
        "src": ["*.py"],
    },
    # metadata to display on PyPI
    author="Deacone",
    author_email="1173619682@qq.com.com",
    description="This is a tools for init flask restful api project, this can save your time.",
    keywords="flask restful api init",
    # project home page
    url="https://github.com/Deacone/init-flask-restful-api",
    project_urls={
        "Documentation": "https://github.com/Deacone/init-flask-restful-api",
        "Source Code": "https://github.com/Deacone/init-flask-restful-api",
        "Issue tracker": "https://github.com/Deacone/init-flask-restful-api/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "License :: OSI Approved :: MIT License",

    ],

    # could also include long_description, download_url, etc.
    long_description=readme,
    long_description_content_type='text/x-rst'
)
