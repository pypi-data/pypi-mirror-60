import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="xtractr", # Replace with your own username
    version="0.0.1",
    author="Noah Caldwell-Gatsos",
    author_email="ncg17developer@gmail.com",
    description="A mechanism to improve extraction",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ncaldwell17/xTractr",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
