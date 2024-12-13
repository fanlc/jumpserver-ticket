from django.http import JsonResponse
import json
import time
from perms.utils.perm_application_tools import create_authorization


def perm_application(request):
    '''
    创建授权
    Node
    admin token : ef5c1e53ece1028b3cbff47f56b5e3357a6b42e0
    '''
    if request.method == 'POST':
        get_params = request.GET.dict()
        json_b = request.body
        json_str = json_b.decode('utf-8')
        json_obj = json.loads(json_str)
        
        res = create_authorization(get_params, json_obj)

        return JsonResponse(res, safe=False)
    

def perm_application_db(request):
    '''
    创建授权
    Mysql
    admin token : ef5c1e53ece1028b3cbff47f56b5e3357a6b42e0

    params = {'pname': '范立春', 'uname': 'fanlichun', 'nameid': 'eb0a174e-25d4-445a-9d9a-f4db58f8f5a7'}

    body = 
    [
        {
            'id': '1f86e5e6-d0d9-4cc1-b45d-dsadsasad', 
            'name': '测试mysql4', 
            'address': '10.8.100.102', 
            'platform': 'MySQL', 
            'created_by': 'Administrator',
            'readonly': 'true',
            'alldb': [{'value': 'jumpserver', 'label': 'jumpserver'}, {'value': 'test1', 'label': 'test1'}, {'value': 'test2', 'label': 'test2'}, {'value': 'test3', 'label': 'test3'}, {'value': 'test4', 'label': 'test4'}], 
            'xz': ['jumpserver']
        },
        {
            'id': '1f86e5e6-d0d9-4cc1-b45d-dsadwqczxc', 
            'name': '测试mysql5', 
            'address': '10.8.100.103', 
            'platform': 'MySQL', 
            'created_by': 'Administrator', 
            'readonly': 'true',
            'alldb': [{'value': 'jumpserver', 'label': 'jumpserver'}, {'value': 'test1', 'label': 'test1'}, {'value': 'test2', 'label': 'test2'}, {'value': 'test3', 'label': 'test3'}, {'value': 'test4', 'label': 'test4'}], 
            'xz': ['jumpserver']
        },
        {
            'id': '1f86e5e6-d0d9-4cc1-b45d-fdafdas', 
            'name': '测试mysql6', 
            'address': '10.8.100.104', 
            'platform': 'MySQL', 
            'created_by': 'Administrator', 
            'readonly': 'true',
            'alldb': [{'value': 'jumpserver', 'label': 'jumpserver'}, {'value': 'test1', 'label': 'test1'}, {'value': 'test2', 'label': 'test2'}, {'value': 'test3', 'label': 'test3'}, {'value': 'test4', 'label': 'test4'}], 
            'xz': ['jumpserver']
        }
    ]
    '''

    if request.method == 'POST':
        # 参数
        get_params = request.GET.dict()
        json_b = request.body
        json_str = json_b.decode('utf-8')
        # body
        json_obj = json.loads(json_str)


        ################################
        overall_name = 'jump_db_{}_r'.format(get_params['uname'])


        # 整理数据
        mes_format_dict = {}

        mes_format_dict['name'] = overall_name
        mes_format_dict['uname'] = get_params['uname']
        mes_format_dict['pname'] = get_params['pname']
        mes_format_dict['accounts'] = "select"
        mes_format_dict['comment'] = overall_name
        mes_format_dict['is_done'] = "false"
        mes_format_dict['nameid'] = get_params['nameid']
        mes_format_dict['platform'] = "MySQL"

        # 先删除 一些无用的数据
        for node_mes in json_obj:
            del node_mes['alldb']
            del node_mes['created_by']
            del node_mes['platform']
            xzstr = ",".join(node_mes['xz'])
            node_mes['xzstr'] = xzstr

        # 整合数据
        mes_format_dict['allasset'] = json_obj


        # 简易版本的 就不用把数据放数据库了，直接序列化到文件
        time_second = str(time.time())
        file_name = overall_name + '.' + time_second + '.json'
        file_name_path = 'perms/utils/nowapplication/%s' % file_name

        mes_format_dict['file_name'] = file_name

        # 序列化数据到文件
        try:
            with open(file_name_path, 'w') as file:
                json.dump(mes_format_dict, file)
            res = {
                "code": 20000,
                'type': 'success',
                'mes': '工单创建成功！请通知运维审批！'
            }
            return JsonResponse(res, safe=False)
        except Exception as e:
            res = {
                "code": 40000,
                'type': 'error',
                'mes': e
            }
            return JsonResponse(res, safe=False)

