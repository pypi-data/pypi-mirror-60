import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="magic_sisters_932", # Replace with your own username
    version="0.0.1",
    author="Yuani Chen",
    author_email="yuanic12@gmail.com",
    description="Specially created package for Magic Sisters",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
)