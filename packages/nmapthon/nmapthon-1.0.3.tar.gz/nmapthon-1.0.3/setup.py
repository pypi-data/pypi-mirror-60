import setuptools

with open("../README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="nmapthon", # Replace with your own username
    version="1.0.3",
    author="cblopez",
    author_email="noeroiff@protonmail.com",
    description="A simple, high level Nmap library for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cblopez/nmapthon",
    py_modules="nmapthon",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: System :: Networking",
        "Topic :: Security",
        "License :: OSI Approved :: MIT License"
    ]
)
