# ahd; Ad-Hoc Dispatcher

*Create ad-hoc commands to be dispatched within their own namespace.*



## Quick-start

### Installation

#### From Pypi

Run ```pip install ahd``` or ```sudo pip3 install ahd```



#### From source

1. Clone this repo: (https://github.com/Descent098/ahd)
2. Run ```pip install .``` or ```sudo pip3 install .```in the root directory



### Usage

```bash
Usage: 

    ahd [-h] [-v] [-d]

    ahd register <name> [<command>] [<paths>]

    ahd <name> [<command>] [<paths>]



Options:

-h, --help        show this help message and exit

-v, --version     show program's version number and exit

-l, --log         If present will output logs to sys.stdout

-d, --doc         If present will open up the ahd docs
```



#### Example

Here is a quick example of creating a command that runs ```sudo apt-get update && sudo apt-get upgrade```:

1. Register the command as the name "update": ```ahd register update "sudo apt-get update && sudo apt-get upgrade"```
2. Run the command using the name "update": ```ahd update```



This example was somewhat trivial but keep in mind this effectively means you can replace any short bash scripts you are using to do things like updating multiple git repos, executing a sequence of commands to sort your downloads folder etc.



#### Arguments

##### Register

The register command allows you to register a name to be used later on. For example if I wanted to create a command that dispatched running git pull in several of my directories that is activated when I type ```ahd git-upt``` then I can just run ```ahd register git-upt "git pull" "~/path/to/project, ~/path/to/project-2, ~/path/to/project-3```



##### \<name\>

This is a placeholder value for the name of a command you have registered. Once the command is registered you can run it by using ```ahd <name>```, additionally you can override the default set commands or paths, details can be found at [https://ahd.readthedocs.io/usage#overriding](https://ahd.readthedocs.io/usage#overriding).





## Additional Documentation

Additional user documentation will be available at [https://ahd.readthedocs.io](https://ahd.readthedocs.io).



## Development-Contribution guide



### Installing development dependencies

There are a few dependencies you will need to begin development, you can install them by using ```pip install adh[dev]``` or just install them manually:

```
nox   	# Used to run automated processes
pytest 	# Used to run the test code in the tests directory
mkdocs	# Used to create HTML versions of the markdown docs in the docs directory
```

Just go through and run ```pip install <name>``` or ```sudo pip3 install <name>```. These dependencies will help you to automate documentation creation, testing, and build + distribution (through PyPi) automation.



### Folder Structure

*A Brief explanation of how the project is set up for people trying to get into developing for it*



#### /ahd

*Contains all the first party modules used in ahd*



#### /docs

*Contains markdown source files to be used with [mkdocs](https://www.mkdocs.org/) to create html/pdf documentation.* 



#### /tests

*Contains tests to be run before release* 



#### Root Directory

**setup.py**: Contains all the configuration for installing the package via pip.



**LICENSE**: This file contains the licensing information about the project.



**CHANGELOG.md**: Used to create a changelog of features you add, bugs you fix etc. as you release.



**mkdocs.yml**: Used to specify how to build documentation from the source markdown files.



**noxfile.py**: Used to configure various automated processes using [nox](https://nox.readthedocs.io/en/stable/), these include;

- Building release distributions
- Releasing distributions on PyPi
- Running test suite agains a number of python versions (3.5-current)

If anything to do with deployment or releases is failing, this is likely the suspect.



There are 4 main sessions built into the noxfile and they can be run using ```nox -s <session name>``` i.e. ```nox -s test```:

- build: Creates a source distribution, builds the markdown docs to html, and creates a universal wheel distribution for PyPi.
- release: First runs the build session, then asks you to confirm all the pre-release steps have been completed, then runs *twine* to upload to PyPi
- test: Runs the tests specified in /tests using pytest, and runs it on python versions 3.5-3.8 (assuming they are installed)
- docs: Serves the docs on a local http server so you can validate they have the content you want without having to fully build them.



**.gitignore**: A preconfigured gitignore file (info on .gitignore files can be found here: https://www.atlassian.com/git/tutorials/saving-changes/gitignore)







