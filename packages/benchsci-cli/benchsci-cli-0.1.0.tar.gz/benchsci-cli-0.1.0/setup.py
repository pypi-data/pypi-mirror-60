import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="benchsci-cli",
    version="0.1.0",
    author="Harsh Verma",
    author_email="harsh@benchsci.com",
    description="BenchSci CLI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/benchsci/benchsci-cli",
    packages=['src'],
    install_requires=['invoke'],
    entry_points={
        'console_scripts': ['bench = src:program.run']
    },
    python_requires='>=3.6',
)
