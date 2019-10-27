from django.urls import path, re_path
from .views import *

app_name = 'deploy'
urlpatterns = [
    path("apply/", ApplyView.as_view(), name='apply'),
    path("list/", ApplyListView.as_view(), name='list'),
    re_path("deploy/(?P<pk>[0-9]+)?/",  DeployView.as_view(), name='deploy'),
    path("history/", DeployHistoryView.as_view(), name='history'),
    #
    # # 获取某个项目列表及项目版本
    path("projectlist/", ProjectListView.as_view(), name='project_list'),
    path("projecttag/", GetProjectVersionsView.as_view(), name='project_versions')
]
