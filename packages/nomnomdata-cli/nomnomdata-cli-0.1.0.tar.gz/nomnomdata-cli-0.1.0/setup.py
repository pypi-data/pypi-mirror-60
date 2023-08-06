import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="nomnomdata-cli",
    version="0.1.0",
    author="Nom Nom Data",
    author_email="info@nomnomdata.com",
    description="Core package for the nomnomdata cli suite",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/nomnomdata/tools/nomnomdata-cli",
    packages=setuptools.find_namespace_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Environment :: Console",
        "Intended Audience :: Developers",
    ],
    install_requires=[
        "pytest>=4.3.0",
        "click-plugins>=1.0.4",
        "click>=7.0",
        "coloredlogs>=4.12.1",
    ],
    entry_points={"console_scripts": ["nnd=nomnomdata.cli.cli:cli"]},
    python_requires=">=3.7",
    zip_safe=False,
)
