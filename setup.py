from setuptools import setup, find_packages


version = {}
with open("./regonapi/version.py", "r") as fp:
    exec(fp.read(), version)

with open("README.rst", "r") as fh:
    long_description = fh.read()


setup(
    name="regonapi",
    version=version["__version__"],
    author="Zbigniew Heintze",
    author_email="zheintze@gmail.com",
    description="GUS REGON API Client",
    long_description=long_description,
    url="https://github.com/bigzbig/regonapi",
    packages=find_packages(),
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    setup_requires=[
        "pytest-runner",
        "flake8",
        "mypy",
    ],
    install_requires=[
        "zeep>=3.2.0",
        "lxml>=4.4.1",
    ],
    tests_require=[
        "pytest>=5.2.1",
    ]
)
