from setuptools import setup, find_packages
from os import path
from io import open

here = path.abspath(path.dirname(__file__))
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()


__author__ = "Dang Duc Ngoc"
__email__ = "ngoc.dang@f4.intek.edu.vn"
__version__ = "1.0.7"
__copyright__ = "Copyright (C) 2019, Intek Institute"
__credits__ = "Daniel CAUNE"
__license__ = "MIT"
__maintainer__ = "Dang Duc Ngoc"
__url__ = "https://github.com/Friendlyngoc/Friendlyngoc_spriteutil"
__description__ = "A Sprite dectection tool"


setup(
    extras_require={
        "dev": [
            "appdirs==1.4.3",
            "attrs==19.3.0",
            "black==19.10b0; python_version >= '3.6'",
            "cached-property==1.5.1",
            "cerberus==1.3.2",
            "certifi==2019.11.28",
            "chardet==3.0.4",
            "click==7.0",
            "colorama==0.4.3",
            "distlib==0.3.0",
            "first==2.0.2",
            "idna==2.8",
            "importlib-metadata==1.4.0; python_version < '3.8'",
            "more-itertools==8.1.0",
            "orderedmultidict==1.0.1",
            "packaging==19.2",
            "pathspec==0.7.0",
            "pep517==0.8.1",
            "pip-shims==0.4.0",
            "pipenv-setup==3.0.0",
            "pipfile==0.0.2",
            "plette[validation]==0.2.3",
            "pyparsing==2.4.6",
            "regex==2020.1.8",
            "requests==2.22.0",
            "requirementslib==1.5.3",
            "six==1.14.0",
            "toml==0.10.0",
            "tomlkit==0.5.8",
            "typed-ast==1.4.1",
            "typing==3.7.4.1",
            "urllib3==1.25.8",
            "vistir==0.5.0",
            "wheel==0.33.6",
            "zipp==2.0.1",
        ]
    },
    name="Spriteutils_Ngoc_Dang",
    version=__version__,
    description=__description__,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=__url__,
    author=__author__,
    author_email=__email__,
    license=__license__,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
    ],
    packages=find_packages(exclude=["contrib", "docs", "tests"]),
    python_requires=">=3.6",
    install_requires=[
        "bleach==3.1.0",
        "certifi==2019.11.28",
        "cffi==1.13.2",
        "chardet==3.0.4",
        "cryptography==2.8",
        "docutils==0.16",
        "idna==2.8",
        "importlib-metadata==1.4.0; python_version < '3.8'",
        "jeepney==0.4.2; sys_platform == 'linux'",
        "keyring==21.1.0",
        "more-itertools==8.1.0",
        "numpy==1.18.1",
        "pillow==7.0.0",
        "pkginfo==1.5.0.1",
        "pycparser==2.19",
        "pygments==2.5.2",
        "readme-renderer==24.0",
        "requests==2.22.0",
        "requests-toolbelt==0.9.1",
        "secretstorage==3.1.2; sys_platform == 'linux'",
        "six==1.14.0",
        "spriteutils-ngoc-dang==1.0.6",
        "tqdm==4.41.1",
        "twine==3.1.1",
        "urllib3==1.25.8",
        "webencodings==0.5.1",
        "wheel==0.33.6",
        "zipp==2.0.1",
    ],
    dependency_links=[],
    maintainer=__maintainer__,
)
