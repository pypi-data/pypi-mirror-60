import pathlib
import os
import sys
from pprint import pprint
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

import click
import requests
import gitlab
from cookiecutter.main import cookiecutter

from gcli.pull_repos import pull_repos as pull_gitlab_repos
from gcli.clone import clone_wikis
from gcli.clone import clone_notebooks
from gcli.clone import clone as clone_repo
from gcli.config import CONFIG
from gcli.config import print_config
from gcli.config import remove_path
from gcli import __version__


gl = gitlab.Gitlab(url=CONFIG["git_url"], private_token=CONFIG["private_token"])
home = pathlib.Path.home()
cwd = pathlib.Path.cwd()


def _print_projects_list(projects_list):
    for p in projects_list:
        a = p.attributes
        print("  ", a["id"], a["path_with_namespace"])


def _print_issues_list(issues_list, key="title"):
    for i in issues_list:
        a = i.attributes
        print(a["id"], a[key])


def print_version(ctx, param, value):
    """ Prints the version """
    if not value or ctx.resilient_parsing:
        return
    click.echo(__version__)
    ctx.exit()


@click.command()
def status():
    """ Show CLI version, gitlab connection status and python version"""
    print("CLI v{}".format(__version__))

    url = CONFIG["git_url"]
    try:
        requests.get(url, timeout=1)
        print(f"[V] Git server {url} is up and available")
    except Exception as e:
        print(f"[X] Could not reach the Git server ({url})")

    print("[V] Python {}".format(sys.version[:5]))


@click.group()
def issues():
    """ Work with gitlab issues"""


@click.command(name="list")
def issues_list():
    """ list my Gitlab issues"""
    issues = gl.issues.list()
    _print_issues_list(issues)


@click.command(name="project")
@click.argument("project_id")
def issues_project(project_id):
    """ list gitlab issues for a project_id number"""
    p = gl.projects.get(int(project_id))
    issues = p.issues.list()
    _print_issues_list(issues)


@click.command(name="remove")
@click.argument("path", default=None, required=False)
def remove(path=None):
    """ Stop tracking a repo by removing its path from ~/.gitcli.yml """
    remove_path(path)


@click.group()
def project():
    """ Work with gitlab projects"""


@click.command(name="list")
@click.argument("key", default=None, required=False)
def project_list(key):
    """ search Gitlab projects"""
    projects = gl.projects.list(all=True, search=key)
    _print_projects_list(projects)


@click.command(name="info")
@click.argument("project_id")
@click.argument("project_attribute", default=None, required=False)
def project_info(project_id, project_attribute):
    """ get Gitlab's project info from project_id"""
    project = gl.projects.get(int(project_id))
    if project_attribute:
        print(project.attributes.get(project_attribute))
        return project.attributes.get(project_attribute)
    pprint(project.attributes)
    return project.attributes


@click.command(name="clone")
@click.argument("project_id")
def clone(project_id):
    """ Clone a project by name or project_id"""
    try:
        p = gl.projects.get(project_id)
    except Exception:
        projects = gl.projects.list(search=project_id)

        if len(projects) == 1:
            project_id = projects[0].get_id()
        else:
            if projects:
                print(
                    "Found multiple project_ids, try again with the exact project name or project id number"
                )
                _print_projects_list(projects)
                sys.exit()
            else:
                print("Type a valid project name or project id")
                sys.exit()
        p = gl.projects.get(project_id)

    repo_name = p.attributes["name"]
    repo_url = p.attributes["ssh_url_to_repo"]
    repo_path = str(cwd / repo_name)
    clone_repo(repo_url, repo_path)


@click.group()
def pull():
    """ git clone or git pull Gitlab projects """


@click.command(name="repos")
def pull_repos():
    """ git pull on each project downloaded"""
    pull_gitlab_repos()


@click.command(name="wikis")
def pull_wikis():
    """ clone all the wikis in ~/files/wikis"""
    clone_wikis()


@click.command(name="notebooks")
def pull_notebooks():
    """ clone all the python jupyter notebooks"""
    clone_notebooks()


@click.command(name="template")
@click.argument("template_name_or_url", required=False, default=None)
def template(template_name_or_url):
    """ add cookiecutter template (url, python_project, wiki, jupyter_notebook_project)
    """

    overwrite_if_exists = True
    templates = CONFIG.get("templates")

    if template_name_or_url in templates:
        template_name_or_url = templates.get(template_name_or_url)
    else:
        e = f"`{template_name_or_url}` is not a valid cookiecutte template. please use a valid cookiecutter template url or name:"
        if templates:
            print([f"- {template} \n" for template in templates.keys()])
            # print('\n'.join(templates.keys()))
        print(e)
        return

    return cookiecutter(template_name_or_url, overwrite_if_exists=overwrite_if_exists)


@click.command(name="key")
def get_ssh_key():
    """ Show public SSH key (create one if does not exist) """
    ssh_folder = home / ".ssh"
    key_path_public = ssh_folder / "id_rsa.pub"
    key_path_private = ssh_folder / "id_rsa"

    if not os.path.isfile(key_path_private):
        key = rsa.generate_private_key(
            backend=default_backend(), public_exponent=65537, key_size=2048
        )

        # get public key in OpenSSH format
        public_key = key.public_key().public_bytes(
            serialization.Encoding.OpenSSH, serialization.PublicFormat.OpenSSH
        )

        pem = key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )

        private_key = pem.decode("utf-8")
        public_key = public_key.decode("utf-8")

        if not os.path.isdir(ssh_folder):
            os.makedirs(ssh_folder)

        with open(key_path_private, "w") as f:
            f.write(private_key)
        with open(key_path_public, "w") as f:
            f.write(public_key)

        os.chmod(key_path_private, 0o0600)
        os.chmod(key_path_public, 0o0600)

    else:
        public_key = open(key_path_public).read()
    click.echo(public_key)


@click.command(name="config")
@click.argument("key", required=False, default=None)
def config_get(key):
    """ Shows key values from CONFIG """
    print_config(key)


@click.group()
@click.option(
    "--version",
    is_flag=True,
    callback=print_version,
    expose_value=False,
    is_eager=True,
    help="Show the version number.",
)
def cli():
    """ `gcli` is a command line tool to create repos, test and keep your computer up to date
    """


pull.add_command(pull_repos)
pull.add_command(pull_wikis)
pull.add_command(pull_notebooks)

project.add_command(project_list)
project.add_command(project_info)

issues.add_command(issues_list)
issues.add_command(issues_project)

# Set up top-level group
cli.add_command(status)
cli.add_command(issues)
cli.add_command(config_get)
cli.add_command(clone)
cli.add_command(pull)
cli.add_command(template)
cli.add_command(project)
cli.add_command(remove)
cli.add_command(get_ssh_key)

if __name__ == "__main__":
    cli()
