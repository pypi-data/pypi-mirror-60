import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="datahen-helpers",
    version="0.2",
    author="Datahen",
    author_email="services@datahen.com",
    description="Datahen package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://datahen.com",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
      'datahen',
      'pandas',
      'requests',
      'tqdm'
    ],
    python_requires='>=3.6',
)