import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ez-cli",
    version="0.3.0",
    author="Harsh Verma",
    author_email="harsh376@gmail.com",
    description="A small cli",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/harsh376/ez-cli",
    packages=['ez_cli'],
    install_requires=['invoke'],
    entry_points={
        'console_scripts': ['ezpz = ez_cli:program.run']
    },
    python_requires='>=3.7',
)
