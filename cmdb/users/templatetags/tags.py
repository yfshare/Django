from django import template
from django import template
register = template.Library()

# Django 模版高级过滤器

@register.filter(name='group_str2')
def groups_str2(group_list):
    '''
    将角色列表转换为 str
    '''
    # print(group_list)
    if len(group_list) < 3:
        return ','.join([user.name for user in group_list])
    else:
        return '{} ...'.format(','.join([user.name for user in group_list[0:2]]))
@register.filter(name='user_groups')
def user_groups(group_list):
    return '\n'.join([user.name for user in group_list])


@register.filter(name='bool2str')
def bool2str(value):
    if value:
        return '正常'
    else:
        return '禁用'

@register.filter(name='permission_code')
def permission_code(permission_list):
    '''
    将权限列表转为 str
    '''
    # for permission in permission_list:
    #     print(permission.codename)   #django.contrib.auth.models.Permission
        #该模型在数据库中被保存为auth_permission数据表。每条权限拥有id ,name , content_type_id, codename四个字段
    pers = [permission.codename for permission in permission_list]
    if len(permission_list) < 3:
        per = ','.join(pers)
        return '{}'.format(per)
    else:
        return '{} ...'.format(','.join(pers[0:2]))

@register.filter(name='permission_all')
def permissions(permission_all):
    perAll = '\n'.join([perAlls.codename for perAlls in permission_all])
    return perAll

@register.filter(name='group_users')
def guser(group_users):
    users = [user.username for user in group_users]
    if len(group_users) < 3:
        return ','.join(users)
    else:
        user = ','.join(users[0:2])
        return '{} ...'.format(user)

@register.filter(name='group_all')
def content(group_all):
    con = '\n'.join([content.username for content in group_all])
    return con

@register.filter(name='permission_models')
def pmodel(permission_models):
    model_name = str(permission_models).split('|')[1].strip()
    return model_name
