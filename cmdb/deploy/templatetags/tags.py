# _*_ encoding:utf-8 _*_
__author__ = 'sunzhaohui'
__date__ = '2019-08-11 15:49'

from django import template
register = template.Library()


@register.filter(name='group_str2')
def groups_str2(group_list):
    """
    将角色列表转换为str
    """
    if len(group_list) < 3:
        return ' '.join([user.name for user in group_list])
    else:
        return '%s ...' % ' '.join([user.name for user in group_list[0:2]])


@register.filter(name='bool2str')
def bool2str(value):
    if value:
        return u'是'
    else:
        return u'否'

@register.filter(name='bool2str')
def bool2str(value):
    if value:
        return u'是'
    else:
        return u'否'

@register.filter(name='member_str')
def member_str(member_list):
    """
    将角色列表转换为str
    """
    members = []
    for member in member_list:
        members.append(str(member))
    if len(members) < 3:

        return ','.join(members)
    else:
        return '%s ...' % ' '.join(members[0:2])

@register.filter(name='all_power_str')
def all_power_str(power_list):
    powers = []
    for power in power_list:
        powers.append(power.codename)
    return ','.join(powers)

@register.filter(name='power_str')
def power_str(permissions):
    """
    将角色列表转换为str
    """
    permissions_list = []
    for permission in permissions:

        permissions_list.append(str(permission).split('|')[-1])
    if len(permissions_list) < 3:

        return ','.join(permissions_list)
    else:
        return '%s ...' % ' '.join(permissions_list[0:2])


@register.filter(name='userlist_str2')
def userlist_str2(user_list):
    """
    将用户列表转换为str
    """
    if len(user_list) < 3:
        return ' '.join([user.name_cn for user in user_list])
    else:
        return '%s ...' % ' '.join([user.name_cn for user in user_list[0:2]])



@register.filter(name='perm_str2')
def perm_str2(perm_list):
    """
    将用户或者租的权限列表转换为str
    """
    if len(perm_list) < 3:
        return ' '.join([perm.codename for perm in perm_list])
    else:
        return '%s ...' % ' '.join([perm.codename for perm in perm_list[0:2]])