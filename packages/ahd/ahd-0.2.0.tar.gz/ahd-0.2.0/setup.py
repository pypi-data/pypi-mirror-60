"""
Description:
    Contains all the configuration for the package on pip
"""
import setuptools

def get_content(*filename):
    """ Gets the content of a file and returns it as a string
    Args:
        filename(str): Name of file to pull content from
    Returns:
        str: Content from file
    """
    content = ""
    for file in filename:
        with open(file, "r") as full_description:
            content += full_description.read()
    return content

setuptools.setup(
    name = "ahd",
    version = "0.2.0",
    author = "Kieran Wood",
    author_email = "kieran@canadiancoding.ca",
    description = "Create ad-hoc commands to be dispatched in their own namespace.",
    long_description = get_content("README.md", "CHANGELOG.md"),
    long_description_content_type = "text/markdown",
    url = "https://github.com/Descent098/ahd",
    include_package_data = True,
    packages = setuptools.find_packages(),
    entry_points = { 
           'console_scripts': ['ahd = ahd.cli:main']
       },
    install_requires = [
    "docopt", # Used for argument parsing
      ],
    extras_require = {
        "dev" : ["nox",    # Used to run automated processes
                 "pytest", # Used to run the test code in the tests directory
                 "mkdocs"],# Used to create HTML versions of the markdown docs in the docs directory

    },
    classifiers = [
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)