from django.urls import path, re_path
from users import views,user,group,permission

app_name = 'users'
urlpatterns = [
    path("",views.IndexView.as_view(), name='index'),
    # path('login1/',views.loginAuthView1, name='login1'),
    # path('login2/',views.loginAuthView2.as_view(), name='login2'),
    path('login/',views.LoginView.as_view(), name='login'),
    path('logout/',views.LogoutView.as_view(), name='logout'),
    path('userlist/',user.UserListView.as_view(), name='user_list'),
    path('adduser/',user.AdduserView.as_view(), name='add_user'),
    path('modifypass/',user.ModifyPwdView.as_view(), name='modify_pwd'),
    re_path('userdetail/(?P<pk>[0-9]+)?/$',user.UserDetailView.as_view(), name='user_detail'),
    path('rolelist/',group.RolelistView.as_view(), name='role_list'),
    re_path('roledetail/(?P<pk>[0-9]+)?/$',group.RoleDetailView.as_view(), name='role_detail'),
    path('powerlist/',permission.PowerlistView.as_view(), name='power_list'),
    re_path('modifypower/(?P<pk>[0-9]+)?/$',permission.PowerView.as_view(),name='modify_power'),
]