import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="shrek-aio-tegraze", 
    version="0.1.0",
    author="Tegraze",
    author_email=" ",
    description="All-in-one script with flooding attacks for IDS testing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tegraze/Shrek-AIO-Flooder",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
