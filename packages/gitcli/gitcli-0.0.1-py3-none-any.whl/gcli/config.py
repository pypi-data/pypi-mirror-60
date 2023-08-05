""" loads a configuration from a config file on your disk `~/.gitcli.yml`
the config file stores the path of all the repos that you download

wiki2url:
    wiki1_name: wiki1_url
templates:
    template1_name: template1_url

"""

import sys
import pathlib
import os
import logging
from pprint import pprint
import distro
import hiyapyco

__all__ = ["CONFIG"]
__version__ = "0.0.1"


default = """
git_url: https://gitlab.com
private_token: AddYourTokenTo ~/.gitcli.yml
"""
if sys.platform == "win32":
    operating_system = "windows"
elif sys.platform == "darwin":
    operating_system = "mac"
else:
    try:
        if distro.linux_distribution()[0].startswith("CentOS"):
            operating_system = "centos"
        elif distro.linux_distribution()[0].startswith("Ubuntu"):
            operating_system = "ubuntu"
        else:
            operating_system = distro.linux_distribution()[0]
    except Exception:
        operating_system = "linux"


home = pathlib.Path.home()
cwd = pathlib.Path(__file__).parent.absolute()
repo = cwd.parent
cwd_config = pathlib.Path.cwd() / "config.yml"
local_config_path = str(home / ".gitcli.yml")


CONFIG = hiyapyco.load(
    default,
    str(cwd_config),
    str(local_config_path),
    failonmissingfiles=False,
    loglevelmissingfiles=logging.DEBUG,
)

CONFIG["root"] = cwd
CONFIG["repo"] = repo
CONFIG["home"] = home
CONFIG["log_path"] = home / ".gitcli.log"
CONFIG["local_config_path"] = local_config_path
CONFIG["os"] = operating_system
CONFIG["version"] = __version__

CONFIG["code_path"] = home / "code"
CONFIG["wikis_path"] = home / "wikis"
CONFIG["notebooks_path"] = home / "notebooks"


def create_local_config(local_config_path=local_config_path):
    """ Creates a local config file ~/.gitcli.yml in your computer """

    if os.path.exists(local_config_path):
        return "Local configuration file {} already exists".format(local_config_path)

    # Load the template and render
    config = "path2url: {}"

    # Write to disk
    try:
        with open(local_config_path, "w") as f:
            f.write(config)
        print("Generated local configuration file {}".format(local_config_path))
    except Exception:
        print("No access to local configuration file {}".format(local_config_path))


def save_config(config, path=local_config_path):
    """ saves a CONFIG dict into disk """
    try:
        with open(path, "w") as f:
            f.write(hiyapyco.dump(config))
    except Exception:
        print("No access to local configuration file {}".format(local_config_path))


def read_config(path=local_config_path):
    """ reads CONFIG dict from disk """
    if os.path.exists(path):
        return hiyapyco.load(
            path, failonmissingfiles=False, loglevelmissingfiles=logging.DEBUG
        )
    else:
        create_local_config(path)
        read_config(path)


def append_config(config, path=local_config_path):
    """ appends CONFIG dict into disk """
    existing_config = read_config(path=path)
    if existing_config is None:
        create_local_config()

    existing_config.update(config)
    save_config(existing_config)


def append_path2url(path, url, config_path=local_config_path):
    """ appends CONFIG dict into .gitcli.yml """
    existing_config = read_config(config_path)
    if existing_config is None:
        existing_config = {}
        existing_config["path2url"] = {}
    elif existing_config.get("path2url") is None:
        existing_config["path2url"] = {}
    elif path not in existing_config["path2url"].keys():
        existing_config["path2url"][path] = url
    save_config(existing_config)


def print_paths(paths):
    """ print paths list """
    for path in paths:
        print("  ", path)


def print_config(key=None):
    """ prints config key or all config Keys """
    if key:
        if CONFIG.get(key):
            print(CONFIG[key])
        else:
            print(f"`{key}` key not found in {cwd_config}")
    else:
        pprint(CONFIG)


def remove_path(path=None, config_path=local_config_path):
    """ removes repo path from .gitcli.yml """
    existing_config = read_config(config_path)
    if existing_config.get("path2url") is None:
        existing_config["path2url"] = {}
    elif path in existing_config["path2url"].keys():
        print("stopped tracking {} ".format(path))
        existing_config["path2url"].pop(path)
    elif path:
        print("{} is not being tracked".format(path))
        print("Projects currently tracked:")
        print_paths(existing_config["path2url"].keys())
    else:
        print("Projects currently tracked:")
        print_paths(existing_config["path2url"].keys())
    save_config(existing_config)


def test_config():
    assert CONFIG


if __name__ == "__main__":
    print(", ".join(CONFIG["wiki2url"].keys()))
    # print(CONFIG["wiki2url"])
    # print(type(CONFIG['repos']['hardware']))
    # print(CONFIG["teams"])
    # save_config(CONFIG)
    # save_config(CONFIG)
    # print(read_config()["name2id"])
