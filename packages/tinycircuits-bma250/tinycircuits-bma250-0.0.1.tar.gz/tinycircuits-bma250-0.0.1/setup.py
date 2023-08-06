import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tinycircuits-bma250", 
    version="0.0.1",
    author="TinyCircuits",
    author_email="info@tinycircuits.com",
    description="Wireling Accelerometer Sensor Python library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TinyCircuits/TinyCircuits-Wireling-Accelerometer-Python-AST1001",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)