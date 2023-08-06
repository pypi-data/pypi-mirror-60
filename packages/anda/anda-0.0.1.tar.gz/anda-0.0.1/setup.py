import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="anda", # Replace with your own username
    version="0.0.1",
    author="Vojtech Kase",
    author_email="vojtech.kase@gmail.com",
    description="A package collecting various functions to work with ancient Mediterranean datasets (textual, spatial, etc.)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sdam-au/anda",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
