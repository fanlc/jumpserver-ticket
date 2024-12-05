import json
import time


# {'assets': ['44437214-26a7-4f8f-8f41-0b92f7409f4f'], 'nodes': [], 'accounts': ['@SPEC', 'root'], 'protocols': ['all'], 'actions': ['connect', 'upload', 'download', 'copy', 'paste', 'delete', 'share'], 'is_active': 'true', 'name': 'admin-superuser', 'users': ['083d6d95-c035-4362-a1b4-df946ff55d9c'], 'comment': 'Administrator-超级用户'}

# 序列化数据到文件
def serialize_perm(mes_format_dict):
    # print(type(mes_format_dict), mes_format_dict)
    time_second = str(time.time())
    file_name_ago = mes_format_dict['name']
    file_name = file_name_ago + '.' + time_second + '.json'
    file_name_path = 'perms/utils/nowapplication/%s' % file_name
    # file_name_path = '%s' % file_name
    mes_format_dict['file_name'] = file_name
    mes_format_dict['is_done'] = 'false'
    pname = mes_format_dict['comment'].split("-")[0]
    mes_format_dict['pname'] = pname
    try:
        with open(file_name_path, 'w') as file:
            json.dump(mes_format_dict, file)
        res = {
            "code": 20000,
            'type': 'success',
            'mes': '工单创建成功！请通知运维审批！'
        }
        return res
    except Exception as e:
        res = {
            "code": 40000,
            'type': 'error',
            'mes': e
        }
        return res

