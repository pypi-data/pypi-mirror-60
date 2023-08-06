from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="privat24-business-python-sdk",
    version="0.0.1",
    author="Anton Kuzmenko",
    author_email="antonlabsnet@gmail.com",
    description="Privat24 for Business Python SDK",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/antonlabs/privat24-business-python-sdk",
    project_urls={
        "Bug Tracker": "https://github.com/pandas-dev/pandas/issues",
        "Documentation": "https://pandas.pydata.org/pandas-docs/stable/",
        "Source Code": "https://github.com/pandas-dev/pandas",
    },
    packages=find_packages(),
    platforms="any",
    classifiers=[
        "Development Status :: 1 - Planning",
        "Environment :: Web Environment",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Scientific/Engineering",
    ],
    python_requires='>=3.6',
)
