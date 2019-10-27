# # _*_ encoding:utf-8 _*_
# from jenkinsapi.jenkins import Jenkins
# from jenkinsapi.build import Build
#
# from cmdb.settings import Jenkins_Url,Jenkins_User,Jenkins_Password
#
# def get_server_instance():
#     jenkins_url = Jenkins_Url
#     server = Jenkins(jenkins_url, username=Jenkins_User, password=Jenkins_Password)
#     return server
#
# #执行构建
# def build_job(name,params):
#     server = get_server_instance()
#     server.build_job(name,params)
#     return None
#
# #得到一个已知url的构建状态或结果
# def get_build_result(name,url,number):
#     server = get_server_instance()
#     job = server.get_job(name)
#     try:
#         obj = Build(url, number, job)
#         console = obj.get_console()
#         if obj.is_running():
#             return console,False,'构建中'
#         elif obj.is_good():
#             return console,True,'构建成功'
#         else:
#             return console,False,'构建失败'
#     except:
#         return '准备构建中，耐心等待',False,'准备构建中，耐心等待'
#
# #计算下一次构建序号，在最后一次基础上+1
# def get_build_url_number(name):
#     server = get_server_instance()
#     job = server.get_job(name)
#     url = job.__dict__['_data']['lastBuild']['url']
#     number = job.__dict__['_data']['lastBuild']['number']
#     new_number = int(number) +1
#     new_url_list = url.split('/')
#     new_url_list[-2] = str(new_number)
#     new_url = '/'.join(new_url_list)
#     return new_url,new_number
#
#
#
# #检测构建序号是否在构建或已构建
# def check_job(name,number):
#     server = get_server_instance()
#     job = server.get_job(name)
#     try:
#         build_number = int(job.__dict__['_data']['executable']['number'])
#     except:
#         build_number = int(job.__dict__['_data']['lastBuild']['number'])
#     if build_number >= number:
#         #已存在，不用再构建
#         return False
#     else:
#         #不存在，可以构建
#         return True
#