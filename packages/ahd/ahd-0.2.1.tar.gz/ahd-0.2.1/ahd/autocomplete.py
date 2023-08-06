"""This module is used to generate autocomplete files for vaious systems (bash, zsh etc.)

Examples
--------

Creating a bash autocomplete file:

```
>> from ahd.autocomplete import generate_bash_autocomplete, command

>> commands =  [ # Used for autocompletion generation
        command("docs", ["-a", "--api", "-o", "--offline"]),
        command("register", [])
    ]

>> print(generate_bash_autocomplete(commands))
```

Notes
-----
If you need to fix a bug in this file contact me with the cost of the whisky bottle :)
"""

from collections import namedtuple

command = namedtuple("command", ["name", "arguments"])


def _generate_root_autocomplete(commands:list , arguments:list = [], root:str = "ahd") -> str:
    """Generates the first portion of a bash autocomplete file"""
    arguments = _stringify_list(arguments)

    root_template = f"""_{root}()
    {{
        local cur
        cur=\"${{COMP_WORDS[COMP_CWORD]}}\"

        if [ $COMP_CWORD -eq 1 ]; then
            COMPREPLY=( $( compgen -fW '{arguments} {_stringify_list(commands)}' -- $cur) )
        else
            case ${{COMP_WORDS[1]}} in
    """

    for command in commands:
        root_template += f"""
                {command})
                _{root}_{command}
            ;;
        """

    root_template+="""
            esac

        fi
    }
    """

    return root_template
        




def _generate_command_autocomplete(command:str, arguments:list, root:str = "ahd") -> str:
    """Generates a bash autocomplete section for a single command"""
    
    if arguments:
        arguments = _stringify_list(arguments)
    else:
        arguments = " "
    command_result = f"""_{root}_{command}()
    {{
        local cur
        cur=\"\${{COMP_WORDS[COMP_CWORD]}}\"

        if [ $COMP_CWORD -ge 2 ]; then
            COMPREPLY=( $( compgen -W '{arguments}' -- $cur) )
        fi
    }}
    """

    return command_result


def _stringify_list(arguments:list) -> str:
    """Takes a list and stringifies it to a useable format for autocomplete files
    
    Examples
    --------
    >> _stringify_list(["-a", "--api", "-o", "--offline"])
    >> # Returns: '-a --api -o --offline' """
    stringified = ""
    for argument in arguments: # Preprocess arguments into appropriate string form
        stringified += f" {argument}"
    
    return stringified


def generate_bash_autocomplete(commands:list, root:str = "ahd") -> str:
    """Takes a list of commands (namedtuple type) and returns the text necessary
     for a bash autocomplete file"""

    sub_commands = [root] # list of just top level sub-commands
    for command in commands: # Iterate through and pull just subcommands from commands list
        sub_commands.append(command.name)

    arguments = ["-h", "--help", "-v", "--version"]
    for command in commands:
        for argument in command.arguments:
            arguments.append(argument)
    
    autocomplete_text = _generate_root_autocomplete(sub_commands, arguments)

    for command in commands:
        autocomplete_text += _generate_command_autocomplete(command.name, command.arguments)


    autocomplete_text += f"\ncomplete -o bashdefault -o default -o filenames -F _{root} {root}\n"

    return autocomplete_text
