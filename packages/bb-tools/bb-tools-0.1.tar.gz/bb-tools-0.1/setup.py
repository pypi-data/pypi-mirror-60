import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='bb-tools',  
    version='0.1',
    # scripts=['bb-tools'] ,
    author="Roman Borysenko",
    author_email="lngphp@gmail.com",
    description="Bitbucket tools package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://roman_newaza@bitbucket.org/roman_newaza/bb-tools.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
 )
