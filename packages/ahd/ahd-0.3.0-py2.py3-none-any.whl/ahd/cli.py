"""This file houses the primary entrypoint, and main business logic of ahd.

Module Variables
----------------

usage (str);
    Used by docopt to setup argument parsing;
    Defines the actual command line interface.

CONFIG_FILE_PATH(str):
    The path to the configuration file.

CURRENT_PATH(str):
    Used to keep track of users current directory
    to cd back into it after script execution.


Documentation
-------------
Docs website: https://ahd.readthedocs.io
"""

# Standard lib dependencies
import os                             # Used primarily to validate paths
import sys                            # Used to check length of input arguments
import glob                           # Used to preprocess wildcard paths
import logging                        # Used to log valueable logging info
import webbrowser                     # Used to auto-launch the documentation link
import subprocess                     # Used to run the dispatched commands
from configparser import ConfigParser # Used to serialize and de-serialize config files


# Internal dependencies
from .autocomplete import command, generate_bash_autocomplete

# Third-party dependencies
import colored                        # Used to colour terminal output
from docopt import docopt             # Used to parse arguments and setup POSIX compliant usage info


usage = """Add-hoc dispatcher
    Create ad-hoc commands to be dispatched within their own namespace.

    Usage: 
        ahd [-h] [-v] [-d]
        ahd docs [-a] [-o]
        ahd config [-e] [-i CONFIG_FILE_PATH]
        ahd register <name> [<command>] [<paths>]
        ahd <name> [<command>] [<paths>]

    Options:
    -h, --help            show this help message and exit
    -v, --version         show program's version number and exit
    -a, --api             shows the local API docs
    -o, --offline         shows the local User docs instead of live ones
    -e, --export          exports the configuration file
    -i CONFIG_FILE_PATH, --import CONFIG_FILE_PATH 
                        imports the configuration file
    """

commands =  [ # Used for autocompletion generation
    command("docs", ["-a", "--api", "-o", "--offline"]),
    command("register", []),
    command("config", ["-e", "--export", "-i", "--import"])
]


config = ConfigParser() # Global configuration parser

# The default (and currently only) path to the configuration file
CONFIG_FILE_PATH = f"{os.path.dirname(__file__)}{os.sep}.ahdconfig"


CURRENT_PATH = os.curdir # Keeps track of current directory to return to after executing commands

def main():
    """The primary entrypoint for the ahd script.
    
    All primary business logic is within this function."""

    # Setup arguments for parsing
    arguments = docopt(usage, version="ahd V 0.3.0")

    if len(sys.argv) == 1:
        print("\n", usage)
        exit()

    if os.path.exists(CONFIG_FILE_PATH): # If the file already exists
        config.read(CONFIG_FILE_PATH) # Read it

    else: # If a file does not exist create one
        with open(CONFIG_FILE_PATH, "w") as config_file:
                config.write(config_file)
    
    # Begin argument parsing

    # ========= Docs argument parsing =========
    if arguments["docs"]:
        if not arguments["--offline"] and not arguments["--api"]:
            webbrowser.open_new("https://ahd.readthedocs.io")
            exit()
        else:
            if arguments["--offline"]:
                # TODO
                print("Not yet implemented")

            if arguments["--api"]:
                # TODO
                print("Not yet implemented")

    # ========= config argument parsing =========
    if arguments["config"]:
        if not arguments["--export"] and not arguments["--import"]:
            print(usage)
            exit()
        if arguments["--export"]:
            with open(f"{os.path.abspath(os.curdir)}{os.sep}.ahdconfig", "w") as config_file:
                config.write(config_file)

        if arguments["--import"]:

            new_config_path = arguments["--import"]
            new_config = ConfigParser()
            
            new_config.read(new_config_path)
            try:
                os.remove(CONFIG_FILE_PATH)
                print(f"Importing {os.path.abspath(new_config_path)} to {CONFIG_FILE_PATH}")
                with open(CONFIG_FILE_PATH, "w") as config_file:
                    new_config.write(config_file)
            except PermissionError:
                print(f"{colored.fg(1)} Unable to import configuration file, are you sudo?")
                print(f"{colored.fg(15)}\tTry running: sudo ahd config -i \"{arguments['--import']}\" ")

        
            
    # ========= preprocessing commands and paths =========
    if not arguments["<paths>"]:
        logging.debug("No paths argument registered setting to \'\'")
        arguments["<paths>"] = ""
    else:
        arguments["<paths>"] = _preprocess_paths(arguments["<paths>"])
    
    if not arguments["<command>"]:
        logging.debug("No command argument registered setting to \'\'")
        arguments["<command>"] = ""
    
    if "." == arguments["<command>"]: # If <command> is . set to specified value
        logging.debug(f". command registered, setting to {config[arguments['<name>']]['command']}")
        arguments["<command>"] = config[arguments["<name>"]]["command"]

    # ========= register argument parsing =========
    if arguments["register"]:
        logging.info(f"Registering command {arguments['<name>']} with \nCommand: {arguments['<command>']} \nPaths: {arguments['<paths>']}")
        if not arguments["<name>"] or not arguments["<paths>"]:
            print(usage)
            exit()
        config[arguments["<name>"]] = {
            "command": arguments["<command>"],
            "paths": arguments["<paths>"],
        }

        try:
            logging.info(f"Begin writing config file to {CONFIG_FILE_PATH}")
            with open(CONFIG_FILE_PATH, "w") as config_file:
                config.write(config_file)
        except PermissionError:
                print(f"{colored.fg(1)}Unable to register command are you sudo?")
                print(f"{colored.fg(15)}\tTry running: sudo ahd register {arguments['<name>']} \"{arguments['<command>']}\" \"{arguments['<paths>']}\" ")

        if not os.name == "nt": # Generate bash autocomplete
            for index, custom_command in enumerate(config):
                if not index == 0: # for some reason the first thing in config object is garbage
                    commands.append(command(custom_command, []))

            autocomplete_file_text = generate_bash_autocomplete(commands)
            try:
                with open("/etc/bash_completion.d/ahd.sh", "w") as autocomplete_file:
                    autocomplete_file.write(autocomplete_file_text)
                print("Bash autocompletion file written to /etc/bash_completion.d/ahd.sh \nPlease restart shell for autocomplete to update")
            except PermissionError:
                print(f"{colored.fg(1)}Unable to write bash autocompletion file are you sudo?")

        # Since executing commands requires changing directories, make sure to return after
        os.chdir(CURRENT_PATH)
        exit()

    else: # If not registering a command

    # ========= User command argument parsing =========
        
        if arguments['<name>']:
            if "register" == arguments['<name>']:
                print(usage)
                exit()
            logging.info(f"Beggining execution of {arguments['<name>']}")
            try:
                paths = _postprocess_paths(config[arguments['<name>']]['paths'])
                current_command = config[arguments['<name>']]['command']
            except KeyError: # TODO Find a way to suggest a similar command
                print(f"{colored.fg(1)}Command not found in configuration validate spelling is correct.")
                exit()
            if len(paths) > 1:
                for current_path in paths:
                    if os.name == "nt":
                        current_path = current_path.replace("/", f"{os.sep}")
                        current_path = current_path.replace("~", os.getenv('USERPROFILE'))
                    print(f"Running: cd {current_path} && {current_command} ".replace("\'",""))
                    subprocess.Popen(f"cd {current_path} && {current_command} ".replace("\'",""), shell=True)

            else: # if only a single path is specified instead of a 'list' of them
                print(f"Running: cd {paths[0]} && {current_command} ".replace("\'",""))
                subprocess.Popen(f"cd {paths[0]} && {current_command} ".replace("\'",""), shell=True)
    


