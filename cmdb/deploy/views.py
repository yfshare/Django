from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views.generic import View, TemplateView, ListView, DetailView
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin

# 分页
from pure_pagination import Paginator, PageNotAnInteger
from pure_pagination.mixins import PaginationMixin

#导入gitlab api
from utils.gitlab_api import get_user_projects, get_project_versions

# 自定义模块
from deploy.forms import ApplyForm, DeployForm
from deploy.models import Deploy
from users.models import UserProfile

import json, logging, traceback
logger = logging.getLogger("reboot")

class ApplyView(LoginRequiredMixin, TemplateView):
    """
    申请发布
    """
    template_name = 'deploy/apply.html'

    def get_context_data(self, **kwargs):
        context = super(ApplyView, self).get_context_data(**kwargs)
        context['user_projects'] = get_user_projects(self.request)
        return context

    def post(self, request):
        forms = ApplyForm(request.POST)
        print(forms)
        if forms.is_valid():
            print(request.POST)
            name = request.POST.get('name', '')
            version = request.POST.get('version', '')
            version_desc = request.POST.get('version_desc', '')
            update_detail = request.POST.get('update_detail', '')
            has_apply = Deploy.objects.filter(name=name.split('/')[1], status__lt=2)
            if has_apply:
                return render(request, 'deploy/apply.html',
                              {'errmsg': '该项目已经申请上线，但是上线还没有完成，上线完成后方可再次申请！'})
            try:
                apply_release = Deploy()
                apply_release.name = name.split('/')[1]
                apply_release.version = version
                apply_release.version_desc = version_desc
                apply_release.update_detail = update_detail
                apply_release.status = 0
                apply_release.applicant = request.user
                print(apply_release)
                apply_release.save()
                return HttpResponseRedirect(reverse('deploy:list'))
            except:
                return render(request, 'deploy/apply.html', {'errmsg': '申请失败，请查看日志'})
        else:
            return render(request, 'deploy/apply.html', {'forms': forms, 'errmsg': '申请格式错误！'})

class ProjectListView(LoginRequiredMixin, View):
    """
    当前登陆用户的项目列表
    """
    def get(self, request):
        my_projects = get_user_projects(request)
        print(my_projects)
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        p = Paginator(my_projects, 10, request=request)
        projects = p.page(page)
        return render(request, 'deploy/project_list.html', {'page_obj': projects, 'p': p})

class GetProjectVersionsView(LoginRequiredMixin, View):
    """
    获取指定项目的所有版本
    """
    def get(self, request):
        project_id = request.GET.get('project_id', '').split('/')[0]
        print(project_id)
        tags = get_project_versions(int(project_id))
        tags = [[tag.name, tag.message] for tag in tags]
        return HttpResponse(json.dumps(tags), content_type='application/json')

# 视图view
class ApplyListView(LoginRequiredMixin, PaginationMixin, ListView):
    """
    申请发布列表
    """

    model = Deploy
    template_name = "deploy/apply_list.html"
    context_object_name = "apply_list"
    paginate_by =10
    keyword = ''

    def get_queryset(self):
        queryset = super(ApplyListView, self).get_queryset()
        queryset = queryset.filter(status__lt=2)
        # 管理员能看到所有待上线列表，个人只能看到自己的
        if 'sa' not in [group.name for group in self.request.user.groups.all()]:
            queryset = queryset.filter(applicant=self.request.user)
        self.keyword = self.request.GET.get('keyword', '')
        if self.keyword:
            queryset = queryset.filter(Q(name__icontains=self.keyword) |
                                           Q(update_detail__icontains=self.keyword) |
                                           Q(version_desc__icontains=self.keyword))
        return queryset

    def get_context_data(self, **kwargs):
        context = super(ApplyListView, self).get_context_data(**kwargs)
        context['keyword'] = self.keyword
        return context

class DeployView(LoginRequiredMixin, DetailView):
    """
    通过获取当前项目状态，执行代码发布功能
    """
    model = Deploy
    template_name = 'deploy/deploy_detail.html'
    context_object_name = 'deploy'

    def post(self, request, **kwargs):
        forms = DeployForm(request.POST)
        pk = kwargs.get('pk')
        deploy = Deploy.objects.get(pk=pk)
        deploy.handler = request.user
        if forms.is_valid():
            if deploy:
                # 如果status为0,说明是申请状态，点击了仿真按钮，需要上线到仿真环境，并把status改为1
                if deploy.status == 0:
                    deploy.status = 1
                    # deploy.reviewer = request.user
                    # 通过Jenkins api 操作将制定项目的代码推送到规定的服务器上去
                    msg = "灰度发布完成"
                # 如果状态为1 ，说明已经是仿真状态，点击上线按钮，讲代码推到正式环境，同时状态改为2
                elif deploy.status == 1:
                    deploy.status = 2
                    # deploy.handler = request.user
                    # 通过Jenkins api 操作将制定项目的代码推送到规定的服务器上去
                    msg = "正式发布完成"
                else:
                    return HttpResponseRedirect(reverse('deploy:history'))
                deploy.save()
                return render(request, 'deploy/deploy_detail.html', {'deploy': deploy, 'msg': msg})
        else:
            return render(request, 'deploy/deploy_detail.html', {'errmsg': "提交格式不正确", 'forms': forms})

class DeployHistoryView(LoginRequiredMixin, PaginationMixin, ListView):
    """
    历史发布列表
    """

    model = Deploy
    template_name = "deploy/history_list.html"
    context_object_name = "apply_list"
    paginate_by =10
    keyword = ''

    def get_queryset(self):
        queryset = super(DeployHistoryView, self).get_queryset()
        queryset = queryset.filter(status__gte=2)
        # 管理员能看到所有待上线列表，个人只能看到自己的
        if 'sa' not in [group.name for group in self.request.user.groups.all()]:
            queryset = queryset.filter(applicant=self.request.user)
        self.keyword = self.request.GET.get('keyword', '')
        if self.keyword:
            queryset = queryset.filter(Q(name__icontains=self.keyword) |
                                           Q(update_detail__icontains=self.keyword) |
                                           Q(version_desc__icontains=self.keyword))

        return queryset

    def get_context_data(self, **kwargs):
        context = super(DeployHistoryView, self).get_context_data(**kwargs)
        print(context)
        context['keyword'] = self.keyword
        context['request_user_groups'] = [ group.name for group in self.request.user.groups.all()]
        return context