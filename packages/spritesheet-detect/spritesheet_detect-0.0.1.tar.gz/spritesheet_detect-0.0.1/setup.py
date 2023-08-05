from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

__author__ = "Thu Hoai"
__copyright__ = "Copyright (C) 2019, Intek Institute"
__credits__ = ["Thu Hoai"]
__email__ = "hoai.le@f4.intek.edu.vn"
__license__ = "MIT"
__maintainer__ = "Thu Hoai"
__version__ = "0.0.1"


setup(
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
        "tqdm==4.41.1",
        "twine==3.1.1",
        "urllib3==1.25.7",
        "webencodings==0.5.1",
        "wheel==0.33.6",
        "zipp==2.0.0",
    ],
    author=__author__,
    author_email=__email__,
    description="SpriteSheet Detection package",
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    include_package_data=True,
    name="spritesheet_detect",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    version=__version__
)
