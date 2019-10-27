# _*_ encoding:utf-8 _*_
__author__ = 'sunzhaohui'
__date__ = '2019-08-27 16:50'

Jenkins_Url = 'http://172.33.0.82:8080'
Jenkins_User = 'admin'
Jenkins_Password = 'admin'

import jenkins



def get_server_instance():
    jenkins_url = Jenkins_Url
    server = jenkins.Jenkins(jenkins_url, username=Jenkins_User, password=Jenkins_Password)
    return server

def getSCMInfroFromLatestGoodBuild(jobname):
    server = get_server_instance()
    job = server[jobname]
    lgb = job.get_last_good_build()
    return lgb

def get_all_jobs():
    server = get_server_instance()
    return server.get_jobs_list()

def get_job_obj(job):
    url = job.__dict__['_data']['lastBuild']['url']

# def build_job(jobname):
#     server = get_server_instance()
#     ret = server.build_job(jobname)
#     print(ret)

if __name__ == '__main__':
    #print(get_server_instance().version)
    # server = get_server_instance()
    # for job_name ,job_instance in server.get_jobs():
    #     print(job_name,job_instance)
    #     print(job_instance.get_description())
    #     print(job_instance.is_running())
    #     print(job_instance.is_enabled())
    # server = get_server_instance()
    # job = server.get_job('reboot')
    # #print(job.__dict__['_data']['builds'])
    # url = job.__dict__['_data']['lastBuild']['url']
    # number = job.__dict__['_data']['lastBuild']['number']
    # obj = Build(url, number, job)
    # print(obj)
    # print(obj.is_good())
    # #print(obj.pprint())
    # print(obj.get_console())
    # #print(get_server_instance().get_build_info('reboot', 5))

    params = {'Branch': 'qa', 'host': 'node1'}
    # build_job('reboot_qa')
    server = get_server_instance()
    user = server.get_whoami()
    version = server.get_version()
    print('Hello %s from Jenkins %s' % (user['fullName'], version))

    server.build_job('reboot_qa',params)
