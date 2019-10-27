from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username','name_cn','email','is_active','is_staff','is_superuser')
    search_fields = ('username','name_cn','email')
    filter_horizontal = ('user_permissions','groups',)
    list_per_page = 10

    fieldsets = (
        (None,{'fields': ('username','password')}),
        ('基本信息',{'fields': ('name_cn','email','phone')}),
        ('用户权限',{'fields': ('is_active','is_staff','is_superuser','user_permissions','groups')}),
        ('日期信息', {'fields': ('last_login', 'date_joined')}),
    )
