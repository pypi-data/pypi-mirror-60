import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="json-section",
    version="1.1",
    author="Carlos Armando",
    author_email="contato.carmando@gmail.com",
    description="Tool used to return sections of JSON documents",
    url="https://github.com/InfeCtlll3/json-section",
    packages=["section"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    keywords="json section cli",
    python_requires=">=3.6",
    entry_points='''
        [console_scripts]
        section=section.section:query
    '''
)
