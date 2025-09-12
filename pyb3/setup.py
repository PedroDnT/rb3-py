from setuptools import setup, find_packages

setup(
    name="pyb3",
    version="0.1.0",
    author="Wilson Freitas, Marcelo Perlin",
    author_email="wilson.freitas@gmail.com, marceloperlin@gmail.com",
    description="Download and parse public data released by B3 Exchange",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ropensci/pyb3",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "pandas",
        "numpy",
        "requests",
        "pyyaml",
        "pyarrow",
        "beautifulsoup4",
        "lxml",
        "python-dateutil",
        "pytz",
        "tqdm",
        "sqlalchemy",    # For database connections
    ],
    include_package_data=True,
    package_data={
        "pyb3": ["templates/*.yaml", "data/*.json"],
    },
)