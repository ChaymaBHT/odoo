# Runbot Manager

More doc on docs directory.

## Table of contents

[[_TOC_]]

## Installation

To install the runbot command line tools, first activate you Python environment and use pip.

This installation use pyenv but you can use the tool you want.

### Create an new pyenv project

```bash
$ pyenv virtualenv 3.7.2 runbotmgr
```

You can found the available Python version with the command:

```bash
$ pyenv install --list | grep " 3\.[678]"
```

### Install the project on the new pyenv environment

On the root folder of this project:

```bash
$ pyenv activate runbotmgr
$ pip3 install . 
# If you want develop and improve this project you can also use the command
$ pip3 -e install .
$ pyenv rehash # important to refresh you PATH environment variable.
```

To use the command, run the commands:

```bash
$ runbot --list
$ runbotmgr --list
```
