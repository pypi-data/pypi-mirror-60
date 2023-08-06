import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="TopLoader", # Replace with your own username
    version="0.0.1",
    author="Emmett Boudreau",
    author_email="emmettgb@gmail.com",
    description="Load Julia Modules -- The Easy way!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/emmettgb/TopLoader",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
