from django.shortcuts import render,reverse
from django.contrib.auth.models import Group
from django.http import JsonResponse,QueryDict,HttpResponseRedirect
from django.contrib.auth.mixins import PermissionRequiredMixin,LoginRequiredMixin
from pure_pagination.mixins import PaginationMixin   #pip3 install django-pure-pagination
from users.models import UserProfile
from django.views.generic import View,ListView,DetailView
from django.db.models import Q

from users.forms import UserProfileForm,UserUpdateForm
from django.contrib.auth.hashers import make_password
from django.conf import settings

import traceback,logging

# https://www.cnblogs.com/ccorz/p/6358074.html
class AdduserView(LoginRequiredMixin, PaginationMixin, ListView):
    model = UserProfile
    template_name = "users/adduser.html"
    keyword = ''
    login_url = '/login/'

    def post(self,request):
        print(request.POST)
        _userForm = UserProfileForm(request.POST)
        # print(_userForm)
        if _userForm.is_valid():
            try:
                _userForm.cleaned_data['password'] = make_password('12345678')
                _userForm.cleaned_data['is_active'] = True
                data = _userForm.cleaned_data
                print(data)
                self.model.objects.create(**data)
                res = {'code': 0, 'next_url': reverse("users:user_list"), 'result': '添加用户成功'}
            except:
                res = {'code': 1, 'next_url': reverse("users:user_list"), 'errmsg': '添加用户失败'}
                # logging.error("edit  user group pwoer error: %s" % traceback.format_exc())
        else:
            try:
                # 获取自定义的表单错误的两种常用方式
                print(_userForm.errors)
                print(_userForm.errors.as_json())
                print(_userForm.errors['phone'][0])
                print(_userForm.errors['username'][0])
            except Exception as e:
                # res = {'code': 1, 'errmsg': _userForm.errors.as_json()}
                res = {'code': 1, 'errmsg': _userForm.errors}
        return render(request, settings.JUMP_PAGE, res)

class UserListView(LoginRequiredMixin, PaginationMixin, ListView):
    model = UserProfile    #相当于 UserProfile.objects.all()
    template_name = "users/userlist.html"    #自定义模版路径
    context_object_name = "userlist"   #自定义传给前端模版渲染的变量，默认object_list(查询数据库存放的变量)
    paginate_by = 5
    keyword = ''
    login_url = '/login/'

    def get_queryset(self):    #搜索功能
        queryset = super(UserListView,self).get_queryset()   #查询所有用户信息
        # print('queryset: ',queryset)
        self.keyword = self.request.GET.get('keyword','').strip()
        # print(self.keyword)
        if self.keyword:
            queryset = queryset.filter(Q(name_cn__icontains=self.keyword) |
                                       Q(username__icontains=self.keyword))
            # __icontains 查询, Q 支持多条件查询
        return queryset

    def get_context_data(self, **kwargs):   #返回前端显示
        context = super(UserListView, self).get_context_data(**kwargs)
        # print(context)
        context['keyword'] = self.keyword
        return context

    '''
    删除用户
    '''
    def delete(self,request):
        data = QueryDict(request.body).dict()
        print(data)
        ID = data.get('id')
        print(ID)

        try:
            user = self.model.objects.filter(pk=ID)
            print(user)
            user.delete()
            res = {'code':0,'result':'删除用户成功.'}
        except:
            res = {'code':1,'result':'删除用户成功.'}
        return JsonResponse(res,safe=True)

class UserDetailView(LoginRequiredMixin,PermissionRequiredMixin, PaginationMixin,DetailView):
    '''
    用户详情
    '''
    model = UserProfile
    template_name = "users/user_edit.html"
    context_object_name = 'user'
    permission_required = ('users.admin',)

    '''
    更新用户信息
    '''
    def post(self,request,**kwargs):
        print(request.POST)
        print(kwargs)
        print(request.body)

        ID = kwargs.get('pk')
        data = QueryDict(request.body).dict()
        print(data)

        _userForm = UserUpdateForm(request.POST)
        if _userForm.is_valid():
            try:
                self.model.objects.filter(pk=ID).update(**data)
                res = {'code': 0, "next_url": reverse("users:user_list"), 'result': '更新用户成功'}
            except:
                res = {'code': 1, "next_url": reverse("users:user_list"), 'result': '更新用户失败'}
        else:
            # 获取所有的表单错误
            print(_userForm.errors)
            res = {'code': 1, "next_url": reverse("users:user_list"), 'errmsg': _userForm.errors}
        return render(request, settings.JUMP_PAGE, res)

class ModifyPwdView(LoginRequiredMixin,View):
    '''
    重置密码
    '''
    def get(self,request):
        print(request)
        ID = request.GET.get('uid',None)   # user_edit.html 里修改密码传参为 uid
        return render(request,'users/change_passwd.html',context={'uid':ID})

    def post(self,request):
        uid = request.POST.get('uid',None)
        pwd1 = request.POST.get('password1','')
        pwd2 = request.POST.get('password2','')

        if pwd1 != pwd2:
            return render(request,'users/change_passwd.html',context={'msg':'两次密码不一致!'})
        try:
            user = UserProfile.objects.get(pk=uid)
            user.password = make_password(pwd1)
            print(user.password)
            user.save()
            # return HttpResponseRedirect(reverse('users:index'))
            return render(request,'users/change_passwd.html',context={'msg': '密码修改成功!'})
        except Exception as e:
            print(e)
            return render(request,'users/change_passwd.html',context={'msg': '密码修改失败!'})
