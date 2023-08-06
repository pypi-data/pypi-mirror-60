import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="camper",
    version="1.0.1",
    author="David (Ming) Zeng",
    author_email="me@davidvfx.com",
    description="Pythonic utilities for Tweak RV",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/davinozen/camper",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    status='alpha',
    python_requires='>=3.6',
)
