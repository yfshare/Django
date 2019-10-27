# _*_ encoding:utf-8 _*_
__author__ = 'sunzhaohui'
__date__ = '2019-08-25 17:01'

from django import forms
from .models import Deploy


class ApplyForm(forms.ModelForm):
    class Meta:
        model = Deploy
        # fields= "__all__"
        fields = ['name', 'version', 'version_desc', 'update_detail']


class DeployForm(forms.ModelForm):
    class Meta:
        model = Deploy
        #fields = ['name', 'version', 'version_desc', 'update_detail']
        fields = []