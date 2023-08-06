import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ebukafy", # Replace with your own username
    version="0.0.2",
    author="maticstric",
    author_email="maticjecar@gmail.com",
    description="Turn a text file into an epub chapter",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/maticstric/ebukafy",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
