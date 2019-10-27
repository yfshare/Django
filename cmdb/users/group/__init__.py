from django.contrib.auth.models import Group,Permission
from django.contrib.auth.mixins import PermissionRequiredMixin,LoginRequiredMixin
from django.views.generic import View,ListView,DetailView
from pure_pagination.mixins import PaginationMixin
from django.http import Http404,JsonResponse,QueryDict
from users.forms import RoleProfileForm
from users.forms import UserProfile
from django.shortcuts import render,reverse
from django.conf import settings
import traceback,logging

class RolelistView(LoginRequiredMixin,PermissionRequiredMixin, PaginationMixin, ListView):
    model = Group
    template_name = "group/rolelist.html"
    context_object_name = "groups"
    paginate_by = 3
    keyword = ''
    login_url = '/login/'
    permission_required = ('users.admin',)
    # permission_required = ('users.view_userprofile', 'users.delete_userprofile', 'users.add_userprofile', 'users.change_userprofile')

    def get_queryset(self):    #搜索功能
        queryset = super(RolelistView,self).get_queryset()   #查询所有用户信息
        self.keyword = self.request.GET.get('keyword','').strip()
        if self.keyword:
            queryset = queryset.filter(name__icontains=self.keyword)
            # __icontains 查询, Q 支持多条件查询
        return queryset

    def get_context_data(self, **kwargs):   #返回前端显示
        context = super(RolelistView, self).get_context_data(**kwargs)
        # print(context)
        context['keyword'] = self.keyword
        return context

    #添加组
    def post(self, request):
        print('request: ',request)
        _roleForm = RoleProfileForm(request.POST)
        print('rolefrom: ',_roleForm)
        if _roleForm.is_valid():
            try:
                data = _roleForm.cleaned_data
                self.model.objects.create(**data)
                res = {'code': 0, 'result': '添加组成功'}
            except:
                # logger.error("create user  error: %s" % traceback.format_exc())
                res = {'code': 1, 'errmsg': '添加组失败'}
        else:
            # 获取自定义的表单错误的两种常用方式
            print('form_error: ',_roleForm.errors)
            print('form_error_as_json: ',_roleForm.errors.as_json())
            print('form_error_name: ',_roleForm.errors['name'][0])  # 已存在一位使用该名字的用户
            res = {'code': 1, 'errmsg': _roleForm.errors.as_json()}

        return JsonResponse(res, safe=True)

    def delete(self, request,**kwargs):
        data = QueryDict(request.body).dict()
        print(data)
        pk = data.get('id')
        try:
            group = self.model.objects.filter(id=pk)
            # print(group)
            group.delete()
            res = {'code': 0, 'result': '删除用户成功'}
            # logging.error("edit  user group power error: %s" % traceback.format_exc())
        except:
            res = {'code': 1, 'errmsg': '删除用户失败'}
            # logging.error("edit  user group power error: %s" % traceback.format_exc())
        return JsonResponse(res,safe=True)

