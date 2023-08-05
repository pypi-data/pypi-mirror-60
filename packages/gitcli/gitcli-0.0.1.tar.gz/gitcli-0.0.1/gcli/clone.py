import os
import subprocess
import git

from gcli.config import CONFIG
from gcli.config import append_path2url


def clone_name2url(name2url, path=os.getcwd()):
    """ clone urls into path directory """
    print("cloning {} into {}".format(", ".join(name2url.keys()), path))
    if not os.path.isdir(path):
        os.makedirs(path)

    for repo_name, repo_url in name2url.items():
        repo_path = os.path.join(path, repo_name)

        if os.path.isdir(repo_path):
            print("git pull {}".format(repo_path))
            g = git.cmd.Git(repo_path)
            g.pull()
        else:
            print("git clone {} {}".format(repo_url, repo_path))
            git.Repo.clone_from(repo_url, to_path=repo_path)
        append_path2url(repo_path, repo_url)


def clone_wikis():
    clone_name2url(CONFIG["wiki2url"], path=CONFIG["wikis_path"])


def clone_notebooks():
    clone_name2url(CONFIG["notebooks2url"], path=CONFIG["notebooks_path"])


def clone(url, repo_path=os.getcwd()):
    """ clones a git repository
    if repo_path already exists, git pulls instead
    """
    home = os.path.expandvars("$HOME")
    known_hosts_path = os.path.join(home, ".ssh", "known_hosts")

    if not os.path.exists(known_hosts_path):
        host = subprocess.check_output(
            ["ssh-keyscan", CONFIG['git_url']]
        ).decode()
        with open(known_hosts_path, "w") as f:
            f.write(host)

    if os.path.isdir(repo_path):
        print("git pull {}".format(repo_path))
        g = git.cmd.Git(repo_path)
        g.pull()

    else:
        print("git clone {} {}".format(url, repo_path))
        git.Repo.clone_from(url, to_path=repo_path)
    append_path2url(repo_path, url)
    return repo_path


if __name__ == "__main__":
    # clone_and_install_projects()
    clone_wikis()
