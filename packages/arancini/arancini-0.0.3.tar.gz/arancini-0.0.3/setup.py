import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
    name="arancini", # Replace with your own username
    version="0.0.3",
    author="Michael Edward Vinyard",
    author_email="vinyard@g.harvard.edu",
    description="scATAC-seq utils",
    long_description="This package contains various pre-processing and post-processing tools for scATAC-seq data",
    long_description_content_type="text/markdown",
    url="https://github.com/mvinyard/arancini",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    scripts=['arancini-scripts/arancini2'],
)
