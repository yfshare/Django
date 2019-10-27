from django.contrib.auth.models import Group,Permission
from django.contrib.auth.mixins import PermissionRequiredMixin,LoginRequiredMixin
from django.views.generic import View,ListView,DetailView
from pure_pagination.mixins import PaginationMixin
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render
from django.db.models import Q
from django.http import HttpResponse,QueryDict,HttpResponseRedirect,JsonResponse
from django.urls import reverse

class PowerlistView(LoginRequiredMixin,PermissionRequiredMixin, PaginationMixin, ListView):
    model = Permission
    template_name = "permission/powerlist.html"
    context_object_name = "permissions"
    paginate_by = 5
    keyword = ''
    login_url = '/login/'
    permission_required = ('users.admin',)

    #搜索
    def get_queryset(self):
        queryset = super(PowerlistView, self).get_queryset()
        self.keyword = self.request.GET.get('keyword','').strip()
        print(self.keyword)
        if self.keyword:
            queryset = queryset.filter(Q(codename__icontains=self.keyword)| Q(name__icontains=self.keyword))
        return queryset
    #显示搜索关键字
    def get_context_data(self, **kwargs):
        context = super(PowerlistView,self).get_context_data(**kwargs)
        context['keyword'] = self.keyword
        context['user'] = self.request.user.username
        ContentType_object_list = ContentType.objects.all()

        context['ContentType_object_list'] = ContentType_object_list
        #print(context)
        return context

    """
        创建权限
    """

    def post(self, request):
        data = QueryDict(self.request.body).dict()
        print(data)
        try:
            self.model.objects.create(**data)
            res = {'code': 0, 'result': '添加权限成功'}
        except Exception as e:
                #logger.error("create user  error: %s" % traceback.format_exc())
            print(e)

            res = {'code': 1, 'errmsg': '添加权限失败'}

        print(JsonResponse(res))
        return JsonResponse(res, safe=True)

    def delete(self,request,**kwargs):
        print(kwargs)
        data = QueryDict(request.body).dict()
        id = data['id']

        try:
            self.model.objects.get(id=id).delete()
            res = {'code': 0, 'result': '删除成功'}
        except:
        # print(id)
            res = {'code': 1, 'errmsg': '删除失败'}
        return JsonResponse(res, safe=True)

class PowerView(LoginRequiredMixin,PermissionRequiredMixin,DetailView):
    login_url = '/login/'  # 用户没有通过或者权限不够时跳转的地址，默认是 settings.LOGIN_URL.
    # 把没通过检查的用户重定向到没有 "next page" 的非登录页面时，把它设置为 None ，这样它会在 URL 中移除。
    redirect_field_name = 'redirect_to'

    permission_required = (
    'users.add_permission', 'users.change_permission', 'users.delete_permission', 'users.view_permission')
    """
        更新权限
    """
    template_name = 'permission/modify_power.html'
    model = Permission
    context_object_name = 'power'

    def get_context_data(self, **kwargs):
        context = super(PowerView,self).get_context_data(**kwargs)
        # context['keyword'] = self.keyword
        # context['user'] = self.request.user.username
        ContentType_object_list = ContentType.objects.all()

        context['ContentType_object_list'] = ContentType_object_list
        #print(context)
        return context

    def post(self, request, **kwargs):
        print(request.POST)  # <QueryDict: {'id': ['7'], 'username': ['aa'], 'name_cn': ['bb'], 'phone': ['13305779168']}>
        print(kwargs)  # {'pk': '7'}
        print(request.body)  # b'id=7&username=aa&name_cn=bb&phone=13305779168'
        pk = kwargs.get("pk")
        data = QueryDict(request.body).dict()
        print(data)  # {'id': '7', 'username': 'aa', 'name_cn': 'bb', 'phone': '13305779168'}
        #_userForm = UserUpdateForm(request.POST)
        #if _userForm.is_valid():
        try:
            self.model.objects.filter(pk=pk).update(**data)
            res = {'code': 0, "next_url": reverse("users:power_list"), 'result': '更新权限成功'}
        except Exception as e:
            print(e)
            res = {'code': 1, "next_url": reverse("users:power_list"), 'errmsg': '更新权限失败'}

    # else:
    #     # 获取所有的表单错误
    #     print(_userForm.errors)
    #     res = {'code': 1, "next_url": reverse("users:user_list"), 'errmsg': _userForm.errors}
        return render(request, settings.JUMP_PAGE, res)