class RoleDetailView(LoginRequiredMixin, DetailView):
    """
    组详情
    """
    model = Group
    template_name = 'group/group_edit.html'
    context_object_name = "group"
    pk_url_kwarg = 'pk'

    # 返回所有权限，并将当前组所拥有的权限选中
    def get_context_data(self, **kwargs):
        context = super(RoleDetailView, self).get_context_data(**kwargs)
        context['group_has_permissions'] = self._get_group_permission()
        context['group_not_permissions'] = self._get_group_not_permission()
        context['role_has_users'],context['group_has_permissions'] = self._get_role_power()
        context['role_not_users'],context['group_not_permissions'] = self._get_role_not_power()
        return context

    # 获取当前角色所有用户，权限以列表形式返回
    def _get_role_power(self):
        pk = self.kwargs.get(self.pk_url_kwarg)
        try:
            role = self.model.objects.get(pk=pk)
            users = role.user_set.all()
            return users,role.permissions.all()
        except self.model.DoesNotExist:
            raise Http404

    # 获取当前角色没有的用户，权限，以列表形式返回
    def _get_role_not_power(self):
        pk = self.kwargs.get(self.pk_url_kwarg)
        try:
            role = self.model.objects.get(pk=pk)
            all_user = UserProfile.objects.all()
            users = [user for user in all_user if user not in role.user_set.all()]
            all_perms = Permission.objects.all()
            perms = [perm for perm in all_perms if perm not in role.permissions.all()]
            return users,perms
        except:
            return JsonResponse([], safe=False)

    # 获取当前组所有权限，以列表形式返回
    def _get_group_permission(self):
        pk = self.kwargs.get(self.pk_url_kwarg)
        try:
            role = self.model.objects.get(pk=pk)
            users = role.user_set.all()
            return users,role.permissions.all()
        except self.model.DoesNotExist:
            raise Http404

    # 获取当前组没有的权限，以列表形式返回
    def _get_group_not_permission(self):
        pk = self.kwargs.get(self.pk_url_kwarg)
        try:
            group = Group.objects.get(pk=pk)
            all_perms = Permission.objects.all()
            perms = [perm for perm in all_perms if perm not in group.permissions.all()]
            return perms
        except:
            return JsonResponse([], safe=False)

    #修改角色
    def post(self, request, **kwargs):
        #ops.user_set.set([2])
        print(request.POST)
        print(request.POST.getlist('users', []))
        user_id_list = request.POST.getlist('users_selected', [])
        permission_id_list = request.POST.getlist('perms_selected', [])
        pk = kwargs.get("pk")
        try:
            role = self.model.objects.get(pk=pk)
            # user.groups.set(group_id_list)
            print(user_id_list)
            role.user_set.set(user_id_list)
            role.permissions.set(permission_id_list)
            res = {'code': 0, 'next_url': reverse("users:role_list"), 'result': '角色权限更新成功'}
        except:
            res = {'code': 1, 'next_url': reverse("users:role_list"), 'errmsg': '角色权限更新失败'}
            #logger.error("edit  user group pwoer error: %s" % traceback.format_exc())
        return render(request, settings.JUMP_PAGE, res)

class RolePowerView(LoginRequiredMixin,PermissionRequiredMixin, DetailView):
    login_url = '/login/'  # 用户没有通过或者权限不够时跳转的地址，默认是 settings.LOGIN_URL.
    # 把没通过检查的用户重定向到没有 "next page" 的非登录页面时，把它设置为 None ，这样它会在 URL 中移除。
    redirect_field_name = 'redirect_to'

    permission_required = ('users.view_group','users.delete_group','users.add_group','users.change_group')

    """
    更新角色及权限
    """
    template_name = 'users/role_power.html'
    model = Group
    context_object_name = 'role'

    # 返回所有组、权限，并将当前用户所拥有的组、权限显示
    def get_context_data(self, **kwargs):
        context = super(RolePowerView, self).get_context_data(**kwargs)
        context['role_has_users'],context['role_has_permissions'] = self._get_role_power()
        context['role_not_users'],context['role_not_permissions'] = self._get_role_not_power()
        return context

    # 获取当前角色所有用户，权限以列表形式返回
    def _get_role_power(self):
        pk = self.kwargs.get(self.pk_url_kwarg)
        try:
            role = self.model.objects.get(pk=pk)
            users = role.user_set.all()
            return users,role.permissions.all()
        except self.model.DoesNotExist:
            raise Http404

    # 获取当前角色没有的用户，权限，以列表形式返回
    def _get_role_not_power(self):
        pk = self.kwargs.get(self.pk_url_kwarg)
        try:
            role = self.model.objects.get(pk=pk)
            all_user = UserProfile.objects.all()
            users = [user for user in all_user if user not in role.user_set.all()]
            all_perms = Permission.objects.all()
            perms = [perm for perm in all_perms if perm not in role.permissions.all()]
            return users,perms
        except:
            return JsonResponse([], safe=False)

    #修改角色
    def post(self, request, **kwargs):
        #ops.user_set.set([2])
        print(request.POST)
        print(request.POST.getlist('users', []))
        user_id_list = request.POST.getlist('users_selected', [])
        permission_id_list = request.POST.getlist('perms_selected', [])
        pk = kwargs.get("pk")
        try:
            role = self.model.objects.get(pk=pk)
            # user.groups.set(group_id_list)
            print(user_id_list)
            role.user_set.set(user_id_list)
            role.permissions.set(permission_id_list)
            res = {'code': 0, 'next_url': reverse("users:role_list"), 'result': '角色权限更新成功'}
        except:
            res = {'code': 1, 'next_url': reverse("users:role_list"), 'errmsg': '角色权限更新失败'}
            #logger.error("edit  user group pwoer error: %s" % traceback.format_exc())
        return render(request, settings.JUMP_PAGE, res)