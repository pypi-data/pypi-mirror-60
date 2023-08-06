import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pynidus",
    version="0.0.119",
    author="Keurcien Luu",
    author_email="keurcien@appchoose.io",
    description="A handful of utilities.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/appchoose/pynidus",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)