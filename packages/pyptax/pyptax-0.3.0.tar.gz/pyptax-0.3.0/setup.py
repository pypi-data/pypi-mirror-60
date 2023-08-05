import ast
import re

import setuptools

_version_re = re.compile(r"__version__\s+=\s+(.*)")

with open("pyptax/__init__.py", encoding="utf8") as f:
    version = ast.literal_eval(_version_re.search(f.read()).group(1))

with open("README.md", "r", encoding="utf8") as f:
    long_description = f.read()

documentation_deps = [
    "sphinx",
    "sphinx_rtd_theme",
]

testing_deps = [
    "pytest",
    "pytest-cov",
    "responses",
]

setuptools.setup(
    name="pyptax",
    version=version,
    description="A Python library to retrieve information on Ptax rates",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="ptax",
    author="Bruno Cardoso",
    author_email="cardosobrunob@gmail.com",
    url="https://github.com/brunobcardoso/pyptax",
    license="MIT",
    packages=["pyptax"],
    install_requires=["requests >= 2.0"],
    extras_require={
        "docs": documentation_deps,
        "testing": testing_deps,
        "dev": documentation_deps + testing_deps,
    },
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business :: Financial",
    ],
)