def _preprocess_paths(paths:str) -> str:
    """Preprocesses paths from input and splits + formats them
    into a useable list for later parsing.
    
    Example
    -------
    ```
    paths = '~/Desktop/Development/Canadian Coding/SSB, C:\\Users\\Kieran\\Desktop\\Development\\*, ~\\Desktop\\Development\\Personal\\noter, .'
    
    paths = _preprocess_paths(paths)

    print(paths) # Prints: '~/Desktop/Development/Canadian Coding/SSB,~/Desktop/Development/*,~/Desktop/Development/Personal/noter,.'
    ```
    """
    logging.info(f"Beginning path preprocessing on {paths}")
    result = paths.split(",")
    for index, directory in enumerate(result):
        directory = directory.strip()
        logging.debug(f"Directory: {directory}")
        if directory.startswith(".") and (len(directory) > 1):
            directory = os.path.abspath(directory)
        if not "~" in directory:
            if os.name == "nt":
                directory = directory.replace(os.getenv('USERPROFILE'),"~")

            else:
                directory = directory.replace(os.getenv('HOME'),"~")
            directory = directory.replace("\\", "/")
            result[index] = directory
        else:
            directory = directory.replace("\\", "/")
            result[index] = directory

    logging.debug(f"Result: {result}")
    result = ",".join(result)

    return result

def _postprocess_paths(paths:str) -> list:
    """Postprocesses existing paths to be used by dispatcher.

    This means things like expanding wildcards, and processing correct path seperators.
    
    Example
    -------
    ```
    paths = 'C:\\Users\\Kieran\\Desktop\\Development\\Canadian Coding\\SSB, C:\\Users\\Kieran\\Desktop\\Development\\Canadian Coding\\website, ~/Desktop/Development/Personal/noter, C:\\Users\\Kieran\\Desktop\\Development\\*'
    
    paths = _preprocess_paths(paths)

    print(_postprocess_paths(paths)) 
    # Prints: ['C:/Users/Kieran/Desktop/Development/Canadian Coding/SSB', ' C:/Users/Kieran/Desktop/Development/Canadian Coding/website', ' C:/Users/Kieran/Desktop/Development/Personal/noter', 'C:/Users/Kieran/Desktop/Development/Canadian Coding', 'C:/Users/Kieran/Desktop/Development/Personal', 'C:/Users/Kieran/Desktop/Development/pystall', 'C:/Users/Kieran/Desktop/Development/python-package-template', 'C:/Users/Kieran/Desktop/Development/Work']
    ```
    """
    logging.info(f"Beginning path postprocessing on {paths}")

    paths = paths.split(",")
    result = []
    for directory in paths:
        directory = directory.strip()

        if os.name == "nt":
            directory = directory.replace("/", "\\")

        if directory.startswith("."):
            try:
                if directory[1] == "/" or directory[1] == "\\":
                    directory = f"{os.curdir}{directory[1::]}"
            except IndexError:
                directory = os.path.abspath(".")

        if "~" in directory:
            if os.name == "nt":
                directory = directory.replace("~",f"{os.getenv('USERPROFILE')}")
            else:
                directory = directory.replace("~", f"{os.getenv('HOME')}")
        
        if "*" in directory:

            wildcard_paths = glob.glob(directory.strip())

            for wildcard_directory in wildcard_paths:
                wildcard_directory = wildcard_directory.replace("\\", "/")
                result.append(wildcard_directory)
        else:
            result.append(directory)

    logging.debug(f"Result: {result}")
    return result


if __name__ == "__main__":
    main()
