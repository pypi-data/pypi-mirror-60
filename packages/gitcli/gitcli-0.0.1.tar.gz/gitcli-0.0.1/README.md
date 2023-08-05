# Git Command Line 0.0.1

Command line to:

- clone repos from Gitlab, by approximate name
- templates: create templates with cookiecutter for different projects (python, wiki, jupyter-notebooks)
- pull changes for all the repos that you have downloaded
- pull all wikis into your local computer

# Usage

- `gcli` with no arguments lists all commands
- `gcli clone`: clone repos from Git
- `gcli config`: show key values from CONFIG
- `gcli pull`: pull already downloaded repos or wikis
- `gcli status`: checks gcli and python version
- `gcli template`: creates a template

# Installation

Type `pip install gitcli --upgrade` in a terminal

You will need to create a token in Gitlab and add it to your local config in `~/.gcli.yml`

```
git_url: https://gitlab.com
private_token: AddYourTokenTo ~/.gitcli.yml
wiki2url:
    wiki1_name: wiki1_url
templates:
    template1_name: template1_url

```

# TODO

- It works with gitlab. Need to test it with github

References:

- https://github.com/awslabs/aws-sam-cli
- https://python-gitlab.readthedocs.io/en/stable/gl_objects/projects.html
- https://github.com/audreyr/cookiecutter
- gem install gitlab_cli
