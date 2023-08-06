# git-cd
[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/Doma1204/git-cd/Python_Unit_Test)](https://github.com/Doma1204/git-cd/actions)
[![GitHub release](https://img.shields.io/github/v/release/Doma1204/git-cd)](https://github.com/Doma1204/git-cd/releases)
[![PyPI](https://img.shields.io/pypi/v/git-cd?color=brightgreen)](https://pypi.org/project/git-cd)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/git-cd)](https://pypi.org/project/git-cd/#files)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/git-cd)
[![Licence](https://img.shields.io/github/license/Doma1204/git-cd)](https://github.com/Doma1204/git-cd/blob/master/LICENSE)

A terminal tool for easy navigation to local git repository. It let you change to a repository directory easily.

### Table of content
- [Installation](#Installation)
    - [Install with pip](#Install-with-pip)
- [Usage](#Usage)
    - [Change Directory](#Change-Directory)
    - [Indexing Local Repositories](#Indexing-Local-Repository)
    - [Update Local Repository Index](#Update-Local-Repository-Index)
    - [Autocompletion](#Autocompletion)
- [Dependencies](#Dependencies)
- [Licence](#Licence)

## Installation
### Install with pip
``` bash
$ pip3 install git-cd
```

## Usage
Type `gitcd` or `gitcd -h` will show you the command help page
```
$ gitcd
Usage: gitcd [OPTIONS] [REPO]

  gitcd [your-repo-name]

  Terminal tool for easy navigation to local git repository

  For more detail: please visit https://github.com/Doma1204/gitcd

Options:
  -i, --index             index all the local repo
  -u, --update            update the local repo index
  -p, --path PATH         only find local repo under this path
  -a, --autocomplete      activate shell autocompletion
  -s, --shell [bash|zsh]  specify the shell
  -h, --help              Show this message and exit.
```

### Change Directory
```bash
$ gitcd [repo-name]
```
It changes the current directory to the corresponding local repository. Press `Tab` to autocomplete the repository name if needed(activate [autocompletion](#Autocompletion) is required)

### Indexing Local Repositories
Before using `gitcd` to change directory, you needs to first index you local repositories. Use the commmand below to start indexing.
```bash
$ gitcd -i
```
The default root directory is home directory(`~/`). It starts finding local repositories recursively from the root directory. You can change the root directory by using `-p`.
```bash
$ gitcd -i -p [root-path]
```

### Update Local Repository Index
If some of the repositories have been deleted, the old index will still contain those invalid repositories directory, and errors occur when you attemps to cd into deleted repositories. Thus, you needs to update the local repository index by the following command. It deletes all invalid repositories.
```bash
$ gitcd -u
```

### Autocompletion
Limited by [Click](https://pypi.org/project/click/), autocompletion only support `bash` and `zsh` shell. To activate autocompletion, use the command below:
```bash
$ gitcd -a
```
In normal cases, it detects the current shell and activate the autocompletion of that shell, but you can specify the shell that you wants to activate by using `-s`.
```bash
$ gitcd -a -s [bash or zsh]
```

To actiavte autocompletion manually, you needs to add the following line to you `.bashrc`(`bash`) or `.zshrc`(`zsh`).

For `bash`: `eval "$(_GITCD_COMPLETE=source gitcd)"`

For `zsh`: `eval "$(_GITCD_COMPLETE=source_zsh gitcd)"`

## Dependencies
The tool is built on top of [Click](https://pypi.org/project/click/).

## Licence
[MIT Licence](https://github.com/Doma1204/git-cd/blob/master/LICENSE)