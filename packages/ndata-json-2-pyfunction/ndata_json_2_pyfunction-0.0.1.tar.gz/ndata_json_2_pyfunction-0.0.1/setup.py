import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ndata_json_2_pyfunction", 
    version="0.0.1",
    author="Kapil Rajput",
    author_email="kapilrajput22@gmail.com",
    description="json to pyfunction",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kapilrajput22/prediction_model",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
