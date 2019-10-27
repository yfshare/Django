from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse, QueryDict
from django.urls import reverse
from django.views.generic import View, ListView, DetailView
from django.db.models import Q
from django.core.mail import send_mail
from django.contrib.auth.mixins import LoginRequiredMixin
from pure_pagination.mixins import PaginationMixin
import  datetime

# 自定义模块导入
from .models import WorkOrder
from .forms import WorkOrderApplyForm,WorkOrderResultForm
from django.conf import settings

class WorkOrderApplyView(LoginRequiredMixin, View):
    def get(self, request):
        forms = WorkOrderApplyForm()
        return render(request, 'order/workorder_apply.html', {'forms': forms})
    def post(self, request):
        # print(request.POST)
        forms = WorkOrderApplyForm(request.POST or None, request.FILES or None)
        if forms.is_valid():
            try:
                #print(forms.cleaned_data)
                title = forms.cleaned_data["title"]
                order_contents = forms.cleaned_data["order_contents"]
                #print(order_contents)
                assign_id = forms.cleaned_data["assign_id"]

                # print(assign_id)
                orderfiles = forms.cleaned_data["orderfiles"]

                data = forms.cleaned_data
                data['applicant_id'] = request.user.id
                # print(data)
                WorkOrder.objects.create(**data)
                # work_order = WorkOrder()
                # work_order.title = title
                # work_order.order_contents = order_contents
                #
                # work_order.assign_id = assign_id
                # work_order.orderfiles = orderfiles
                # work_order.applicant = request.user
                # work_order.status = 0
                # work_order.save()
                return HttpResponseRedirect(reverse('workorder:list'))
            except Exception as e:
                print(e)
                return render(request, 'order/workorder_apply.html', {'forms': forms, 'errmsg': '工单提交出错！'})
        else:
            return render(request, 'order/workorder_apply.html', {'forms': forms, 'errmsg': '工单填写格式出错！'})

class WorkOrderListView(LoginRequiredMixin, PaginationMixin, ListView):
    """
    待处理工单列表展示
    """
    model = WorkOrder
    template_name = 'order/workorder_list.html'
    context_object_name = "orderlist"
    paginate_by = 10
    keyword = ''

    def get_queryset(self):
        queryset = super(WorkOrderListView, self).get_queryset()
        # 只显示状态小于2，即申请和处理中的工单
        queryset = queryset.filter(status__lt=2)
        # 如果不是sa组的用户只显示自己申请的工单，别人看不到你申请的工单，管理员可以看到所有工单
        if 'sa' not in [group.name for group in self.request.user.groups.all()]:
            queryset = queryset.filter(applicant=self.request.user)

        self.keyword = self.request.GET.get('keyword', '').strip()
        if self.keyword:
            queryset = queryset.filter(Q(title__icontains = self.keyword)|
                                       Q(order_contents__icontains = self.keyword)|
                                       Q(result_desc__icontains=self.keyword))
        return queryset

    def get_context_data(self, **kwargs):
        context = super(WorkOrderListView, self).get_context_data(**kwargs)
        context['keyword'] = self.keyword

        return context


    def delete(self,request,**kwargs):
        #取消工单
        data = QueryDict(request.body).dict()
        id = data['id']
        #
        try:

            work_order = self.model.objects.get(id=id)
            work_order.status = 4
            work_order.complete_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            work_order.save()
            res = {'code': 0, 'result': '取消成功'}
        except:
             res = {'code': 1, 'errmsg': '取消失败'}
        return JsonResponse(res, safe=True)

class WorkOrderDetailView(LoginRequiredMixin, DetailView):
    """
    工单详情页，包括处理结果表单的填写
    """
    model = WorkOrder
    template_name = "order/workorder_detail.html"
    context_object_name = "workorder"

    def post(self, request, **kwargs):
        pk = kwargs.get("pk")
        work_order = self.model.objects.get(pk=pk)

        #接单
        if work_order.status == 0:
            work_order.status = 1
            work_order.handler = request.user
            work_order.handle_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            work_order.save()
            return HttpResponseRedirect(reverse("workorder:list"))
        #回复
        if work_order.status == 1:
            forms = WorkOrderResultForm(request.POST)
            if forms.is_valid():
                result_desc = request.POST.get('result_desc', '')
                work_order.result_desc = result_desc
                work_order.status = 2
                work_order.complete_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                work_order.save()
                return HttpResponseRedirect(reverse('workorder:list'))
            else:
                return render(request, 'order/workorder_detail.html', {'work_order': work_order, 'errmsg': '必须填写处理结果！'})

class WorkOrderHistoryView(LoginRequiredMixin, PaginationMixin, ListView):
    """
    待处理工单列表展示
    """
    model = WorkOrder
    template_name = 'order/workorder_history.html'
    context_object_name = "orderlist"
    paginate_by = 10
    keyword = ''

    def get_queryset(self):
        queryset = super(WorkOrderHistoryView, self).get_queryset()
        # 只显示状态等于2，即已完成的工单
        queryset = queryset.filter(status__gte=2)
        # 如果不是sa组的用户只显示自己申请的工单，别人看不到你申请的工单，管理员可以看到所有工单
        if 'sa' not in [group.name for group in self.request.user.groups.all()]:
            queryset = queryset.filter(applicant=self.request.user)

        self.keyword = self.request.GET.get('keyword', '').strip()
        if self.keyword:
            queryset = queryset.filter(Q(title__icontains = self.keyword)|
                                       Q(order_contents__icontains = self.keyword)|
                                       Q(result_desc__icontains=self.keyword))
        return queryset
    def get_context_data(self, **kwargs):
        context = super(WorkOrderHistoryView, self).get_context_data(**kwargs)
        context['keyword'] = self.keyword
        for order in context['orderlist']:
            print(order.get_status_display)

        return context