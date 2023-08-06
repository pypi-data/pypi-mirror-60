import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tinycircuits-a1454", 
    version="0.0.2",
    author="TinyCircuits",
    author_email="info@tinycircuits.com",
    description="Wireling Analog Hall Effect Sensor Python library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TinyCircuits/TinyCircuits-Wireling-Hall-Effect-Python-AST1006",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)