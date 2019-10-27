from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser

class UserProfile(AbstractUser):
    name_cn = models.CharField('中文名',max_length=30)
    phone = models.CharField('手机',max_length=11,null=True,blank=True)

    class Meta:
        verbose_name = '用户信息'
        verbose_name_plural = verbose_name

        def __str__(self):
            return self.username
