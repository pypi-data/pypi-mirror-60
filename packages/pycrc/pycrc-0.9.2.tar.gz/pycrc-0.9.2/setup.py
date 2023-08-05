import setuptools
from pycrc import progname, version, url


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(name = 'pycrc',
        version = version,
        author = 'Thomas Pircher',
        author_email = 'tehpeh-web@tty1.net',
        description = 'Free, easy to use Cyclic Redundancy Check source code generator for C/C++',
        long_description = long_description,
        long_description_content_type="text/markdown",
        url = url,
        packages = ['pycrc'],
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
            ],
        python_requires='>=3.4',
        )
