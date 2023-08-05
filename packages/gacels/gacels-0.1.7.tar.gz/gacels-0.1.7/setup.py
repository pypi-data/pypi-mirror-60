# pylint: skip-file
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gacels", # Replace with your own username
    version="0.1.7",
    author="Arnt Erik Stene",
    author_email="steneae@gmail.com",
    description="Package containing reusable tools for different applications.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/equinor/gacels",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'numpy==1.17.*',
        'seaborn==0.9.*',
        'matplotlib==3.1.*',
        'pandas==0.25.*',
        'azure-keyvault-secrets==4.0.*',
        'azure.identity==1.2.*',
        'azure-cli-core==2.0.*',
        'azure.mgmt.compute==10.0.*',
        'missingno==0.4.*']
)
