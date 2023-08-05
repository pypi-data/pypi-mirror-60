import os
import git

from gcli.config import CONFIG


def pull_repo(repo_path):
    """ pull repo
    """

    if os.path.isdir(repo_path):
        print("git pull: {}".format(repo_path))
        g = git.cmd.Git(repo_path)
        g.pull()


def pull_repos():
    """ git pull repos installed through the CLI
    reads repo paths and url ~/.gitcli.yml
    """
    path2url = CONFIG.get("path2url")

    if path2url:
        for path, url in path2url.items():
            pull_repo(path)


if __name__ == "__main__":
    pull_repos()
