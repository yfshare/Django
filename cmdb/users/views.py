from django.urls import reverse
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse,HttpResponseRedirect
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin

class IndexView(LoginRequiredMixin,View):
    """
    登出功能
    """
    # 用户没有通过或者权限不够时跳转的地址，默认是 settings.LOGIN_URL.
    login_url = '/login/'
    # 把没通过检查的用户重定向到没有 "next page" 的非登录页面时，把它设置为 None ，这样它会在 URL 中移除。
    redirect_field_name = 'redirect_to'   # http://123.56.73.115:8000/login/?redirect_to=/

    def get(self, request):
        return render(request, 'index.html')

class LoginView(View):
    """
    登录模块
    """
    def get(self, request):
        return render(request, "login.html")

    def post(self, request):
        username = request.POST.get("username", None)
        password = request.POST.get("password", None)
        print(username)
        user = authenticate(username=username, password=password)
        print(user)
        if user:
            if user.is_active:
                # 默认为当前登录用户创建session
                login(request, user)
                # 登录成功则跳到首页
                # return HttpResponseRedirect('/')
                # 命名空间的写法
                # return HttpResponseRedirect('/userlist')
                return HttpResponseRedirect(reverse("users:index"))
            else:
                return render(request, "login.html", {"msg": "用户未激活！"})
        else:
            return render(request, "login.html", {"msg": "用户名或密码错误！"})

class LogoutView(View):
    def get(self,request):
        logout(request)
        return HttpResponseRedirect(reverse("users:login"))