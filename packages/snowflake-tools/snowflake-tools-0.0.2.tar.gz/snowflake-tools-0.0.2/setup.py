import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="snowflake-tools",
    version="0.0.2",
    author="Jake Thomas",
    author_email="jake@bostata.com",
    description="A suite of tools for setting up and managing snowflake data warehouses.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://bostata.com/",
    packages=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
    ],
)
