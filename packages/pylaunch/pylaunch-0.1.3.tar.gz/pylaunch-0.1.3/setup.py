from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='pylaunch',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=[''],
    package_dir={'':'pylaunch'},
    version='0.1.3',
    url='https://github.com/Sandersland/pylaunch',
    author="Steffen Andersland",
    author_email='stefandersland@gmail.com',
    keywords=['dial'],
    install_requires=['requests'],
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows :: Windows 10"
    ],
    extras_require = {
        "dev": [
            "nose==1.3.7",
            "twine==3.1.1"
        ]
    }
)