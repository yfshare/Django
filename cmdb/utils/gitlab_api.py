import gitlab
from django.conf import settings
# from cmdb.settings import GITLAB_HTTP_URI,GITLAB_TOKEN

GITLAB_HTTP_URI = "http://123.56.73.115"
GITLAB_TOKEN = "4iBGCWuTtG2Q6VQ5yBYD"

gl = gitlab.Gitlab(GITLAB_HTTP_URI, GITLAB_TOKEN, api_version=4)

def get_user_projects(request):
    """
    获取gitlab里所有的项目，和登录用户所拥有的项目,以及登录用户所拥有项目的项目成员。本项目只实现用户的项目，不做做组
    :return: []
    """
    user_projects = []
    all_projects = gl.projects.list()
    print(request.user.username)
    print(all_projects)

    # 查出所有项目中包含登录用户的项目,即查出当前用户所有的项目
    for project in all_projects:
        for member in project.members.list():
            # if member.username == request.user.username:
            if member.username == 'zp':
                user_projects.append(project)
    return user_projects

def get_project_versions(project_id):
    project = gl.projects.get(project_id)
    tags = project.tags.list()
    print(tags)
    return tags

# get_project_versions(2)

# pip3.6 install --upgrade python-gitlab
# https://python-gitlab.readthedocs.io/en/stable/install.html