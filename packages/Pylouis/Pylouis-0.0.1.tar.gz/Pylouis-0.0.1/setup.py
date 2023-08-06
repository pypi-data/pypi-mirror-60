import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Pylouis", # Replace with your own username
    version="0.0.1",
    author="Popovici Catalin",
    author_email="cp@baum.ro",
    description="liblouis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://https://github.com/liblouis/liblouis",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
