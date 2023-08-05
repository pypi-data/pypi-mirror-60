from setuptools import setup
from setuptools.command.install import install as _install
import os


def readme():
    with open('README.md') as f:
        README = f.read()
    return README


# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name="get_summary",
    version="0.0.0.3",
    description="A Python package which will helps you to get summary report of any webpage content or summary of paragraphs",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/Vijayraj72/get-summary",
    author="vijay saw",
    author_email="imvijayraj72@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],

    packages=['get_summary'],
    include_package_data=True,
    install_requires=["nltk"],
    
    keywords=['summary', 'content summary', 'website summary',
              'get summary', 'article summary', 'get article summary'],
)
