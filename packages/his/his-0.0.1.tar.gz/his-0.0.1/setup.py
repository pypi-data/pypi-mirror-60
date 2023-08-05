import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="his",
    version="0.0.1",
    author="Utree",
    author_email="Utree@example.com",
    description="Utree package",
    long_description_content_type="text/markdown",
    long_description=long_description,
    url="https://github.com/Utree/his",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
