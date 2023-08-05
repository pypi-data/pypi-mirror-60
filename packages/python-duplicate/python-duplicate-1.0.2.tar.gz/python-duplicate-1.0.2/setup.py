from setuptools import setup, find_packages

with open('PYPI_README.md') as file:
    long_description = file.read()

setup(
    name="python-duplicate",
    version="1.0.2",
    url="https://github.com/Clement-O/python-duplicate",
    license="MIT",
    author="Clément Omont--Agnes",
    author_email="omont.clement@gmail.com",
    description="Handle duplicate in python",
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(exclude=["*.test", "*.test.*", "test.*", "test"]),
    zip_safe=False,
    install_requires=["psycopg2-binary", "PyMySQL"],
    project_urls={
        "Documentation": "https://python-duplicate.readthedocs.io/en/latest/",
        "Source": "https://github.com/Clement-O/python-duplicate",
    },
)
