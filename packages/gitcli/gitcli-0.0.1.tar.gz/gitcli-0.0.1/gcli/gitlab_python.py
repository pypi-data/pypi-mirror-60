import gitlab
from gcli.config import CONFIG

gl = gitlab.Gitlab(url=CONFIG["git_url"], private_token=CONFIG["private_token"])


def search_issue(regex):
    gl.search("issues", regex)


def _print_projects_list(projects_list):
    for p in projects_list:
        a = p.attributes
        print(a["id"], a["path_with_namespace"])


def projects_list(search=None):
    """ lists gitlab projects """
    projects = gl.projects.list(search=search)
    _print_projects_list(projects)


def get_project_attributes(project_id):
    """ get project attributes """
    p = gl.projects.get(project_id)
    return p.attributes


def _demo_get_project_attributes():
    assert get_project_attributes(191)


if __name__ == "__main__":
    # projects_list(search="pdk")
    # projects_list()
    print(get_project_attributes(191))
