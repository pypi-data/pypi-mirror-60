from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

__author__ = "Le Cuong"
__copyright__ = "Copyright (C) 2019, Intek Institute"
__email__ = "cuong.le@f4.intek.edu.vn"
__license__ = "MIT"
__name__ = "spritesheet_lecuong91"
__version__ = "0.0.2"
__github__ = "https://github.com/intek-training-jsc/sprite-sheet-cuongle91/"

setup(
    install_requires=["setuptools", "wheel", "twine", "numpy", "pillow"],
    name=__name__,
    version=__version__,
    author=__author__,
    author_email=__email__,
    description="Sprite detect",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=__github__,
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
